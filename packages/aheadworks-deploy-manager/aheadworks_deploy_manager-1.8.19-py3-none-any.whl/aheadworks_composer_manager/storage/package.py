import json
import os

def load_composer_file(full_module_name: str, module_path: str) -> dict:
    path_to_composer = f"{module_path}/composer.json"
    if not os.path.isfile(path_to_composer):
        os.system(f"ls {module_path}")
        raise Exception(f"Can not build module {full_module_name}: composer.json is missing")

    with open(path_to_composer) as f:
        return json.load(f)

def save_composer_file(module_path: str, composer_data: dict):
    with open(f"{module_path}/composer.json", 'w') as f:
        json.dump(composer_data, f, indent=4)
