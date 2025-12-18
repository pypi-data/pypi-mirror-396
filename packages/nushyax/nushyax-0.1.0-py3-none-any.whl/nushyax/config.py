# nushyax/config.py

import yaml
from pathlib import Path
from typing import Dict, Any

def load_yaml(path: Path) -> Dict[str, Any]:
    if path.exists():
        return yaml.safe_load(path.read_text()) or {}
    return {}

def deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge overlay into base. overlay wins on conflicts."""
    result = base.copy()
    for key, value in overlay.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def load_config(framework: str | None) -> Dict[str, Any]:
    if not framework:
        return {}

    # Load default framework config
    defaults_path = Path(__file__).parent / "defaults" / f"{framework}.yaml"
    config = load_yaml(defaults_path)

    # Load global config (optional, per-framework)
    global_path = Path.home() / ".nushyax" / "config.yaml"
    global_config = load_yaml(global_path)
    global_framework_config = global_config.get(framework, {})

    # Load local project config
    local_config = load_yaml(Path(".nushyax.yaml"))

    # Deep merge: defaults ← global ← local (local wins)
    config = deep_merge(config, global_framework_config)
    config = deep_merge(config, local_config)

    # Apply overrides to commands
    overrides = config.get("overrides", {})
    commands = config.get("commands", {})
    for cmd_name, new_exec in overrides.items():
        if cmd_name in commands:
            commands[cmd_name]["exec"] = new_exec
        else:
            # Allow defining new commands via overrides
            commands[cmd_name] = {"exec": new_exec, "desc": "(overridden command)"}

    # Ensure aliases and commands are present
    config.setdefault("aliases", {})
    config.setdefault("commands", {})

    return config