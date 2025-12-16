import json
from pathlib import Path

import jsonschema
import yaml


def validate_spec(spec_data: dict, schema: dict):
    jsonschema.validate(instance=spec_data, schema=schema)


def load_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"File '{path}' not found")

    with open(path, "r") as f:
        if path.suffix == ".json":
            return json.load(f)
        elif path.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(f)

        raise NotImplementedError(f"File extension '{path.suffix}' not supported")
