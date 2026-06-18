from app.models import OsPlatform
from app.services.platforms import itch_platform_from_link, platform_label


def test_itch_platform_from_link_urls() -> None:
    assert (
        itch_platform_from_link("HTML5", "https://itch.io/games/html5")
        == OsPlatform.web
    )
    assert (
        itch_platform_from_link(
            "Windows", "https://itch.io/games/platform-windows"
        )
        == OsPlatform.windows
    )
    assert (
        itch_platform_from_link("Linux", "https://itch.io/games/platform-linux")
        == OsPlatform.linux
    )
    assert (
        itch_platform_from_link("macOS", "https://itch.io/games/platform-osx")
        == OsPlatform.apple
    )
    assert (
        itch_platform_from_link(
            "Android", "https://itch.io/games/platform-android"
        )
        == OsPlatform.android
    )
    assert itch_platform_from_link("iOS", "https://itch.io/games/platform-ios") is None


def test_platform_labels() -> None:
    assert platform_label(OsPlatform.apple) == "Apple"
    assert platform_label(OsPlatform.web) == "Web"
