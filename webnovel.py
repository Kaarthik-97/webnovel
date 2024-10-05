import requests
from bs4 import BeautifulSoup
import edge_tts
import os
import asyncio
import regex as re
from test import chapters


TEXT = "Hello World!"
VOICE = "en-GB-SoniaNeural"
OUTPUT_FILE = "test.mp3"



# while True:
def main(chapter):
    new_text = ""
    try:
        chapter = chapter.lower()
        url = f"https://novelbin.com/b/shadow-slave/{chapter}"
        response = requests.get(url)
        if response.status_code == 404 :
            return "done"
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.find_all("p")
        for paragraph in text:
            paragraph = paragraph.get_text()
            new_text += paragraph
        if "\\" in new_text:
            new_text.replace("\\","")
        return new_text
    except Exception as e:
        return "continue"


async def tts() -> None:
    check = os.getcwd()
    for chapter in reversed(chapters):
        chapter = chapter.split("-")[1]
        if ":" in chapter:
            chapter = chapter.replace(":", "")
        if int(chapter)%3 == 0:
            chapters_to_convert = chapter   
            break

    for i in range(0,int(chapters_to_convert),3):
        path = f"{check}\\output_file\\SS-{int(i)+1}-{int(i)+3}.mp3"
        if os.path.exists(path):
            continue
        text = ""
        for a in range(i,i+3):
            chapter = chapters[a]
            voices = await edge_tts.list_voices()
            # Microsoft Ryan Online (Natural) - English (United Kingdom)
            # Microsoft AndrewMultilingual Online (Natural) - English (United States)
            # Microsoft Christopher Online (Natural) - English (United States)
            # Microsoft Ava Online (Natural) - English (United States)
            # Microsoft Steffan Online (Natural) - English (United States)
            voice_need = "Microsoft Steffan Online (Natural) - English (United States)"
            for voice in voices:
                # print(voice["FriendlyName"])
                if voice["FriendlyName"] == voice_need:
                    speak_voice = voice["ShortName"]
            VOICE = speak_voice
            OUTPUT_FILE = f"{check}\\output_file\\SS-{int(i)+1}-{int(i)+3}.mp3"
            if "-" in chapter:
                text_chapter = chapter.replace("-"," ")
            elif "-" in chapter:
                text_chapter = chapter.replace("-"," ")
            if text == "":
                text += f"{text_chapter}    ."
            else:
                text += f".   {text_chapter}   ."
            text += main(chapter)
        
        print(text)

        if text == "done":
            pass
        else:
            communicate = edge_tts.Communicate(text, VOICE, pitch = "+5Hz",rate = "-5%")
            await communicate.save(OUTPUT_FILE)
            
asyncio.run(tts())