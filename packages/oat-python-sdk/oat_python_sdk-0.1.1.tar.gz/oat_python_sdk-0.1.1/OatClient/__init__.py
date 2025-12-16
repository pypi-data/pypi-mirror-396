import requests

from hashlib import sha1
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
    
@dataclass
class FunctionCall:
    fn: str
    args: Dict[str, Any] = field(default_factory=dict)
    out: Optional[str] = None

    def hash(self) -> str:
        hasher = sha1()
        hasher.update(self.fn.encode('utf-8'))
        for key in sorted(self.args.keys()):
            hasher.update(key.encode('utf-8'))
            hasher.update(str(self.args[key]).encode('utf-8'))
        return hasher.hexdigest()
    
from enum import Enum
class CompilationSetting(Enum):
    INSTANT = "instant"
    ON_DEMAND = "on_demand"

# Helper functions for building filter expressions
class Filter:
    """Helper class for building filter expressions for get_nodes()"""

    @staticmethod
    def property_equals(key: str, value: Any) -> dict:
        """Filter nodes where property equals a value"""
        return {
            "type": "Comparison",
            "field": {"type": "Property", "key": key},
            "op": "Equals",
            "value": value
        }

    @staticmethod
    def property_exists(key: str) -> dict:
        """Filter nodes where property exists"""
        return {
            "type": "Comparison",
            "field": {"type": "Property", "key": key},
            "op": "Exists",
            "value": None
        }

    @staticmethod
    def property_contains(key: str, substring: str) -> dict:
        """Filter nodes where property contains a substring"""
        return {
            "type": "Comparison",
            "field": {"type": "Property", "key": key},
            "op": "Contains",
            "value": substring
        }

    @staticmethod
    def property_gt(key: str, value: float) -> dict:
        """Filter nodes where property is greater than a value"""
        return {
            "type": "Comparison",
            "field": {"type": "Property", "key": key},
            "op": "GreaterThan",
            "value": value
        }

    @staticmethod
    def property_gte(key: str, value: float) -> dict:
        """Filter nodes where property is greater than or equal to a value"""
        return {
            "type": "Comparison",
            "field": {"type": "Property", "key": key},
            "op": "GreaterThanOrEqual",
            "value": value
        }

    @staticmethod
    def property_lt(key: str, value: float) -> dict:
        """Filter nodes where property is less than a value"""
        return {
            "type": "Comparison",
            "field": {"type": "Property", "key": key},
            "op": "LessThan",
            "value": value
        }

    @staticmethod
    def property_lte(key: str, value: float) -> dict:
        """Filter nodes where property is less than or equal to a value"""
        return {
            "type": "Comparison",
            "field": {"type": "Property", "key": key},
            "op": "LessThanOrEqual",
            "value": value
        }

    @staticmethod
    def node_id_equals(node_id: str) -> dict:
        """Filter by node ID"""
        return {
            "type": "Comparison",
            "field": {"type": "NodeId"},
            "op": "Equals",
            "value": node_id
        }

    @staticmethod
    def node_id_starts_with(prefix: str) -> dict:
        """Filter nodes where ID starts with a prefix"""
        return {
            "type": "Comparison",
            "field": {"type": "NodeId"},
            "op": "StartsWith",
            "value": prefix
        }

    @staticmethod
    def and_(*expressions: dict) -> dict:
        """Combine multiple filter expressions with AND"""
        return {
            "type": "And",
            "expressions": list(expressions)
        }

    @staticmethod
    def or_(*expressions: dict) -> dict:
        """Combine multiple filter expressions with OR"""
        return {
            "type": "Or",
            "expressions": list(expressions)
        }

    @staticmethod
    def not_(expression: dict) -> dict:
        """Negate a filter expression"""
        return {
            "type": "Not",
            "expression": expression
        }

@dataclass
class OatClient:
    
    base_url: str
    compilation_setting: CompilationSetting = field(default_factory=lambda: CompilationSetting.INSTANT)

    # Buffer all function calls until compile is called
    _buffer: Dict[str, FunctionCall] = field(default_factory=dict)
    _id_map: Dict[str, str] = field(default_factory=dict)

    # Check health on initialization
    def __post_init__(self):
        if not self.health_check():
            raise RuntimeError(f"Server at '{self.base_url}' is not reachable or unhealthy")

    def health_check(self) -> bool:
        """Check if the server is reachable and healthy"""
        if not self.base_url:
            raise ValueError("No server URL configured")

        endpoint = f"{self.base_url}/health"
        try:
            response = requests.get(endpoint)
            return response.status_code // 100 == 2
        except requests.RequestException:
            return False

    def _resolve_id(self, given_id: str) -> str:
        """
            Three possible ways to assign the correct id:
            
                1. The ID is from the DB, in which case it is used directly. This means not in _id_map nor in buffer.
                2. The ID is from a previous function call, in which case it is mapped via _id_map.
                3. The ID is yet to be used, is therefore in the buffer and is wrapped in a get_result call.
        """
        if given_id in self._id_map:
            return self._id_map[given_id]
        elif given_id in self._buffer:
            return {"fn": "get_result", "args": {"id": given_id}}
        else:
            return given_id

    def _execute_fn(self, fn_call: FunctionCall) -> Any:
        """Execute a single function call to the server"""
        if not self.base_url:
            raise ValueError("No server URL configured")

        payload = {"calls": [{
            "fn": fn_call.fn,
            "args": fn_call.args
        }]}

        endpoint = f"{self.base_url}/call"
        response = requests.post(endpoint, json=payload)
        if response.status_code // 100 != 2:
            raise RuntimeError(f"Failed to execute OAT call '{fn_call.fn}': Status code: {response.status_code}, content: '{response.text}'")
        
        return response.json()[0]
    
    def _execute_fns(self, fn_calls: List[FunctionCall], outputs: List[str] = []) -> Any:
        """Execute multiple function calls to the server"""
        if not self.base_url:
            raise ValueError("No server URL configured")

        payload = {
            "calls": [
                {
                    "fn": fn_call.fn,
                    "args": fn_call.args,
                    "out": fn_call.out
                } for fn_call in fn_calls
            ],
            "outputs": outputs
        }

        endpoint = f"{self.base_url}/call"
        response = requests.post(endpoint, json=payload)
        if response.status_code // 100 != 2:
            raise RuntimeError(f"Failed to execute OAT calls: Status code: {response.status_code}, content: '{response.text}'")
        
        return response.json()
    
    def compile(self) -> None:
        """Compile the buffered function calls to the server"""
        if not self.base_url:
            raise ValueError("No server URL configured")

        if len(self._buffer) == 0:
            return
        
        # Only allow set function calls in the buffer else raise error
        if any(not call.fn.startswith("set_") for call in self._buffer.values()):
            raise RuntimeError("Only 'set_' function calls can be compiled in batch")

        payload = {
            "calls": [ {"fn": call.fn, "args": call.args, "out": call.hash()} for call in self._buffer.values() ]
        }
        buf_ids = list(self._buffer.keys())
        endpoint = f"{self.base_url}/call"
        response = requests.post(endpoint, json=payload)
        if response.status_code // 100 != 2:
            raise RuntimeError(f"Failed to compile OAT calls: Status code: {response.status_code}, content: '{response.text}'")
        
        response_data = response.json()
        self._id_map.update({buf_id: item for buf_id, item in zip(buf_ids, response_data)})
        self._buffer.clear()

    def set_property(self, id: str, property: str, value: Any) -> None:
        fn_call = FunctionCall(
            fn="set_property",
            args={
                "id": self._resolve_id(id),
                "property": property,
                "value": value
            }
        )
        self._buffer[fn_call.hash()] = fn_call
        if self.compilation_setting == CompilationSetting.INSTANT:
            self.compile()
    
    def set_primitive(self, id: str, bound: complex = complex(0, 1)) -> str:
        self._buffer[id] = FunctionCall(
            fn="set_primitive",
            args={
                "id": id,
                "bound": [int(bound.real), int(bound.imag)]
            }
        )
        if self.compilation_setting == CompilationSetting.INSTANT:
            self.compile()
        self._id_map[id] = id
        return id
    
    def set_primitives(self, ids: List[str], bound: complex = complex(0, 1)) -> List[str]:
        for id in ids:
            self._buffer[id] = FunctionCall(
                fn="set_primitives",
                args={
                    "ids": ids,
                    "bound": [int(bound.real), int(bound.imag)]
                }
            )
        if self.compilation_setting == CompilationSetting.INSTANT:
            self.compile()
        self._id_map.update({id: id for id in ids})
        return ids
    
    def set_gelineq(self, coefficients: Dict[str, int], bias: int) -> str:
        fn_data = FunctionCall(
            fn="set_gelineq",
            args={
                "coefficients": [
                    {"id": self._resolve_id(k), "coefficient": v}
                    for k, v in coefficients.items()
                ],
                "bias": bias
            },
        )
        fn_hash = fn_data.hash()
        fn_data.out = fn_hash
        self._buffer[fn_hash] = fn_data

        if self.compilation_setting == CompilationSetting.INSTANT:
            self.compile()
            return self._id_map[fn_hash]

        return fn_hash
    
    def set_atleast(self, references: List[str], value: int) -> str:
        return self.set_gelineq(
            coefficients={r: 1 for r in references},
            bias=-value
        )
    
    def set_atmost(self, references: List[str], value: int) -> str:
        return self.set_gelineq(
            coefficients={r: -1 for r in references},
            bias=value
        )
    
    def set_equal(self, references: List[str], value: Union[int, str]) -> str:
        if isinstance(value, int):
            return self.set_and([
                self.set_atleast(references, value),
                self.set_atmost(references, value)
            ])
        else:
            return self.set_and([
                self.set_gelineq(
                    coefficients={value: -1, **{r: 1 for r in references}},
                    bias=0
                ),
                self.set_gelineq(
                    coefficients={value: 1, **{r: -1 for r in references}},
                    bias=0
                ),
            ])

    def set_and(self, references: List[str]) -> str:
        return self.set_gelineq(
            coefficients={r: 1 for r in references},
            bias=-len(references)
        )
    
    def set_or(self, references: List[str]) -> str:
        return self.set_gelineq(
            coefficients={r: 1 for r in references},
            bias=-1
        )
    
    def set_xor(self, references: List[str]) -> str:
        return self.set_and([
            self.set_or(references),
            self.set_atmost(references, 1)
        ])

    def set_not(self, references: List[str]) -> str:
        return self.set_gelineq(
            coefficients={r: -1 for r in references},
            bias=0
        )

    def set_imply(self, lhs: str, rhs: str) -> str:
        return self.set_or([
            self.set_gelineq(
                coefficients={lhs: -1},
                bias=0
            ),
            rhs
        ])
    
    def set_equiv(self, lhs: str, rhs: str) -> str:
        return self.set_or([
            self.set_gelineq({lhs: -1, rhs: -1}, bias=0),
            self.set_and([rhs, lhs])
        ])
    
    def get_node_ids(self, filter: Optional[dict] = None) -> List[dict]:
        """
        Get node IDs from the database with optional filtering.

        Args:
            filter: Optional filter expression as a dict. You can build filters manually
                or use the Filter helper class for convenience.

                Available comparison operators: "Equals", "NotEquals", "GreaterThan", "GreaterThanOrEqual",
                "LessThan", "LessThanOrEqual", "Contains", "StartsWith", "EndsWith", "Exists"

                Field selectors:
                - Property: {"type": "Property", "key": "property_name"}
                - NodeId: {"type": "NodeId"}

            topo_sorted: If True, return nodes in topological order

        Returns:
            List of node IDs matching the filter.

        Examples:
            # Get all nodes
            nodes = client.get_node_ids()

            # Using Filter helper class (recommended):
            from PLDAGClient import Filter

            # Get nodes with a specific property value
            nodes = client.get_node_ids(filter=Filter.property_equals("color", "red"))

            # Get nodes where property exists
            nodes = client.get_node_ids(filter=Filter.property_exists("status"))

            # Combine filters with AND
            nodes = client.get_node_ids(filter=Filter.and_(
                Filter.property_equals("category", "A"),
                Filter.property_gt("priority", 5)
            ))

            # Filter by node ID prefix
            nodes = client.get_node_ids(filter=Filter.node_id_starts_with("task_"))

            # Complex filter with OR and NOT
            nodes = client.get_node_ids(filter=Filter.or_(
                Filter.property_equals("status", "active"),
                Filter.not_(Filter.property_exists("archived"))
            ))

            # Manual dict format (also supported):
            nodes = client.get_node_ids(filter={
                "type": "Comparison",
                "field": {"type": "Property", "key": "color"},
                "op": "Equals",
                "value": "red"
            })
        """
        fn_data = FunctionCall(
            fn="get_node_ids",
            args={"filter": filter} if filter else {}
        )
        result = self._execute_fn(fn_data)
        return result
    
    def get_properties(self, id: str) -> Dict[str, Any]:
        fn_data = FunctionCall(
            fn="get_properties",
            args={
                "id": self._resolve_id(id)
            }
        )
        result = self._execute_fn(fn_data)
        return result['result'][0]
    
    def get_many_properties(self, ids: List[str]) -> Dict[str, Dict[str, Any]]:
        fn_data = FunctionCall(
            fn="get_many_properties",
            args={
                "ids": [self._resolve_id(id) for id in ids]
            }
        )
        return self._execute_fn(fn_data)
    
    def solve(self, roots: List[str], objectives: List[Dict[str, int]], assume: Dict[str, complex] = {}, maximize: bool = True) -> List[dict]:
        result = self._execute_fns([
            FunctionCall(
                fn="sub",
                args={"roots": [self._resolve_id(r) for r in roots]},
                out="dag"
            ),
            FunctionCall(
                fn="solve",
                args={
                    "dag": {
                        "fn": "get_result",
                        "args": {"id": "dag"}
                    },
                    "objectives": [
                        {self._resolve_id(k): v for k, v in objective.items()}
                        for objective in objectives
                    ],
                    "assume": [
                        {"id": self._resolve_id(k), "bound": [int(v.real), int(v.imag)]} 
                        for k, v in assume.items()
                    ],
                    "maximize": maximize
                },
                out="solutions"
            )
        ], outputs=["solutions"])
        return list(
            map(
                lambda sol: {k: complex(v[0], v[1]) for k, v in sol.items()},
                result[0]
            )
        )
    
    def propagate(self, assignments: Dict[str, complex]) -> Dict[str, complex]:
        result = self._execute_fn(
            FunctionCall(
                fn="propagate",
                args={
                    "assignments": {
                        self._resolve_id(k): [int(v.real), int(v.imag)]
                        for k, v in assignments.items()
                    }
                }
            )
        )
        return result
    
    def sub(self, roots: List[str]) -> str:
        fn_data = FunctionCall(
            fn="sub",
            args={
                "roots": [self._resolve_id(r) for r in roots]
            }
        )
        return self._execute_fn(fn_data)
    
    def delete_node(self, id: str) -> None:
        fn_data = FunctionCall(
            fn="delete_node",
            args={
                "id": self._resolve_id(id)
            }
        )
        self._execute_fn(fn_data)