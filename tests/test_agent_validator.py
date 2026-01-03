import pytest
import json
import os
from src.state.pipeline_state import PipelineState
from src.agents.validate_outputs import ValidatorAgent

def test_validator_agent_pass(tmp_path):
    # Setup files
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"foo": {"type": "string"}},
        "required": ["foo"]
    }
    instance = {"foo": "bar"}
    
    schema_path = tmp_path / "test_schema.json"
    instance_path = tmp_path / "test_instance.json"
    
    with open(schema_path, "w") as f:
        json.dump(schema, f)
    with open(instance_path, "w") as f:
        json.dump(instance, f)
        
    from src.models.product import ProductData
    
    # Run Agent
    state = PipelineState()
    state.product = ProductData(
        product_name="Test", concentration="10%", key_ingredients=["A"], 
        benefits=["B"], skin_type=["S"], how_to_use="Do it", 
        side_effects="None", price_inr=100
    )
    state.output_paths = {"test_key": str(instance_path)}
    state.schema_paths = {"test_key": str(schema_path)} # New strict requirement
    
    agent = ValidatorAgent() # No constructor args
    new_state = agent.run(state)
    
    assert new_state.validation_report is not None
    assert new_state.validation_report["passed"] is True
    assert len(new_state.validation_report["errors"]) == 0

def test_validator_agent_fail(tmp_path):
    # Setup files
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"foo": {"type": "string"}},
        "required": ["foo"]
    }
    instance = {"foo": 123} # Integer, should be string
    
    schema_path = tmp_path / "test_schema.json"
    instance_path = tmp_path / "test_instance.json"
    
    with open(schema_path, "w") as f:
        json.dump(schema, f)
    with open(instance_path, "w") as f:
        json.dump(instance, f)
        
    # Run Agent
    state = PipelineState()
    state.output_paths = {"test_key": str(instance_path)}
    state.schema_paths = {"test_key": str(schema_path)}
    
    agent = ValidatorAgent()
    agent = ValidatorAgent()
    
    with pytest.raises(RuntimeError) as exc:
        agent.run(state)
        
    err_msg = str(exc.value)
    assert "Schema Validation Failed" in err_msg
    assert "123 is not of type 'string'" in err_msg
