import sys

import click
import questionary
from hcs_core.ctxp import data_util, recent


def looks_like_id(text: str):
    example1 = "21eb79bc-f737-479f-b790-7753da55f363"
    example2 = "65064e9d96c3c37900af48cd"
    if len(text) != len(example1) and len(text) != len(example2):
        return False
    id_char_set = set("abcdef-0123456789")
    return all(char in id_char_set for char in text)


def smart_search(items: list, smart_search: str):
    ret = []
    has_exact_match = False
    n = 0
    for i in items:
        score = data_util.deep_search(i, smart_search)
        n += 1
        if score > 0:
            if score == 2:
                has_exact_match = True
            ret.append((score, n, i))

    if has_exact_match:
        ret = [(score, n, i) for score, n, i in ret if score > 1]
    ret.sort(reverse=True)
    return list(map(lambda t: t[2], ret))


def require_single(
    items,
    resource_type: str,
    id_field: str = "id",
    name_field: str = "name",
    interactive: bool = True,
    include_id: bool = True,
    search_text: str = None,
):
    with recent.of(resource_type) as r:
        if not items:
            r.unset()
            return "No item found.", 1

        if len(items) == 1:
            item = items[0]
            recent.set(resource_type, item[id_field])
            return item

        if isinstance(items, dict):
            item = items
            recent.set(resource_type, item[id_field])
            return item

        if search_text:
            items = smart_search(items, search_text)

            if len(items) == 1:
                item = items[0]
                recent.set(resource_type, item[id_field])
                return item

        current_id = recent.get(resource_type)
        current = None
        items_display = []
        for item in items:
            item_id = item[id_field]
            if include_id:
                display = item_id + "/" + item.get(name_field, f"<{name_field} field not found>")
            else:
                display = item[name_field]
            items_display.append(display)
            if item_id == current_id:
                current = display

        if interactive:
            selected_display = questionary.select("Multiple matches:", items_display, default=current, show_selected=True).ask()
            if not selected_display:
                recent.unset(resource_type)
                return "", 1

            selected_id = selected_display.split("/")[0]
            r.set(selected_id)
            for item in items:
                if item[id_field] == selected_id:
                    return item
        else:
            msg = "Multiple items found:"
            click.echo(click.style(msg, fg="yellow"), file=sys.stderr)
            for i in items:
                msg = f"  - {i[id_field]} / {i.get(name_field, '<no-name>')}"
                click.echo(click.style(msg, fg="yellow"), file=sys.stderr)
            return "", 1
