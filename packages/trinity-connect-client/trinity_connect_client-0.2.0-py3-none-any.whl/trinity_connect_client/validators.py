def validate_id(i):
    if not isinstance(i, int) or i <= 0:
        raise ValueError("ID must be a positive integer")


def validate_uid(u):
    if not isinstance(u, str) or not u.strip():
        raise ValueError("UID must be a non-empty string")


def validate_command(command):
    if not isinstance(command, dict):
        raise ValueError("Command must be a dictionary")

    required_fields = {"rpc", "args", "pid", "ttl", "qos"}
    if not required_fields.issubset(command.keys()):
        missing = required_fields - command.keys()
        raise ValueError(f"Command missing required fields: {missing}")

    if not isinstance(command["rpc"], str):
        raise ValueError("Command 'rpc' must be a string")

    if not isinstance(command["args"], list):
        raise ValueError("Command 'args' must be a list")

    if not isinstance(command["pid"], (str, int)):
        raise ValueError("Command 'pid' must be a string or integer")

    if not isinstance(command["ttl"], (int, float)) or command["ttl"] < 0:
        raise ValueError("Command 'ttl' must be a non-negative number")

    if not isinstance(command["qos"], int) or command["qos"] < 0:
        raise ValueError("Command 'qos' must be a non-negative integer")
