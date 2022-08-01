def get_row(points):
    row = None
    for p in points:
        if p:
            row = p["points"][0]["customdata"][0]["index"]

    return row
