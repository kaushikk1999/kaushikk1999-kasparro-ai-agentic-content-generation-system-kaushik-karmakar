from typing import List, Dict, Any, Set
from dataclasses import dataclass, field
from src.state.pipeline_state import PipelineState

@dataclass
class NodeSpec:
    node_id: str
    agent: Any  # Must have .run(state)
    depends_on: List[str] = field(default_factory=list)

class DagRunner:
    def __init__(self):
        self._nodes: Dict[str, NodeSpec] = {}

    def register(self, node: NodeSpec):
        if node.node_id in self._nodes:
            raise ValueError(f"Node {node.node_id} already registered.")
        self._nodes[node.node_id] = node

    def _topological_sort(self) -> List[str]:
        # Kahn's algorithm
        in_degree = {u: 0 for u in self._nodes}
        adj = {u: [] for u in self._nodes}
        
        for u, node in self._nodes.items():
            for v in node.depends_on:
                if v not in self._nodes:
                     raise ValueError(f"Dependency {v} not found for node {u}")
                adj[v].append(u)
                in_degree[u] += 1
        
        queue = [u for u in self._nodes if in_degree[u] == 0]
        result = []
        
        while queue:
            u = queue.pop(0)
            result.append(u)
            
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
                    
        if len(result) != len(self._nodes):
            raise ValueError("Cycle detected in DAG or unresolved dependencies")
            
        return result

    def run(self, initial_state: PipelineState) -> PipelineState:
        execution_order = self._topological_sort()
        state = initial_state
        print(f"DAG Execution Order: {execution_order}")
        
        for node_id in execution_order:
            node = self._nodes[node_id]
            print(f"Running node: {node_id}")
            state = node.agent.run(state)
            
        return state
