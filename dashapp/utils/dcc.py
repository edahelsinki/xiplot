import re


def dropdown_regex(options: list, selected: list, keyword=None):
    if not selected:
        selected = []
    unselected_options = []
    for o in options:
        if o not in selected:
            unselected_options.append(o)
    if keyword:
        new_options = [s for s in selected]
        found = False
        for o in unselected_options:
            if re.search(keyword, o):
                found = True
            else:
                new_options.append(o)
        if found:
            selected.append(keyword + " (regex)")
            new_options.append(keyword + " (regex)")
        return new_options, selected
    sub_selected = []
    for s in selected:
        if " (regex)" not in s:
            sub_selected.append(s)
    for s in selected:
        if " (regex)" in s:
            options, sub_selected = dropdown_regex(options, sub_selected, s[:-8])
    return options, sub_selected
