"""Base classes for Acapela-box.com website communication."""
import re
import time
import math
from urllib.parse import urlencode
from typing import List, Optional, Iterable, Callable, Union
import requests
from . import data

class AcapelaBoxError(Exception):
    """Base exception class for Acapela Box related errors."""


class InvalidCredentialsError(AcapelaBoxError):
    """Exception class for invalid credentials error."""


class NeedsUpdateError(AcapelaBoxError):
    """Exception class thrown when the code cannot scrap the website.

    Basically, it means that the module needs some update to keep interfacing
    with the Acapela Box website.
    """


class LanguageNotSupportedError(AcapelaBoxError):
    """Exception class thrown when the language is not supported.

    For a complete list of supported languages, see data.py.
    """


class AcapelaBox():
    base_url:str = "https://acapela-box.com/AcaBox/"
    session:requests.Session = requests.Session()
    # session.verify=False
    # session.proxies = {
        # "https": "http://127.0.0.1:8888"
    # }
    session.headers.update({
        "User-Agent": r"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
    })
    index_page:str = ''
    def __init__(self):
        pass  

    def get_index_page(self, reload_page:Optional[bool] = False)->str:
        if reload_page or self.index_page == '':
            self.index_page = self.session.get(self.base_url+"index.php").text
        return self.index_page

    def between(self, start:str, end:str, string:str)->str:
        return string[string.index(start)+len(start):string.index(end)]

    def tag_between(self, tagname:str, string:str)->str:
        try:
            return self.between(f"<{tagname}>", f"</{tagname}>", string)
        except ValueError:
            raise NeedsUpdateError(f"Can't get the information from {tagname}")

    def login(self, login:str, password:str, mode:Optional[str] = "login")->dict:
        self.get_index_page()
        headers = self.session.headers.copy()
        headers.update({
            "Referer": self.base_url+"index.php",
            "Content-type": "application/x-www-form-urlencoded",
            "Origin": "https://acapela-box.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        })
        data = urlencode({"login":login, "password":password, "mode":mode})
        d:str = self.session.post(self.base_url+"login.php", headers=headers, data=data).text
        root:str = self.tag_between("root", d)
        if int(self.tag_between("status", root)) == 0:
            raise InvalidCredentialsError("Wrong couple of login/password.")
        account:str = self.tag_between("account", root)
        transaction:str = self.tag_between("transaction", root)
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
                "acaboxfilename": self.tag_between("acaboxfilename", transaction)
            }
        }

    def get_languages(self)->List[dict]:
        return data.languages

    def get_audioformats(self)->List[dict]:
        return data.audioformats

    def get_voices(self, iso:str)->List[dict]:
        if not type(iso) == str:
            raise TypeError("iso must be str")
        if "-" not in iso or len(iso) < 5 or len(iso) > 9:
            raise ValueError("iso must be country code hyphen language code two letters. Example: en-US")
        if iso not in [v['language'] for v in data.voices]:
            raise LanguageNotSupportedError(f"Iso code {iso} not found")
        return [v for v in data.voices if v['language'] == iso]

    def get_text_info(self, text:str, voice:str, voiceid:str, byline:Optional[int] = 0)->dict:
        self.get_index_page()
        data = {"voice":voice,"voiceid":voiceid,"byline":byline}
        j:dict = self.session.post(self.base_url+"GetTextInfo.php", data=data).json()
        return j

    def dovaas(
        self,
        text:str,
        voice:str,
        spd:Optional[int] = 180,
        vct:Optional[int] = 100,
        format:int = 1,
        byline:Optional[int] = 0,
        listen:Optional[int] = 1,
        codecMP3:Optional[int] = 1,
        ts:Optional[int] = math.floor(time.time())
    )->dict:
        # notes: voice == voiceid
        self.get_index_page()
        text = r"\vct={vct}\ \spd={spd}\ {text}".format(vct=vct, spd=spd, text=text)
        data = {
            "voice":voice,
            "listen":listen,
            "byline":byline,
            "format":format, 
            "text": text,
            "spd": spd,
            "vct": vct,
            "codecMP3":codecMP3,
            "ts":ts
        }
        j:dict = self.session.post(self.base_url+"dovaas.php", data=data).json()
        return j

    def acabox_flashsession(
        self,
        text:str,
        voice:str,
        audioformat:int,
        speechrate:Optional[int] = 180,
        vocaltract:Optional[int] = 100,
        fontsize:Optional[int] = 13,
        automatictextname:Optional[int] = 0,
        exportlinebyline:Optional[int] = 0,
        session:Optional[str] = "save"
    )->dict:
        # notes: voice == voiceid, plus, not %20 in text spaces
        self.get_index_page()
        data = {
            "voice":voice,
            "speechrate":speechrate,
            "vocaltract":vocaltract,
            "fontsize":fontsize,
            "audioformat":audioformat,
            "automatictextname":automatictextname,
            "exportlinebyline":exportlinebyline,
            "text":text,
            "session":session
        }
        j:dict = self.session.post(self.base_url+"acabox-flashsession.php", data=data).json()
        return j

    def download_file(self, url:str, filename:str)->int:
        total_size:int = 0
        r = self.session.get(url, stream=True)
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk:
                    total_size += f.write(chunk)
                    f.flush()
        return total_size
