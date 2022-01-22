from enum import IntEnum, auto


class Mods(IntEnum):
    CHROMA = 1 << 0
    ME = 1 << 1
    NE = 1 << 2
    CINEMA = 1 << 3


class Difficulties(IntEnum):
    EASY = auto()
    NORMAL = auto()
    HARD = auto()
    EXPERT = auto()
    EXPERTPLUS = auto()


class Characteristics(IntEnum):
    STANDARD = auto()
    NOARROWS = auto()
    ONESABER = auto()
    _360DEGREE = auto()
    _90DEGREE = auto()
    LIGHTSHOW = auto()
    LAWLESS = auto()


class Status(IntEnum):
    UNRANKED = auto()
    QUALIFIED = auto()
    RANKED = auto()


def parse_beatmap_metadata(data: dict) -> dict:
    parsed = {
        "id": data["id"],
        "title": data.get("name"),
        "description": data.get("description"),
        "artist": data["metadata"]["songAuthorName"],
        "creator": data["metadata"]["levelAuthorName"],
        "status": Status.UNRANKED,
        "created_at": data["uploaded"],
        "updated_at": data["updatedAt"],
    }

    versions = []
    for version in data["versions"]:
        current_version = {
            "hash": version["hash"],
            "createdAt": version["createdAt"],
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
                "characteristic": Characteristics[
                    (
                        "_" + d
                        if (d := difficulty["characteristic"])
                        in ["360Degree", "90Degree"]
                        else d
                    ).upper()
                ],
                "difficulty": Difficulties[difficulty["difficulty"].upper()],
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

            for mod in Mods:
                if difficulty[mod.name.lower()]:
                    current_difficulty["mods"] |= mod

            difficulties.append(current_difficulty)

        current_version["difficulties"] = difficulties
        versions.append(current_version)

    parsed["versions"] = versions

    for status in ["qualified", "ranked"]:
        if data[status]:
            parsed["status"] = Status[status.upper()]

    return parsed
