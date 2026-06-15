from typing import Any, Dict

from .search_params import SearchParams

# Internal-key → UI-URL-key renames. The UI URL spells `ukamended` all
# lowercase, unlike the API. Other camelCase params (startYear, pageSize)
# keep their casing in UI URLs.
_UI_KEY_RENAMES = {
    "ukAmended": "ukamended",
}


def to_ui_params(params: SearchParams) -> Dict[str, Any]:
    """Translate SearchParams to a dict suitable for emitting in UI URLs.

    Booleans are lowercased to "true"/"false"; ukAmended is renamed to
    ukamended.
    """
    out: Dict[str, Any] = {}
    for key, value in params.items():
        out_key = _UI_KEY_RENAMES.get(key, key)
        out[out_key] = _coerce(value)
    return out


def _coerce(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return [_coerce(v) for v in value]
    return value
