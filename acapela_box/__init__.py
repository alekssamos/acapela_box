import re
import json
import time
import math
from typing import List, Optional, Iterable, Callable
import requests
from pyquery import PyQuery as pq # type: ignore

class AcapelaBox():
    base_url:str = "https://acapela-box.com/AcaBox/"
    session:requests.Session = requests.Session()
    session.headers.update({
        "User-Agent": r"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
    })
    index_page:str = ''
    def __init__(self):
        self.get_index_page()

    def get_index_page(self)->str:
        self.index_page = self.session.get(self.base_url+"index.php").content.decode("UTF-8")
        return self.index_page

    def login(self, username:str, password:str, mode:Optional[str] = "login")->int:
        data = {"username":username, "password":password, "mode":mode}
        d:Callable = pq(self.session.post(self.base_url+"login.php", data=data).content.decode("UTF-8"))
        return int(d("root status").text())

    def get_languages(self)->List[dict]:
        htmlpage:str = self.index_page
        d:Callable = pq(htmlpage)
        select:Callable = d("#acaboxlanguage_cb")
        options:Iterable = select("option")
        languages:List[dict] = []
        for option in options:
            languages.append({
                "id": pq(option).attr("data-id").strip(),
                "iso": pq(option).attr("data-language").strip(),
                "language": pq(option).text().strip()
            })
        return languages

    def get_audioformats(self)->List[dict]:
        htmlpage:str = self.index_page
        d:Callable = pq(htmlpage)
        select:Callable = d("#audioformat_cb")
        options:Iterable = select("option")
        audioformats:List[dict] = []
        for option in options:
            audioformats.append({
                "id": pq(option).attr("id").strip(),
                "value": pq(option).attr("value").strip(),
                "text": pq(option).text().strip()
            })
        return audioformats

    def get_voices(self, iso:str)->List[dict]:
        if not type(iso) == str:
            ValueError("iso must be str")
        if "-" not in iso or len(iso) < 5:
            ValueError("iso must be country code hyphen language code two letters")
        data = {"ISO":iso}
        htmlpage:str = self.session.post(self.base_url+"filtervoices.php", data=data).content.decode("UTF-8")
        d:Callable = pq(htmlpage)
        select:Callable = d("#acaboxvoice_cb")
        options:Iterable = select("option")
        voices:List[dict] = []
        for option in options:
            voices.append({
                "id": pq(option).attr("data-id").strip(),
                "language": pq(option).attr("data-language").strip(),
                "features": pq(option).attr("data-features").strip(),
                "value": pq(option).attr("value").strip(),
                "text": pq(option).text().strip()
            })
        return voices

    def get_text_info(self, text:str, voice:str, voiceid:str, byline:Optional[int] = 0)->dict:
        data = {"voice":voice,"voiceid":voiceid,"byline":byline}
        j = json.loads(self.session.post(self.base_url+"GetTextInfo.php", data=data).content.decode("UTF-8"))
        return j

    def dovaas(
        self,
        text:str,
        voice:str,
        format:str,
        listen:Optional[int] = 1,
        vct:Optional[int] = 100,
        spd:Optional[int] = 180,
        codecMP3:Optional[int] = 1,
        byline:Optional[int] = 0,
        ts:Optional[int] = math.floor(time.time())
    )->dict:
        # notes: voice == voiceid
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
        j = json.loads(self.session.post(self.base_url+"dovaas.php", data=data).content.decode("UTF-8"))
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
        j = json.loads(self.session.post(self.base_url+"acabox-flashsession.php", data=data).content.decode("UTF-8"))
        return j

    def download_file(self, url:str, filename:str)->int:
        with open(filename, "wb") as f:
            return f.write(self.session.get(url).content)

