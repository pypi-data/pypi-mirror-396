from nicegui import ui


def fullpage() -> ui.column:
    """
    Returns a column with 100% width and 100% height.

    NB: This sets the global view padding to 0 in order to work
    properly. You should use only once per page. Use `fcolumn()`
    or `frow()` if you just want a full column or row.
    """
    ui.query(".nicegui-content").classes("p-0")
    return ui.column().classes("p-0 w-full h-[100vh] gap-0")


def fcolumn() -> ui.column:
    """
    Returns a column with full width and full height.
    """
    return ui.column().classes("w-full h-full")


def frow() -> ui.row:
    """
    Returns a row with full width and full height.
    """
    return ui.row().classes("w-full h-full")
