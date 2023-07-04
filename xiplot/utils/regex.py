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
    is_regex = re.compile(r" \(regex(()|(: \d+))\)$")
    select_results = []
    for s in selected:
        reg = is_regex.search(s)
        if reg:
            s = s[: reg.start()]
            regex = re.compile(s)
            old_len = len(options)
            options = [o for o in options if not regex.search(o)]
            s = f"{s} (regex: {old_len - len(options)})"
        select_results.append(s)
    # Return new_options, new_selected, hits for the new regex
    return (
        select_results + options,
        select_results,
        old_len - len(options) if hits else 0,
    )


def get_columns_by_regex(columns, features):
    if features is None:
        return []

    new_features = []

    is_regex = re.compile(r" \(regex(()|(: \d+))\)$")
    for f in features:
        reg = is_regex.search(f)
        if reg:
            regex = re.compile(f[: reg.start()])
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
