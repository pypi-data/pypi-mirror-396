from dataclasses import dataclass


@dataclass(kw_only=True)
class LinkInformation:
    href: str
    type: str
