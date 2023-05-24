import re


def dropdown_regex(options: list, selected: list, keyword=None):
    """
    Dropdown's values are searchable with regex

    Patameters:

        options: options of the dropdown
        selected: already selected values of the dropdown
        keyword: keyword to search values of the dropdown with

    Returns:

        new_options: options with the keyword which replaces the original
            values which were found by the keyword
        selected: selected values of the dropdown
        hits: amount of found values with the keyword


    """

    # initialize selected if selected is None
    if not selected:
        selected = []

    # collect unselected options of the dropdown
    unselected_options = []
    for o in options:
        if o not in selected:
            unselected_options.append(o)

    # return if any amount of values were found with the keyword
    hits = 0
    if keyword:
        # add already selected values to the new options
        new_options = [s for s in selected]

        found = False
        for o in unselected_options:
            # if value matched with the keyword, set found True and increase
            #  hits by 1
            if re.search(keyword, o):
                found = True
                hits += 1
            # if value not matched with the keyword, add to the new options
            else:
                new_options.append(o)

        # if found any amount of values, add keyword to the new options and
        #  to the selected values
        if found:
            selected.append(keyword + " (regex)")
            new_options.append(keyword + " (regex)")
        return new_options, selected or None, hits

    sub_selected = []

    # add every value of the dropdown to the sub_selected
    # which is not a regex keyword
    for s in selected:
        if " (regex)" not in s:
            sub_selected.append(s)

    # update options, sub_selected and hits,
    # if any regex keywords are selected
    for s in selected:
        if " (regex)" in s:
            options, sub_selected, hits = dropdown_regex(
                options, sub_selected, s[:-8]
            )
    return options, sub_selected or None, hits


def get_columns_by_regex(columns, features):
    if features is None:
        return []

    new_features = []

    for f in features:
        if " (regex)" in f:
            for c in columns:
                if re.search(f[:-8], c) and c not in new_features:
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
