import re


def dropdown_multi_selection(options, selected, keyword):
    if not selected:
        selected = []
    prog = re.compile(keyword, re.I)
    for option in options:
        if option not in selected and prog.search(option):
            selected.append(option)
    return selected
