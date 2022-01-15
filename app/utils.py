from typing import Any

JSON = dict[str, Any]

def beatsaver2db(resp: JSON) -> JSON:
    del resp[""]