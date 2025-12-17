import requests
import json
import time
from urllib import parse
from pyratebay.config import FAKE_HEADERS, API_URL, SEARCH_URL, INFO_URL, HOT_URL, MEDIA_TYP
from pyratebay.models import Media

def media_search(query: str, media_type: str) -> list:
    media_list: list[Media] = []
    search_key: str = parse.quote(query)
    typ: str = MEDIA_TYP.get(media_type) if media_type in MEDIA_TYP else "0"
    url: str = API_URL + SEARCH_URL.format(query=search_key, typ=typ)

    try:
        response: requests.Response = requests.get(url, headers=FAKE_HEADERS)
        data: list = json.loads(response.text)
    except Exception:
        time.sleep(3)
        response: requests.Response = requests.get(url, headers=FAKE_HEADERS)
        data: list = json.loads(response.text)

    for x in data:
        media = Media(
            mid       = x["id"],
            title     = x["name"],
            size      = int(x["size"]) if "size" in x else None,
            seeders   = int(x["seeders"]) if "seeders" in x else None,
            leechers  = int(x["leechers"]) if "leechers" in x else None,
            uploader  = x["username"] if "username" in x else None,
            time      = int(x["added"]) if "added" in x else None,
            info_hash = x["info_hash"] if "info_hash" in x else None,
        )
        media_list.append(media)

    return media_list

def media_info(mid: str) -> Media:
    url: str = API_URL + INFO_URL.format(tid=mid)

    try:
        response: requests.Response = requests.get(url, headers=FAKE_HEADERS)
        data: dict = json.loads(response.text)
    except Exception:
        time.sleep(3)
        response: requests.Response = requests.get(url, headers=FAKE_HEADERS)
        data: dict = json.loads(response.text)

    media = Media(
        mid       = data["id"],
        title     = data["name"],
        desc      = data["descr"] if "size" in data else None,
        size      = data["size"] if "size" in data else None,
        seeders   = data["seeders"] if "seeders" in data else None,
        leechers  = data["leechers"] if "leechers" in data else None,
        uploader  = data["username"] if "username" in data else None,
        time      = data["added"] if "added" in data else None,
        info_hash = data["info_hash"] if "info_hash" in data else None,
    )
    return media

def hot_media(media_type: str, limit: bool) -> list:
    media_list: list[Media] = []

    recent = "_48h" if limit else ""
    typ: str = MEDIA_TYP.get(media_type) if media_type in MEDIA_TYP else "0"
    url:str = API_URL + HOT_URL.format(typ=typ, recent=recent)

    try:
        response: requests.Response = requests.get(url, headers=FAKE_HEADERS)
        data: list = json.loads(response.text)
    except Exception:
        time.sleep(3)
        response: requests.Response = requests.get(url, headers=FAKE_HEADERS)
        data: list = json.loads(response.text)

    for x in data:
        media = Media(
            mid       = x["id"],
            title     = x["name"],
            size      = x["size"] if "size" in x else None,
            seeders   = x["seeders"] if "seeders" in x else None,
            leechers  = x["leechers"] if "leechers" in x else None,
            uploader  = x["username"] if "username" in x else None,
            time      = x["added"] if "added" in x else None,
            info_hash = x["info_hash"] if "info_hash" in x else None,
        )
        media_list.append(media)

    return media_list