PASSWORD_PAGE_HTML = """
<html><body class="view_game">
<div class="game_password_page" id="game_password_1">
<h2>A password is required to view this page</h2>
<form action="/password" method="post">
<input type="password" name="game_password" required="required"/>
</form>
</div>
</body></html>
"""

RESTRICTED_PAGE_HTML = """
<html><head><meta content="itch.io" property="og:title"/></head>
<body data-page_name="view_game">
<div class="game_not_published_error_page">
<h2>You do not have access to this page</h2>
<p>This asset pack has been restricted by the author and can not be downloaded.</p>
</div>
</body></html>
"""

PUBLIC_GAME_HTML = """
<html><head>
<meta name="itch:path" content="games/4601517"/>
<meta content="Your Name is HAWK by MaeFlip" property="og:title"/>
</head><body>
<script>init_ViewHtmlGame('#view', {});</script>
</body></html>
"""


def test_password_protected_page_is_not_publicly_viewable() -> None:
    from app.services.itch_public import is_itch_page_publicly_viewable

    assert is_itch_page_publicly_viewable(PASSWORD_PAGE_HTML) is False


def test_restricted_page_is_not_publicly_viewable() -> None:
    from app.services.itch_public import is_itch_page_publicly_viewable

    assert is_itch_page_publicly_viewable(RESTRICTED_PAGE_HTML) is False


def test_public_game_page_is_publicly_viewable() -> None:
    from app.services.itch_public import is_itch_page_publicly_viewable

    assert is_itch_page_publicly_viewable(PUBLIC_GAME_HTML) is True


def test_empty_content_is_not_publicly_viewable() -> None:
    from app.services.itch_public import is_itch_page_publicly_viewable

    assert is_itch_page_publicly_viewable("") is False
