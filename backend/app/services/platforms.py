from urllib.parse import urlparse

from app.models import OsPlatform

PLATFORM_LABELS: dict[OsPlatform, str] = {
    OsPlatform.android: "Android",
    OsPlatform.windows: "Windows",
    OsPlatform.apple: "Apple",
    OsPlatform.linux: "Linux",
    OsPlatform.web: "Web",
}

PLATFORM_DISPLAY_ORDER: list[OsPlatform] = [
    OsPlatform.web,
    OsPlatform.windows,
    OsPlatform.linux,
    OsPlatform.apple,
    OsPlatform.android,
]

INDEX_PLATFORM_FILTERS: list[OsPlatform] = [
    OsPlatform.web,
    OsPlatform.windows,
    OsPlatform.linux,
    OsPlatform.apple,
]


def platform_label(platform: OsPlatform) -> str:
    return PLATFORM_LABELS[platform]


def itch_platform_from_link(name: str, url: str) -> OsPlatform | None:
    path = urlparse(url).path.lower().rstrip("/")
    segment = path.rsplit("/", 1)[-1]

    if segment in {"html5", "platform-web"} or "html5" in path:
        return OsPlatform.web
    if segment == "platform-windows":
        return OsPlatform.windows
    if segment in {"platform-osx", "osx"}:
        return OsPlatform.apple
    if segment == "platform-linux":
        return OsPlatform.linux
    if segment == "platform-android":
        return OsPlatform.android

    normalized_name = name.strip().lower()
    if normalized_name in {"html5", "web"}:
        return OsPlatform.web
    if normalized_name == "windows":
        return OsPlatform.windows
    if normalized_name in {"macos", "osx", "mac", "apple"}:
        return OsPlatform.apple
    if normalized_name == "linux":
        return OsPlatform.linux
    if normalized_name == "android":
        return OsPlatform.android

    return None
