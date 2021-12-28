def simple_name(name):
    return "".join(name.split("_")[-1])


def replace_os_separator(path):
    return path.replace("\\", "_").replace("/", "_")
