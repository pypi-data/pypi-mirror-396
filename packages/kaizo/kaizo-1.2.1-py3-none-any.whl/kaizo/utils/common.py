import re


def extract_variable(entry: str) -> tuple[str | None, str]:
    matched = re.match(r"^(\w*)\.\{(\w+)\}$", entry)
    if matched is None:
        return None, entry

    return matched.groups()
