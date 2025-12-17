def map_command(canonical, os_type):
    parts = canonical.split()
    action = parts[0]
    args = {}

    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=")
            args[k] = v

    if os_type == "linux":
        return linux_map(action, args)
    else:
        return windows_map(action, args)


def linux_map(action, args):
    mapping = {
        "LIST_FILES": "ls",
        "LIST_FILES_LONG": "ls -l",
        "SHOW_HIDDEN": "ls -a",
        "PRINT_CWD": "pwd",
        "MAKE_DIR": f"mkdir {args.get('name')}",
        "DELETE_FILE": f"rm {args.get('name')}",
        "FIND_LARGE": f"find . -size +{args.get('size')}",
        "DISK_USAGE": "df -h",
        "SHOW_DATE": "date"
    }
    return mapping.get(action)


def windows_map(action, args):
    mapping = {
        "LIST_FILES": "dir",
        "LIST_FILES_LONG": "dir",
        "SHOW_HIDDEN": "dir /a",
        "PRINT_CWD": "cd",
        "MAKE_DIR": f"mkdir {args.get('name')}",
        "DELETE_FILE": f"del {args.get('name')}",
        "FIND_LARGE": "dir /s",
        "DISK_USAGE": "wmic logicaldisk get size,freespace,caption",
        "SHOW_DATE": "date /t"
    }
    return mapping.get(action)
