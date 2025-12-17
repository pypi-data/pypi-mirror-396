from dataclasses import dataclass

@dataclass
class Media:
    mid      : str
    title    : str
    desc     : str | None = None
    size     : int | None = None
    seeders  : int | None = None
    leechers : int | None = None
    uploader : str | None = None
    time     : int | None = None
    info_hash: str | None = None