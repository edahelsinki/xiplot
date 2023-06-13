import re
from typing import List, Optional, Tuple


def dropdown_regex(
    options: List[str], selected: List[str], new_regex: Optional[str] = None
) -> Tuple[List[str], List[str], int]:
    """Dropdown options with regex.

    Args:
        options: List of dropdown options.
        selected: List of dropdown selection.
        new_regex: Regex to add to the selection. Defaults to None.

    Returns:
        new_options: New list of options (reduced by regexes).
        new_selected: New list of selection (including the new regex).
        hits: number of hits for the new regex or zero.
    """
    if selected is None:
        selected = []
    hits = False
    # Add optional new regex
    if new_regex:
        new_regex = new_regex + " (regex)"
        if new_regex not in selected:
            selected = selected + [new_regex]
            hits = True
    # Remove selected from options
    options = [o for o in options if o not in selected]
    old_len = len(options)
    # Remove regex matches from options
    for s in selected:
        if s.endswith(" (regex)"):
            old_len = len(options)
            regex = re.compile(s[:-8])
            options = [o for o in options if not regex.search(o)]
    # Return new_options, new_selected, hits for the new regex
    return selected + options, selected, old_len - len(options) if hits else 0


def get_columns_by_regex(columns, features):
    if features is None:
        return []

    new_features = []

    for f in features:
        if " (regex)" in f:
            regex = re.compile(f[:-8])
            for c in columns:
                if regex.search(c) and c not in new_features:
                    new_features.append(c)
        elif f not in new_features:
            new_features.append(f)
    return new_features


if __name__ == "__main__":
    print(
        dropdown_regex(
            [
                "PCA 1",
                "PCA 2",
                "mpg",
                "cylinders",
                "displacement",
                "horsepower",
                "weight",
                "acceleration",
                "model-year",
                "origin",
            ],
            ["mpg", "weight", "P.* (regex)"],
        )
    )
