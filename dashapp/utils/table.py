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


def get_updated_item(items, index, inputs_list):
    """
    Return the of the item that has been updated among all items except a new item entry

    Parameters:
        items: list of items (Input ALL gets list of all items that has same id type)
        index: index of the item that has been updated
        inputs_list: list of all inputs of the callback

    Returns:
        item: item that has been updated
    """
    # Ignore a new item
    if items[-1] is None:
        items = items[:-1]

    # Convert all None values to an empty list
    for id, item in enumerate(items):
        if item is None:
            items[id] = []

    # Get the updated item
    for id, item in enumerate(inputs_list):
        if item["id"]["index"] == index:
            item = items[id]
            break

    return item
