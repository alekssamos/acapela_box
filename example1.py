#!/usr/bin/env python3
from acapela_box import AcapelaBox

ab:AcapelaBox = AcapelaBox()
ls:list = ab.get_languages()
print(ls)
vs:list = ab.get_voices("en-US")
print(vs)
fs:list = ab.get_audioformats()
print(fs)

language:dict = [l for l in ls if l["iso"] == "ru-RU"][0]
voice:dict = ab.get_voices(language["iso"])[0]
format:dict = fs[0]
text:str = "Этот текст получен через питоновский скрипт!"
audiofile = voice["language"]+"_"+voice["text"]+".mp3"
print(language, voice, format, text, audiofile, sep="\n")
print("Everything is ready to start!")

# ab.get_text_info(text=text, voice=voice['value'], voiceid=voice['id'])
ab.acabox_flashsession(text=text, voice=voice['id'], audioformat=format['id'])
resp = ab.dovaas(text=text, voice=voice['id'], format=format['value'])
result:int = ab.download_file(resp['snd_url'], audiofile)
print("result", result)
