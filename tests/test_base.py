from unittest.mock import MagicMock, mock_open, patch

import pytest

from acapela_box.base import (AcapelaBox, InvalidCredentialsError,
                              LanguageNotSupportedError, NeedsUpdateError)


get_index_page_mock = MagicMock(return_value="<p>yes</p>")

@patch("acapela_box.AcapelaBox.get_index_page", get_index_page_mock)
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
        name, args, kwargs = get_method.mock_calls[0]
        assert args[0] == acapela.base_url+"index.php"

        get_method.return_value = second_load_page_moc
        assert "first" in acapela.get_index_page()
        name, args, kwargs = get_method.mock_calls[0]
        assert args[0] == acapela.base_url+"index.php"
        assert "second" in acapela.get_index_page(True)
        name, args, kwargs = get_method.mock_calls[0]
        assert args[0] == acapela.base_url+"index.php"

@patch("acapela_box.AcapelaBox.get_index_page", get_index_page_mock)
def test_acapela_login():
    """Test the login method of the `AcapelaBox` class."""
    acapela = AcapelaBox()
    invalid_credentials_mock = MagicMock()
    invalid_credentials_mock.text = "<root><status>0</status></root>"

    needs_update_credentials_mock = MagicMock(side_effect = ValueError)

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
        name, args, kwargs = post_method.mock_calls[0]
        assert args[0] == acapela.base_url+"login.php"

def test_acapela_box_get_languages():
    """Test the get_languages method of the `AcapelaBox` class."""
    acapela = AcapelaBox()
    languages = acapela.get_languages()
    assert len(languages) > 0
    for language in languages:
        assert "id" in language.keys()
        assert "iso" in language.keys()
        assert "language" in language.keys()

def test_acapela_box_get_voices():
    """Test the get_voices method of the `AcapelaBox` class."""
    acapela = AcapelaBox()
    languages = acapela.get_languages()
    voices = []
    l = ""
    for language in languages:
        l = language['iso']
        voices = acapela.get_voices(l)
        for voice in voices:
            assert "id" in voice.keys()
            assert "value" in voice.keys()
            assert "text" in voice.keys()
            assert "features" in voice.keys()
            assert "," in voice["features"]
            assert l == voice['language']

def test_acapela_box_get_audioformats():
    """Test the get_audioformats method of the `AcapelaBox` class."""
    acapela = AcapelaBox()
    audioformats = acapela.get_audioformats()
    assert len(audioformats) > 0
    for audioformat in audioformats:
        assert "id" in audioformat.keys()
        assert "value" in audioformat.keys()
        assert "text" in audioformat.keys()

dovaas_success_mock =  MagicMock(status_code=200, json=lambda : ({'snd_time': '4074', 'snd_id': '_fa78b130f2c57', 'snd_url': 'https://vaasbox.acapela-box.com/MESSAGES/013099097112101108097066111120095086050/Listen.php?q=DEl160wNhNL6_genKaYaaArfk2hPawgpnmECjcerfUL6ySNilm7mEPhKz855Kcdk.mp3', 'snd_size': '24764', 'res': 'OK', 'create_echo': 'ON', 'req_comment': 'Acapela Type and Talk demo', 'req_text': '\\audio=mix=/data/AcapelaBox/www/acapela-box/quicklife-stingeditmod.raw;repeat=on;volume=80\\ \\pau=1000\\ \\vct=100\\ \\spd=180\\ zxcvb \\pau=1000\\', 'req_voice': 'tyler22k', 'req_snd_kbps': 'DEFAULT', 'cl_ip': '54.36.104.97', 'req_snd_type': 'MP3', 'req_vol': '32768', 'req_spd': '180', 'req_vct': '100', 'cost': 5, 'replaced': '\\audio=mix=/data/AcapelaBox/www/acapela-box/quicklife-stingeditmod.raw;repeat=on;volume=80\\ \\pau=1000\\ \\vct=100\\ \\spd=180\\ zxcvb \\pau=1000\\'}))

@patch("acapela_box.AcapelaBox.get_index_page", get_index_page_mock)
def test_acapela_dovaas():
    """Test the dovaas method of the `AcapelaBox` class."""
    acapela = AcapelaBox()
    text = "zxcvb"
    voice = {
        "id": "tyler22k",
        "language": "en-AU",
        "features": "FMT_MP3,FMT_WAV22K,FMT_WAV8KA,FMT_WAV8KU,FMT_WAV8K,FLAG_DEFAULT",
        "value": "Tyler",
        "text": "Tyler",
    }
    audioformat = {
        "id": "FMT_MP3",
        "value": "1",
        "text": "MP3",
    }
    listen = 1
    vct = 100
    spd = 180
    codecMP3 = 1
    byline = 0
    ts=1641733189
    success_mock = MagicMock()
    success_mock.return_value = dovaas_success_mock
    with patch('requests.sessions.Session.post') as post_method:
        post_method.return_value = success_mock
        resp = acapela.dovaas(
            text=text,
            voice=voice['id'],
            format=audioformat['value'],
            listen = listen,
            vct = vct,
            spd = spd,
            codecMP3 = codecMP3,
            byline = byline,
            ts = ts,
        )
        name, args, kwargs = post_method.mock_calls[0]
        modified_text = r"\vct={vct}\ \spd={spd}\ {text}".format(vct=vct, spd=spd, text=text)
        assert args[0] == acapela.base_url+"dovaas.php"
        assert kwargs["data"] == {
            "voice":voice['id'],
            "listen":listen,
            "byline":byline,
            "format":audioformat['value'], 
            "text": modified_text,
            "spd": spd,
            "vct": vct,
            "codecMP3":codecMP3,
            "ts":ts,
        }

def test_download_file():
    """Test the download_file method of the `AcapelaBox` class."""
    acapela = AcapelaBox()
    mo = mock_open()
    def mywrite(b):
        assert type(b) == bytearray or type(b) == bytes
        assert b == b'qwerty' or b == b'asd'
        return len(b)
    mo.return_value.write = mywrite
    with patch("builtins.open", mo) as mock_file:
        with patch('requests.sessions.Session.get') as get_method:
            get_method.return_value.raise_for_status = MagicMock()
            get_method.return_value.iter_content = MagicMock(return_value=iter([b"qwerty", b"asd"]))
            myfile = "mymessage.mp3"
            u = "https://local.host/messages/234.mp3"
            acapela.download_file(u, myfile)
            name, args, kwargs = get_method.mock_calls[0]
            assert args[0] == u
            assert kwargs.get('stream', False) == True
            name, args, kwargs = get_method.return_value.iter_content.mock_calls[0]
            assert "chunk_size" in kwargs
            assert type(kwargs["chunk_size"]) == int
            assert kwargs['chunk_size'] > 500
            name, args, kwargs = mock_file.mock_calls[0]
            assert args[0] == myfile
            assert args[1] == "wb"
