# pyratebay

Python tools for The Pirate Bay. A simple command line interface and Python API.

## Installation

### From PyPI

```bash
pip install pyratebay
```

### For Developers

```bash
git clone https://github.com/evilcult/pyratebay
cd pyratebay
pip install . 
# or for development    
pip install -e .
```

## CLI Usage

After installation, the `pyratebay` command will be available.

### Search Torrents

Search for torrents by keyword.

```bash
pyratebay search "ubuntu"
```

### View Torrent Info

Get detailed attributes for a specific torrent ID.

```bash
pyratebay info 12345
```

### Browse Hot Torrents

List top 100 recent torrents.

```bash
# Default (Movies)
pyratebay hot

# Filter by category (e.g. games, music, applications, etc.)
pyratebay hot -t games

# Limit to last 48h
pyratebay hot -l true
```

## Python Library Usage

You can also use `pyratebay` as a library in your Python projects.

```python
import pyratebay

# 1. Search
# Returns a list of Media objects
results = pyratebay.search("ubuntu")
for media in results:
    print(f"{media.title} - {media.info_hash}")

# 2. Get Info
# Returns a single Media object with details
media_details = pyratebay.info("12345")
print(media_details.desc)

# 3. Get Hot/Top 100
hot_list = pyratebay.hot(media_type="games", limit=True) # limit=True for recent 48h
```

## Disclaimer

This tool is for educational purposes only. The author is not responsible for any misuse of this tool. Please ensure you comply with your local laws and regulations regarding torrenting and copyright.

