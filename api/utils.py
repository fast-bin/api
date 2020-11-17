import toml

def get_config():
    with open("config.toml") as f:
        return toml.load(f)


def match_format(data, format):
    for k, v in data.items():
        if k not in format:
            return False
        if not isinstance(v, format[k]):
            return False
    return True
