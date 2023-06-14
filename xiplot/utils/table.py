def get_sort_by(sort_by, selected_rows, trigger):
    all_selected = all(selected_rows) or not any(selected_rows)
    if len(sort_by) == 0 and all_selected:
        sort_by = []

    elif len(sort_by) == 0 and not all_selected:
        sort_by = [
            {"column_id": "Selection", "direction": "desc"},
            {"column_id": "index_copy", "direction": "asc"},
        ]

    elif len(sort_by) != 0 and True not in selected_rows:
        pass

    elif sort_by[0]["column_id"] != "Selection":
        sort_by.insert(0, {"column_id": "Selection", "direction": "desc"})

    elif (
        trigger != "auxiliary_store"
        and {"column_id": "index_copy", "direction": "asc"} in sort_by
    ):
        sort_by.remove({"column_id": "index_copy", "direction": "asc"})
        sort_by.append({"column_id": "index_copy", "direction": "asc"})

    elif (
        all_selected
        and {"column_id": "index_copy", "direction": "desc"} in sort_by
    ):
        sort_by.remove({"column_id": "Selection", "direction": "desc"})
        sort_by.remove({"column_id": "index_copy", "direction": "asc"})

    elif sort_by == {"column_id": "Selection", "direction": "desc"}:
        sort_by.append({"column_id": "index_copy", "direction": "asc"})

    elif len(sort_by) == 1 and sort_by[0]["column_id"] == "Selection":
        sort_by.append({"column_id": "index_copy", "direction": "asc"})

    return sort_by


def get_updated_item(items, index, inputs_list):
    """
    Return the of the item that has been updated among all items except a new
    item entry

    Parameters:
        items: list of items (Input ALL gets list of all items that has same
            id type)
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
    item_id = get_updated_item_id(items, index, inputs_list)
    item = items[item_id]

    return item


def get_updated_item_id(items, index, inputs_list):
    for id, item in enumerate(inputs_list):
        if item["id"]["index"] == index:
            return id
