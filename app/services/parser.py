from enum import IntEnum
from app.utils import JSON

class Mods(IntEnum):
    CHROMA = 1 << 0
    ME = 1 << 1
    NE = 1 << 2
    CINEMA = 1 << 3


class Status(IntEnum):
    UNRANKED = 0
    QUALIFIED = 1
    RANKED = 2


def parse_beatmap_metadata(data: JSON) -> JSON:
    parsed = {
        "id": data['id'],
        "title": data.get('name'),
        "description": data.get('description'),
        "artist": data['metadata']['songAuthorName'],
        "creator": data['metadata']['levelAuthorName'],
        "status": Status.UNRANKED,
        "createdAt": data['uploaded'],
        "updatedAt": data['updatedAt'],
    }

    versions = []
    for version in data['versions']:
        current_version = {
            "hash": version['hash'],
            "createdAt": version['createdAt'],
        }

        difficulties = []
        for difficulty in versions:
            current_difficulty = {
                "njs": difficulty['njs'],
                "offset": difficulty['offset'],
                "notes": difficulty['notes'],
                "bombs": difficulty['bombs'],
                "obstacles": difficulty['obstacles'],
                "nps": difficulty['nps'],
                "length": difficulty['length'],
                "characteristic": difficulty['characteristic'],
                "difficulty": difficulty['difficulty'],
                "events": difficulty['events'],
                "mods": 0,
                "seconds": difficulty['seconds'],
                "stars": difficulty.get('stars'),
                "paritySummary": {
                    "errors": difficulty['paritySummary']['errors'],
                    "warns": difficulty['paritySummary']['warns'],
                    "resets": difficulty['paritySummary']['resets'],
                },
            }

            for mod in ['cinema', 'chroma', 'me', 'ne']:
                if difficulty[mod]:
                    current_difficulty['mods'] |= Mods[mod.upper()]

            difficulties.append(current_difficulty)

        current_version['difficulties'] = difficulties
        versions.append(current_version)

    parsed['versions'] = versions

    for status in ['qualified', 'ranked']:
        if data[status]:
            parsed['status'] = Status[status.upper()]

    return parsed
