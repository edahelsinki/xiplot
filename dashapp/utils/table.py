def get_sort_by(sort_by, selected_rows, trigger):

    if len(sort_by) == 0 and False not in selected_rows:
        sort_by = []

    elif len(sort_by) == 0 and False in selected_rows:
        sort_by = [
            {"column_id": "Selection", "direction": "asc"},
            {"column_id": "index_copy", "direction": "asc"},
        ]

    elif len(sort_by) != 0 and False not in selected_rows:
        pass

    elif sort_by[0]["column_id"] != "Selection":
        sort_by.insert(0, {"column_id": "Selection", "direction": "asc"})

    elif (
        trigger != "selected_rows_store"
        and {"column_id": "index_copy", "direction": "asc"} in sort_by
    ):
        sort_by.remove({"column_id": "index_copy", "direction": "asc"})
        sort_by.append({"column_id": "index_copy", "direction": "asc"})

    elif (
        False not in selected_rows
        and {"column_id": "index_copy", "direction": "asc"} in sort_by
    ):
        sort_by.remove({"column_id": "Selection", "direction": "asc"})
        sort_by.remove({"column_id": "index_copy", "direction": "asc"})

    elif sort_by == {"column_id": "Selection", "direction": "asc"}:
        sort_by.append({"column_id": "index_copy", "direction": "asc"})

    elif len(sort_by) == 1 and sort_by[0]["column_id"] == "Selection":
        sort_by.append({"column_id": "index_copy", "direction": "asc"})

    return sort_by
