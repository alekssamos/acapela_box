#!/usr/bin/env python3
import json
from acapela_box import AcapelaBox

code:str = """
# generated automatically

import json
""".lstrip()

ab:AcapelaBox = AcapelaBox()
languages:list = ab.get_languages()
code = code + "languages = " + json.dumps(languages, indent=4) + "\n\n"

all_voices:list = []
voices:list = []
for language in languages:
    voices = ab.get_voices(language['iso'])
    all_voices = all_voices + voices

code = code + "voices = " + json.dumps(all_voices, indent=4) + "\n\n"

audioformats:list = ab.get_audioformats()
code = code + "audioformats = " + json.dumps(audioformats, indent=4) + "\n"

with open("acapela_box_data.py", "w", encoding="UTF-8") as f:
    f.write(code)
