from datetime import datetime as dt

MODS = {
    "CHROMA": 0,
    "ME": 1,
    "NE": 2,
    "CINEMA": 4,
}

DIFFICULTIES = {
    "EASY": 0,
    "NORMAL": 1,
    "HARD": 2,
    "EXPERT": 3,
    "EXPERTPLUS": 4,
}

CHARACTERISTICS = {
    "STANDARD": 0,
    "NOARROWS": 1,
    "ONESABER": 2,
    "360DEGREE": 3,
    "90DEGREE": 4,
    "LIGHTSHOW": 5,
    "LAWLESS": 6,
}

STATUS = {
    "UNRANKED": 0,
    "QUALIFIED": 1,
    "RANKED": 2,
}


def parse_timestamp(timestamp: str) -> dt:
    """Parse the timestamp from beatsaver API
    due to them constantly changing the format over
    the years.

    Args:
        timestamp (str): The timestamp to parse.

    Returns:
        dt: The parsed timestamp.
    """

    # NOTE: This is temporary until we find a better solution.
    dt_format = "%Y-%m-%dT%H:%M:%SZ"
    if "." in timestamp:
        dt_format = (
            "%Y-%m-%dT%H:%M:%S.%fZ" if "Z" in timestamp else "%Y-%m-%dT%H:%M:%S.%f"
        )
    else:
        dt_format = "%Y-%m-%dT%H:%M:%SZ" if "Z" in timestamp else "%Y-%m-%dT%H:%M:%S"
    return dt.strptime(timestamp, dt_format)


def parse_beatmap_metadata(data: dict) -> dict:
    """Parse the beatmap metadata from beatsaver API.

    Args:
        data (dict): The beatmap metadata to parse.

    Returns:
        dict: The parsed beatmap metadata.
    """

    parsed = {
        "id": data["id"],
        "title": data.get("name"),
        "description": data.get("description"),
        "meta": {
            "artist": data["metadata"]["songAuthorName"],
            "creator": data["metadata"]["levelAuthorName"],
            "bpm": data["metadata"]["bpm"],
            "duration": data["metadata"]["duration"],
        },
        "versions": {"difficulties": {}},
        "status": STATUS.get("UNRANKED"),
        "created_at": parse_timestamp(data["uploaded"]),
        "updated_at": parse_timestamp(data["updatedAt"]),
    }

    versions = []
    for version in data["versions"]:
        current_version = {
            "hash": version["hash"],
            "createdAt": parse_timestamp(version["createdAt"]),
        }

        difficulties = []
        for difficulty in version["diffs"]:
            current_difficulty = {
                "njs": difficulty["njs"],
                "offset": difficulty["offset"],
                "notes": difficulty["notes"],
                "bombs": difficulty["bombs"],
                "obstacles": difficulty["obstacles"],
                "nps": difficulty["nps"],
                "length": difficulty["length"],
                "characteristic": CHARACTERISTICS.get(
                    difficulty["characteristic"].upper()
                ),
                "difficulty": DIFFICULTIES.get(difficulty["difficulty"].upper()),
                "events": difficulty["events"],
                "mods": 0,
                "seconds": difficulty["seconds"],
                "stars": difficulty.get("stars"),
                "parity_summary": {
                    "errors": difficulty["paritySummary"]["errors"],
                    "warns": difficulty["paritySummary"]["warns"],
                    "resets": difficulty["paritySummary"]["resets"],
                },
            }

            for mod in MODS:
                if difficulty[mod.lower()]:
                    current_difficulty["mods"] |= MODS[mod]

            difficulties.append(current_difficulty)

        current_version["difficulties"] = difficulties
        versions.append(current_version)

    parsed["versions"] = versions

    for status in ["qualified", "ranked"]:
        if data[status]:
            parsed["status"] = STATUS.get(status.upper())

    return parsed
