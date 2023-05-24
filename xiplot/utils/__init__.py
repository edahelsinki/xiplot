from typing import Any, Dict, Optional

from dash import ALL, ALLSMALLER, MATCH


def generate_id(
    cls: type, index: Optional[Any] = None, subtype: Optional[str] = None
) -> Dict[str, Any]:
    """Generate id:s for (dash) objects.

    Since the type of the id is based on an actual type there is less chance
    for overloading and better refactoring resistance.
    Furthermore, using this function instead of a handcrafted dict leads to
    fewer typos.

    Args:
        cls: The type for which the id is generated, e.g., a subclass of
            `xiplot.plots.APlot`.
        index: The index of the id. Defaults to None.
        subtype: If multiple id:s are generated for the same class (e.g.
            children of a `html.Div`) then this can be used for
            differentiation. Defaults to None.

    Returns:
        An id to be used with Dash.
    """
    if cls in [MATCH, ALL, ALLSMALLER]:
        classtype = cls
    elif subtype is None:
        classtype = f"{cls.__module__}_{cls.__qualname__}".replace(".", "_")
    else:
        classtype = f"{cls.__module__}_{cls.__qualname__}_{subtype}".replace(
            ".", "_"
        )
    if index is None:
        return {"type": classtype}
    else:
        return {"type": classtype, "index": index}
