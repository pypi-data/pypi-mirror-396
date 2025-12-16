def exists(value) -> bool:
    if value is None:
        return False
    if value is False:
        return False
    if value in ([], "", {}, ()):
        return False
    if value in (0.0, 0):
        return False
    else:
        return True