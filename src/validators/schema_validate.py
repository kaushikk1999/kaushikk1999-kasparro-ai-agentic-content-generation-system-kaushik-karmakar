import json
import os
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

class SchemaValidator:
    @staticmethod
    def load_json(path: str) -> dict:
        if not os.path.exists(path):
            raise FileNotFoundError(f"JSON file not found: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def load_schema(path: str) -> dict:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Schema file not found: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        Draft202012Validator.check_schema(schema)
        return schema

    @staticmethod
    def validate(instance: dict, schema: dict):
        validator = Draft202012Validator(schema)
        validator.validate(instance) # Raises ValidationError on first error

    @staticmethod
    def validate_file(instance_path: str, schema_path: str):
        instance = SchemaValidator.load_json(instance_path)
        schema = SchemaValidator.load_schema(schema_path)
        try:
            SchemaValidator.validate(instance, schema)
        except ValidationError as e:
            raise RuntimeError(f"Schema Validation Failed for {instance_path}:\nMessage: {e.message}\nPath: {e.json_path}") from e
