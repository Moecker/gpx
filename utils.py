import simplejson

def simple_name(name):
    return "".join(name.split("_")[-1])


def replace_os_seperator(path):
    return path.replace("\\", "_").replace("/", "_")


def pickle2json(the_dict, json_file):
    simplejson.dump(the_dict, open(json_file, "w"))

