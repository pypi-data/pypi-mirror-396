from importlib.metadata import distributions

EXCLUDE = {
    "pip",
    "setuptools",
    "wheel",
    "pipreqsafe",
}
def get_packages():
    pkgs = []
    for dist in distributions():
        name = dist.metadata["Name"]
        if name.lower() in EXCLUDE:
            continue
        pkgs.append((name, dist.version))
    return sorted(pkgs, key=lambda x: x[0].lower())
