from unittest.mock import MagicMock, patch

import pytest

from acapela_box.base import (AcapelaBox,                                 InvalidCredentialsError,
                                LanguageNotSupportedError, NeedsUpdateError)


def test_acapela_box_init():
    """Test the __init__ method of the `AcapelaBox` class."""
    acapela = AcapelaBox()

    assert acapela.base_url == "https://acapela-box.com/AcaBox/"
    assert "Firefox" in acapela.session.headers["User-Agent"]



def test_acapela_get_index_page():
    """Test the get_index_page method of the `AcapelaBox` class."""
    acapela = AcapelaBox()
    first_load_page_moc = MagicMock()
    first_load_page_moc.text = "<p>first</p>"

    second_load_page_moc = MagicMock()
    second_load_page_moc.text = "<p>second</p>"

    with patch('requests.sessions.Session.get') as get_method:
        get_method.return_value = first_load_page_moc
        assert "first" in acapela.get_index_page()

        get_method.return_value = second_load_page_moc
        assert "first" in acapela.get_index_page()
        assert "second" in acapela.get_index_page(True)

def test_acapela_login():
    """Test the login method of the `AcapelaBox` class."""
    acapela = AcapelaBox()
    invalid_credentials_mock = MagicMock()
    invalid_credentials_mock.text = "<root><status>0</status></root>"

    needs_update_credentials_mock = MagicMock()

    # Here, do not set the status. It would mean that the
    # AcapelaBox class needs some update!
    needs_update_credentials_mock.text = '{"status":"error"}'

    success_mock = MagicMock()
    success_mock.text = (
        "<root><status>1</status>"
        "<login>testuser1</login>"
        "<account><characters>0</characters>"
        "<id>124579</id></account>"
        "<firstname>vasya</firstname><logincount>0</logincount><firstlogin>yes</firstlogin>"
        "<transaction><id>17925680</id>"
        "<boxname>acapelabox_17925680</boxname><acaboxfilename>acapelabox_17925680.mp3</acaboxfilename></transaction></root>"
    )

    with patch('requests.sessions.Session.post') as post_method:
        post_method.return_value = invalid_credentials_mock
        with pytest.raises(InvalidCredentialsError):
            acapela.login("foo", "bar")

        post_method.return_value = needs_update_credentials_mock
        with pytest.raises(NeedsUpdateError):
            acapela.login("foo", "bar")

        post_method.return_value = success_mock
        acapela.login("testuser1", "succe$$p@ssw0rd!")
