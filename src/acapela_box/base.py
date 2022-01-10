"""Base classes for Acapela-box.com website communication."""
import math
import re
import time
from typing import Callable, Iterable, List, Optional, Union
from urllib.parse import urlencode

import requests

from . import data


class AcapelaBoxError(Exception):
    """Base exception class for Acapela Box related errors."""


class InvalidCredentialsError(AcapelaBoxError):
    """Exception class for invalid credentials error."""


class NeedsUpdateError(AcapelaBoxError):
    """Exception class thrown when the code cannot scrap the website.

    Basically, it means that the module needs some update to keep
    interfacing with the Acapela Box website.
    """


class LanguageNotSupportedError(AcapelaBoxError):
    """Exception class thrown when the language is not supported.

    For a complete list of supported languages, see data.py.
    """


class AcapelaBox():
    """the basic class.

    Raises:
        NeedsUpdateError: In case of changes on the website
        InvalidCredentialsError: Username or password is not correct
        TypeError: Invalid data type
        ValueError: Value not found
        LanguageNotSupportedError: You have passed an unknown language code

    Returns:
        AcapelaBox: A class instance
    """
    base_url: str = "https://acapela-box.com/AcaBox/"
    session: requests.Session = requests.Session()
    # session.verify=False
    # session.proxies = {
    # "https": "http://127.0.0.1:8888"
    # }
    session.headers.update({
        "User-Agent": r"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
    })
    index_page: str = ''

    def __init__(self):
        """Initializing a class."""
        pass

    def get_index_page(self, reload_page: Optional[bool] = False) -> str:
        """Refer to the main page of the site.

        Args:
            reload_page (Optional[bool], optional): Load again from the Internet or take an already loaded page from the cache. Defaults to False.

        Returns:
            str: [The HTML code]
        """
        if reload_page or self.index_page == '':
            self.index_page = self.session.get(
                self.base_url + "index.php",
            ).text
        return self.index_page

    def between(self, start: str, end: str, string: str) -> str:
        """Get a substring between the start and end strings.

        Args:
            start (str): The begin substring
            end (str): end substring
            string (str): full string
        Raises:
            ValueError: if the index string method found no matches
        Returns:
            str: the substring being searched for
        """
        return string[string.index(start) + len(start):string.index(end)]

    def tag_between(self, tagname: str, string: str) -> str:
        """Get text between XML tags.

        Args:
            tagname (str): The tagname without less and more
            string (str): XML code

        Raises:
            NeedsUpdateError: The desired tag was not found

        Returns:
            str: The extracted text
        """
        try:
            return self.between(f"<{tagname}>", f"</{tagname}>", string)
        except ValueError:
            raise NeedsUpdateError(f"Can't get the information from {tagname}")

    def login(
        self, login: str, password: str,
        mode: Optional[str] = "login",
    ) -> dict:
        """Log in to the site.

        Args:
            login (str): username
            password (str): password
            mode (Optional[str], optional): mode. Defaults to "login".

        Raises:
            InvalidCredentialsError: You have entered the wrong username and password pair

        Returns:
            dict: Information about your account
        """
        self.get_index_page()
        headers = self.session.headers.copy()
        headers.update({
            "Referer": self.base_url + "index.php",
            "Content-type": "application/x-www-form-urlencoded",
            "Origin": "https://acapela-box.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        })
        data = urlencode({"login": login, "password": password, "mode": mode})
        d: str = self.session.post(
            self.base_url + "login.php",
            headers=headers,
            data=data,
        ).text
        root: str = self.tag_between("root", d)
        if int(self.tag_between("status", root)) == 0:
            raise InvalidCredentialsError("Wrong couple of login/password.")
        account: str = self.tag_between("account", root)
        transaction: str = self.tag_between("transaction", root)
        return {
            "status": int(self.tag_between("status", root)),
            "login": self.tag_between("login", root),
            "account": {
                "characters": self.tag_between("characters", account),
                "id": int(self.tag_between("id", account)),
            },
            "firstname": self.tag_between("firstname", root),
            "logincount": int(self.tag_between("logincount", root)),
            "firstlogin": self.tag_between("firstlogin", root),
            "transaction": {
                "id": int(self.tag_between("id", transaction)),
                "boxname": self.tag_between("boxname", transaction),
                "acaboxfilename": self.tag_between("acaboxfilename", transaction),
            },
        }

    def get_languages(self) -> List[dict]:
        """Get a list of all supported languages.

        Returns:
            List[dict]: list of languages
        """
        return data.languages

    def get_audioformats(self) -> List[dict]:
        """Get a list of supported audio formats.

        Returns:
            List[dict]: List of formats
        """
        return data.audioformats

    def get_voices(self, iso: str) -> List[dict]:
        """Get a list of voices.

        Args:
            iso (str): the country code and the language code are two letters separated by a hyphen

        Raises:
            TypeError: Wrong data type
            ValueError: Error in the value
            LanguageNotSupportedError: This language is not supported

        Returns:
            List[dict]: voice list
        """
        if not isinstance(iso, str):
            raise TypeError("iso must be str")
        if "-" not in iso or len(iso) < 5 or len(iso) > 9:
            raise ValueError(
                "iso must be country code hyphen language code two letters. Example: en-US",
            )
        if iso not in [v['language'] for v in data.voices]:
            raise LanguageNotSupportedError(f"Iso code {iso} not found")
        return [v for v in data.voices if v['language'] == iso]

    def get_text_info(
            self,
            text: str,
            voice: str,
            voiceid: str,
            byline: Optional[int] = 0,
    ) -> dict:
        """Get information about the entered text.

        Args:
            text (str): The text
            voice (str): voice value
            voiceid (str): voice ID
            byline (Optional[int], optional): Export by line. Maybe 1 or 0. Defaults to 0.

        Returns:
            dict: The info about the text
        """
        self.get_index_page()
        data = {"voice": voice, "voiceid": voiceid, "byline": byline}
        j: dict = self.session.post(
            self.base_url +
            "GetTextInfo.php",
            data=data,
        ).json()
        return j

    def dovaas(
        self,
        text: str,
        voice: str,
        spd: Optional[int] = 180,
        vct: Optional[int] = 100,
        format: Optional[int] = 1,
        byline: Optional[int] = 0,
        listen: Optional[int] = 1,
        codecMP3: Optional[int] = 1,
        ts: Optional[int] = math.floor(time.time()),
    ) -> dict:
        """Synthesize text.

        Args:
            text (str): The text to be spoken. SPD and vct tags are supported
            voice (str): voice ID
            spd (Optional[int], optional): Speech rate. Defaults to 180 (average value).
            vct (Optional[int], optional): Speech pitch. Defaults to 100 (average value).
            format (Optional[int], optional): Audio file format (value). Defaults to 1.
            byline (Optional[int], optional): Export by line. It can be 1 or 0. Defaults to 0.
            listen (Optional[int], optional): Have you clicked the listen button on the website?. Defaults to 1.
            codecMP3 (Optional[int], optional): This parameter is always 1, even if a different format is specified. Defaults to 1.
            ts (Optional[int], optional): Request timestamp. Defaults to math.floor(time.time()).

        Returns:
            dict: Information about the audio recording, a direct link to the audio file is in `snd_url`
        """
        self.get_index_page()
        text = r"\vct={vct}\ \spd={spd}\ {text}".format(
            vct=vct, spd=spd, text=text,
        )
        data = {
            "voice": voice,
            "listen": listen,
            "byline": byline,
            "format": format,
            "text": text,
            "spd": spd,
            "vct": vct,
            "codecMP3": codecMP3,
            "ts": ts,
        }
        j: dict = self.session.post(
            self.base_url + "dovaas.php",
            data=data,
        ).json()
        return j

    def acabox_flashsession(
        self,
        text: str,
        voice: str,
        audioformat: Optional[int] = 1,
        speechrate: Optional[int] = 180,
        vocaltract: Optional[int] = 100,
        fontsize: Optional[int] = 13,
        automatictextname: Optional[int] = 0,
        exportlinebyline: Optional[int] = 0,
        session: Optional[str] = "save",
    ) -> dict:
        """Save the text and its parameters to the session on the website.

        Args:
            text (str): The text to pronounce that needs to be saved
            voice (str): voice ID
            audioformat (Optional[int], optional): audioformat value. Defaults to 1 (MP3)
            speechrate (Optional[int], optional): Speech rate to save settings. Defaults to 180.
            vocaltract (Optional[int], optional): I don't know what it is yet. Defaults to 100.
            fontsize (Optional[int], optional): Font size in the text field on the website. Defaults to 13.
            automatictextname (Optional[int], optional): Not sure what it is. Defaults to 0.
            exportlinebyline (Optional[int], optional): Export text by lines? 1 or 0. Defaults to 0.
            session (Optional[str], optional): action? I'm not sure. Defaults to "save".

        Returns:
            dict: The info about this session?
        """
        self.get_index_page()
        data = {
            "voice": voice,
            "speechrate": speechrate,
            "vocaltract": vocaltract,
            "fontsize": fontsize,
            "audioformat": audioformat,
            "automatictextname": automatictextname,
            "exportlinebyline": exportlinebyline,
            "text": text,
            "session": session,
        }
        j: dict = self.session.post(
            self.base_url +
            "acabox-flashsession.php",
            data=data,
        ).json()
        return j

    def download_file(self, url: str, filename: str) -> int:
        """Download file.

        Args:
            url (str): Direct link to the file
            filename (str): The path and name of the file where it will be saved on your device

        Returns:
            int: The size of the recorded data in the file in bytes
        """
        total_size: int = 0
        r = self.session.get(url, stream=True)
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    total_size += f.write(chunk)
                    f.flush()
        return total_size

    def authenticate(self, username: str, password: str):
        """Authenticate against the website using `login` and `password`.

        The session will use the provided credentials to scrap the website.
        It is useful mostly for retrieving sound with no background music
        set when an anonymous user listens to a text-to-speech sound.

        To obtain some credentials, you must register here:
        https://www.acapela-box.com/

        Args:
            username: The account's username used for registration.
            password: The account's password used for registration.

        Note:
            If no exception
                is raised, then the authentication succeeded.

        Raises:
            AcapelaBoxError: something went wrong while authenticating.
        """

        self.login(username, password)

    def get_mp3_url(self, language:str, voice:str, text:str, spd:Optional[int] = 180, vct:Optional[int] = 100, format:Optional[int] = 1, byline: Optional[int] = 0):
        """Retrieve the mp3 url associated to the settings.

        To see the list of supported languages and voices, check the `data` module.

        Args:
            language (str): The language to use for the acapela.
            voice (str): The voice name to use for the acapela.
            text (str): the text to translate to speech.
            spd (Optional[int], optional): Speech rate. Defaults to 180 (average value).
            vct (Optional[int], optional): Speech pitch. Defaults to 100 (average value).
            format (int, optional): Audio file format (value). Defaults to 1.
            byline (Optional[int], optional): Export by line. It can be 1 or 0. Defaults to 0.

        Raises:
            NeedsUpdateError: The module needs an update since the mp3
                url could not have been extracted, somehow.

        Returns:
            str: An HTTP url pointing to the generated mp3.
        """

        selected_lang = None
        selected_voice = None
        for l in self.get_languages():
            if language in (l['iso'], l['language'], str(l['id'])):
                selected_lang = l['iso']
        if selected_lang is None:
            raise LanguageNotSupportedError("You specified the wrong language")
        for v in self.get_voices(selected_lang):
            if voice in (v['value'], v['text'], v['id']):
                selected_voice = v
        if selected_voice is None:
            raise ValueError("Voice not found")
        if not str(format).isdigit():
            raise TypeError("The format is indicated by a digit")
        try:
            self.acabox_flashsession(text=text, voice=v['id'], audioformat=format)
            return self.dovaas(
                voice=selected_voice['id'],
                text=text,
                spd=spd,
                vct=vct,
                format=format,
                byline=byline
            )['snd_url']
        except KeyError:
            raise NeedsUpdateError("I can't extract the link to the audio")
