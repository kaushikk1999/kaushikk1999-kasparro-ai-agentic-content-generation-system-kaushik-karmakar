import pytest
from src.orchestrator.dag_runner import DagRunner, NodeSpec
from src.state.pipeline_state import PipelineState

class DummyAgent:
    def __init__(self, name):
        self.name = name
    
    def run(self, state: PipelineState) -> PipelineState:
        state.debug_log.append(self.name)
        return state

def test_dag_toposort():
    runner = DagRunner()
    # A -> B -> C
    runner.register(NodeSpec(node_id="A", agent=DummyAgent("A"), depends_on=[]))
    runner.register(NodeSpec(node_id="B", agent=DummyAgent("B"), depends_on=["A"]))
    runner.register(NodeSpec(node_id="C", agent=DummyAgent("C"), depends_on=["B"]))
    
    order = runner._topological_sort()
    assert order == ["A", "B", "C"]

def test_dag_execution_order():
    """Verifies that agents actually run in the expected order."""
    runner = DagRunner()
    state = PipelineState()
    
    runner.register(NodeSpec(node_id="A", agent=DummyAgent("A")))
    runner.register(NodeSpec(node_id="B", agent=DummyAgent("B"), depends_on=["A"]))
    runner.register(NodeSpec(node_id="C", agent=DummyAgent("C"), depends_on=["B"]))
    
    final_state = runner.run(state)
    assert final_state.debug_log == ["A", "B", "C"]

def test_dag_fork_join():
    runner = DagRunner()
    # A -> B, A -> C, B+C -> D
    runner.register(NodeSpec(node_id="A", agent=DummyAgent("A")))
    runner.register(NodeSpec(node_id="B", agent=DummyAgent("B"), depends_on=["A"]))
    runner.register(NodeSpec(node_id="C", agent=DummyAgent("C"), depends_on=["A"]))
    runner.register(NodeSpec(node_id="D", agent=DummyAgent("D"), depends_on=["B", "C"]))
    
    order = runner._topological_sort()
    assert order[0] == "A"
    assert order[-1] == "D"
    assert set(order[1:3]) == {"B", "C"}

def test_cycle_detection():
    runner = DagRunner()
    # A -> B -> A
    runner.register(NodeSpec(node_id="A", agent=DummyAgent("A"), depends_on=["B"]))
    runner.register(NodeSpec(node_id="B", agent=DummyAgent("B"), depends_on=["A"]))
    
    with pytest.raises(ValueError, match="Cycle detected"):
        runner._topological_sort()

def test_missing_dependency():
    runner = DagRunner()
    runner.register(NodeSpec(node_id="A", agent=DummyAgent("A"), depends_on=["Z"]))
    
    with pytest.raises(ValueError, match="Dependency Z not found"):
        runner._topological_sort()

# --- New strict payload availability tests ---

class KeyCheckingAgent:
    def __init__(self, check_keys: list[str], set_key: str):
        self.check_keys = check_keys
        self.set_key = set_key

    def run(self, state: PipelineState) -> PipelineState:
        # 1. Assert required keys exist (simulating "payload availability")
        # Since PipelineState is strict, we check if they are NOT None.
        for k in self.check_keys:
            if getattr(state, k) is None:
                raise RuntimeError(f"Required key '{k}' is None!")
        
        # 2. Set the output key (simulating production)
        # We need a field we can arbitrarily set? 
        # PipelineState is strict fields. We can cheat by using existing fields 
        # (faq_draft, product_page_draft etc) as our "flags".
        setattr(state, self.set_key, {"flag": True})
        return state

def test_dag_payload_availability():
    """
    Proves that nodes receive keys produced by upstream dependencies.
    A (sets faq_draft) -> B (checks faq_draft, sets product_page_draft)
    """
    runner = DagRunner()
    state = PipelineState()

    runner.register(NodeSpec(
        node_id="A",
        agent=KeyCheckingAgent(check_keys=[], set_key="faq_draft")
    ))
    runner.register(NodeSpec(
        node_id="B",
        agent=KeyCheckingAgent(check_keys=["faq_draft"], set_key="product_page_draft"),
        depends_on=["A"]
    ))

    final_state = runner.run(state)
    assert final_state.faq_draft is not None
    assert final_state.product_page_draft is not None
