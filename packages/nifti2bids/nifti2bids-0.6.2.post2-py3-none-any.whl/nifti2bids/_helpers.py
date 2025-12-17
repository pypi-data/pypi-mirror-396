"""Helper functions."""


def list_to_str(str_list: list[str]) -> None:
    """Converts a list containing strings to a string."""
    return ", ".join(["'{a}'".format(a=x) for x in str_list])
