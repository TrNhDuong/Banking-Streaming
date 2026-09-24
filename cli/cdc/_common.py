from ..env import env


def tables():
    """Parse CDC_TABLES env var into list of (schema, table) tuples."""
    out = []
    for x in env("CDC_TABLES", required=True).split(","):
        x = x.strip()
        if not x:
            continue
        if "." in x:
            schema, table = x.split(".", 1)
        else:
            schema, table = ("public", x)
        out.append((schema, table))
    return out
