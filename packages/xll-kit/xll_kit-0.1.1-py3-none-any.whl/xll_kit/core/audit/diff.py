
def diff_model(before: dict, after: dict, include=None, exclude=None):
    include = include or []
    exclude = exclude or []

    changes = {}
    for k, old in before.items():
        if k.startswith("_"):
            continue
        if include and k not in include:
            continue
        if exclude and k in exclude:
            continue

        new = after.get(k)
        if new != old:
            changes[k] = (old, new)

    return changes
