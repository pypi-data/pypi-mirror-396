API_URL    = "https://apibay.org"
SEARCH_URL = "/q.php?q={query}&cat={typ}"
INFO_URL   = "/t.php?id={tid}"
HOT_URL    = "/precompiled/data_top100{recent}_{typ}.json"
HASH_URL   = "magnet:?xt=urn:btih:{hash}&dn={title}"

MEDIA_TYP = {
    "all"  : "0",
    "movie": "207",
    "tv"   : "208",
    "music": "101",
}

FAKE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Referer"   : "https://thepiratebay.org",
}

TR_LIST = [
    'udp://tracker.opentrackr.org:1337',
    'udp://open.stealth.si:80/announce',
    'udp://tracker.torrent.eu.org:451/announce',
    'udp://tracker.bittor.pw:1337/announce',
    'udp://public.popcorn-tracker.org:6969/announce',
    'udp://tracker.dler.org:6969/announce',
    'udp://exodus.desync.com:6969',
    'udp://open.demonii.com:1337/announce',
    'udp://glotorrents.pw:6969/announce',
    'udp://tracker.coppersurfer.tk:6969',
    'udp://torrent.gresille.org:80/announce',
    'udp://p4p.arenabg.com:1337',
    'udp://tracker.internetwarriors.net:1337',
]