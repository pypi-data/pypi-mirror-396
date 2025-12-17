import subprocess
import sys
from nl2cmd.rule_engine import rule_match
from nl2cmd.infer import ml_translate
from nl2cmd.os_detect import get_os
from nl2cmd.command_mapper import map_command
from nl2cmd.safety import safe

def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = input("ask> ")

    os_type = get_os()

    canonical = rule_match(text)
    source = "rule-based"

    if canonical is None:
        canonical = ml_translate(text)
        source = "ml"

    if canonical is None:
        print("❌ Could not understand request")
        return

    command = map_command(canonical, os_type)

    if not command:
        print("❌ Unsupported command")
        return

    print(f"Detected OS: {os_type}")
    print(f"Source: {source}")
    print(f"Suggested command: {command}")

    if not safe(command):
        print("❌ Blocked for safety")
        return

    if input("Execute? [y/N]: ").lower() == "y":
        subprocess.run(command, shell=True)


if __name__ == "__main__":
    main()
