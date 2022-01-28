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


def parse_beatmap_metadata(data: dict) -> dict:
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
        "created_at": dt.strptime(data["uploaded"].split(".")[0], "%Y-%m-%dT%H:%M:%SZ"),
        "updated_at": dt.strptime(data["updatedAt"].split(".")[0], "%Y-%m-%dT%H:%M:%SZ"),
    }

    versions = []
    for version in data["versions"]:
        current_version = {
            "hash": version["hash"],
            "createdAt": dt.strptime(version["createdAt"].split(".")[0], "%Y-%m-%dT%H:%M:%SZ"),
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
