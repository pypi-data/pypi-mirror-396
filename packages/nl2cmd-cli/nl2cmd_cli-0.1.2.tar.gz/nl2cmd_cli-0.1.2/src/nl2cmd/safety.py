BLOCKED = [
    "rm -rf",
    "shutdown",
    "reboot",
    "mkfs",
    "dd ",
    ":(){:|:&};:"
]

def safe(command):
    if not command or command.strip() == "":
        return False
    for b in BLOCKED:
        if b in command:
            return False
    return True
