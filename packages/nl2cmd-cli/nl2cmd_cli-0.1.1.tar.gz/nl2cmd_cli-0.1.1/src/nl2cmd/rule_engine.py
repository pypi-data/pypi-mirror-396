import re

def rule_match(text):
    t = text.lower()

    # List files
    if any(w in t for w in ["list", "show", "display"]) and "file" in t:
        if "detail" in t or "long" in t:
            return "LIST_FILES_LONG"
        if "hidden" in t:
            return "SHOW_HIDDEN"
        return "LIST_FILES"

    # Current directory
    if any(p in t for p in ["where am i", "current directory", "working directory"]):
        return "PRINT_CWD"

    # Create folder
    m = re.search(r"(create|make).*folder\s+(\w+)", t)
    if m:
        return f"MAKE_DIR name={m.group(2)}"

    # Delete file
    m = re.search(r"(delete|remove|erase).*file\s+(\S+)", t)
    if m:
        return f"DELETE_FILE name={m.group(2)}"

    # Find large files
    m = re.search(r"larger than\s+(\d+)(mb|gb)", t)
    if m:
        size = m.group(1) + m.group(2).upper()
        return f"FIND_LARGE size={size}"

    return None
