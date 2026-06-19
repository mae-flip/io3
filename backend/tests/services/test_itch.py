from app.models import OsPlatform
from app.services.itch import parse_itch_metadata_from_html

HAWK_HTML_SNIPPET = """
<html><head>
<title>Your Name is HAWK by MaeFlip</title>
<meta content="Your Name is HAWK by MaeFlip" name="twitter:title"/>
<meta content="NSFW Queer Mecha Combat" property="og:description"/>
<meta content="https://img.itch.zone/cover.gif" property="og:image"/>
</head><body>
<table><tbody>
<tr><td>Platforms</td><td>
<a href="https://itch.io/games/html5">HTML5</a>,
<a href="https://itch.io/games/platform-windows">Windows</a>,
<a href="https://itch.io/games/platform-linux">Linux</a>
</td></tr>
<tr><td>Genre</td><td>
<a href="https://itch.io/games/genre-action">Action</a>,
<a href="https://itch.io/games/tag-fighting">Fighting</a>
</td></tr>
<tr><td>Tags</td><td>
<a href="https://itch.io/games/tag-3d">3D</a>,
<a href="https://itch.io/games/tag-adult">Adult</a>,
<a href="https://itch.io/games/tag-lgbt">LGBT</a>,
<a href="https://itch.io/games/tag-nsfw">NSFW</a>
</td></tr>
</tbody></table>
<a href="https://maeflip.itch.io" class="action_btn view_more">View all</a>
<div class="breadcrumbs"><a href="https://itch.io/games">Games</a> › <a href="https://itch.io/games/genre-action">Action</a> › <a href="https://itch.io/games/free">Free</a></div>
<script type="text/javascript">init_ViewHtmlGame('#view_html_game_4466592', {"game":{"actual_price":0,"min_price":0}});</script>
</body></html>
"""

PAID_GAME_HTML_SNIPPET = """
<html><head>
<title>A Short Hike by adamgryu</title>
<script type="application/ld+json">{"offers":{"priceCurrency":"USD","price":"7.99","@type":"Offer"},"@type":"Product","name":"A Short Hike"}</script>
</head><body>
<script type="text/javascript">init_ViewGame('#view_game_2995069', {"game":{"actual_price":799,"min_price":799}});</script>
</body></html>
"""


def test_parse_itch_author_from_page_title() -> None:
    metadata = parse_itch_metadata_from_html(
        HAWK_HTML_SNIPPET,
        url="https://maeflip.itch.io/hawk",
    )
    assert metadata.title == "Your Name is HAWK"
    assert metadata.author_name == "MaeFlip"
    assert metadata.author_url == "https://maeflip.itch.io"
    assert metadata.summary == "NSFW Queer Mecha Combat"
    assert metadata.platforms == [
        OsPlatform.web,
        OsPlatform.windows,
        OsPlatform.linux,
    ]
    assert [(tag.slug, tag.is_genre) for tag in metadata.tags] == [
        ("genre-action", True),
        ("fighting", True),
        ("3d", False),
        ("adult", False),
        ("lgbt", False),
        ("nsfw", False),
    ]
    assert metadata.price_cents == 0
    assert metadata.price_currency == "USD"


def test_parse_itch_price_from_paid_game() -> None:
    metadata = parse_itch_metadata_from_html(
        PAID_GAME_HTML_SNIPPET,
        url="https://adamgryu.itch.io/a-short-hike",
    )
    assert metadata.price_cents == 799
    assert metadata.price_currency == "USD"


def test_parse_itch_author_from_subdomain_fallback() -> None:
    metadata = parse_itch_metadata_from_html(
        "<html><head><title>Some Game</title></head></html>",
        url="https://mooncalf.itch.io/heartwood-hollow",
    )
    assert metadata.author_name == "Mooncalf"
    assert metadata.author_url == "https://mooncalf.itch.io"
