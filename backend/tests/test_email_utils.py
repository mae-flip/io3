from app.core.config import settings
from app.utils import generate_game_removed_email


def test_generate_game_removed_email() -> None:
    email_data = generate_game_removed_email(
        email_to="author@example.com",
        game_title="My Queer Game",
        removal_reason="Still listed on itch.io search.",
    )

    assert "My Queer Game" in email_data.subject
    assert "My Queer Game" in email_data.html_content
    assert "Still listed on itch.io search." in email_data.html_content
    assert "You can appeal this decision by replying to this email." in (
        email_data.html_content
    )
    assert "io3 staff" in email_data.html_content
    assert settings.PROJECT_NAME in email_data.subject
