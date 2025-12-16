import os
try:
    import tomli
except ImportError:
    tomli = None

DEFAULT_RULES = {
    # --- Legacy Rules ---
    "legacy_print": {
        "mode": "warn",
        "severity": "minor",
        "message": "Python 2 'print' statement detected. Use print() function."
    },
    "legacy_raw_input": {
        "mode": "error",
        "severity": "major",
        "message": "Legacy 'raw_input' detected. Use 'input()' instead."
    },
    
    # --- Security Rules (Critical) ---
    "security_eval": {
        "mode": "error",
        "severity": "critical",
        "message": "Security Risk: usage of eval() detected. This allows arbitrary code execution."
    },
    "security_exec": {
        "mode": "error",
        "severity": "critical",
        "message": "Security Risk: usage of exec() detected. This allows dynamic code execution."
    },
    "security_os_system": {
        "mode": "error",
        "severity": "critical",
        "message": "Security Risk: usage of os.system() detected. Vulnerable to shell injection."
    },
    "security_subprocess_shell": {
        "mode": "error",
        "severity": "critical",
        "message": "Security Risk: subprocess.Popen with shell=True is vulnerable to command injection. Use shell=False with list arguments."
    },
    "security_pickle_untrusted": {
        "mode": "error",
        "severity": "critical",
        "message": "Security Risk: Unpickling data allows arbitrary code execution. Do not use pickle.load/loads on untrusted data."
    },
    
    # --- Security Rules (Major/Warning) ---
    "security_insecure_random": {
        "mode": "warn",
        "severity": "major",
        "message": "Weak Cryptography: Using 'random' module for security-sensitive value (token/key/password). Use 'secrets' module instead."
    }
}

def load_config(path="pyproject.toml"):
    """
    Loads configuration from pyproject.toml and merges it with defaults.
    """
    # Start with defaults
    config = {"rules": {k: v.copy() for k, v in DEFAULT_RULES.items()}}
    
    if not os.path.exists(path):
        return config
        
    if not tomli:
        return config

    try:
        with open(path, "rb") as f:
            toml_data = tomli.load(f)
        
        tool_config = toml_data.get("tool", {}).get("refactoring-agent", {})
        
        # 1. Load global settings (if any)
        for key, value in tool_config.items():
            if key != "rules":
                config[key] = value

        # 2. Merge user rules
        user_rules = tool_config.get("rules", {})
        for rule_id, settings in user_rules.items():
            # Normalize shorthand: rule = "off" -> rule = { mode = "off" }
            if isinstance(settings, str):
                settings = {"mode": settings}
            
            if rule_id in config["rules"]:
                config["rules"][rule_id].update(settings)
            else:
                # Custom/Unknown rule
                config["rules"][rule_id] = settings
                
    except Exception as e:
        print(f"[WARN] Failed to parse {path}: {e}")
        
    return config
