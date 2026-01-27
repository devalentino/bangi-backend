from dataclasses import dataclass


@dataclass
class Client:
    browser_family: str | None
    device_family: str | None
    os_family: str | None
    country: str | None
    is_bot: bool
    is_mobile: bool
