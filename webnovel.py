import requests
from bs4 import BeautifulSoup
import edge_tts
import os
import asyncio
import regex as re
import patch
import ss

#keyboard immortal
chapters = ss.chapters
novel = "SS"
base_url = f"https://novelbin.com/b/shadow-slave/"
# base_url = f"https://novelbin.com/b/keyboard-immortal-novel/"
location = novel.lower()

chapters_lot = {
    "KI":2,
    "SS":3
}

voice_list = {
    "KI":"Microsoft Andrew Online (Natural) - English (United States)",
    "SS":"Microsoft Steffan Online (Natural) - English (United States)"
}


#avaliable Good Voices
            # Microsoft Ryan Online (Natural) - English (United Kingdom)
            # Microsoft AndrewMultilingual Online (Natural) - English (United States)
            # Microsoft Christopher Online (Natural) - English (United States)
            # Microsoft Ava Online (Natural) - English (United States)
            # Microsoft Steffan Online (Natural) - English (United States)
            # Microsoft Andrew Online (Natural) - English (United States)



def main(chapter):
    new_text = ""
    try:
        chapter = chapter.lower()
        url = f"{base_url}{chapter}"
        response = requests.get(url)
        if response.status_code == 404 :
            return "done"
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.find_all("p")
        for paragraph in text:
            paragraph = paragraph.get_text()
            if paragraph == " Translator: Pika\n":
                continue
            if "1." in paragraph:
                break
            new_text += paragraph
        if "\\" in new_text:
            new_text.replace("\\","")
        return new_text
    except Exception as e:
        return "continue"


async def tts() -> None:
    voices = await edge_tts.list_voices()
    os_path = os.getcwd()
    for chapter in reversed(chapters):
        chapter = chapter.split("-")[1]
        if ":" in chapter:
            chapter = chapter.replace(":", "")
        if int(chapter)%int(chapters_lot[novel]) == 0:
            chapters_to_convert = chapter   
            break


    folder_path = f"{os_path}\\output_file\\{location}"


    if os.path.exists(folder_path) == False:
        os.makedirs(folder_path)


    for i in range(0,int(chapters_to_convert),chapters_lot[novel]):

        text = ""

        path = f"{os_path}\\output_file\\{location}\\{novel}-{int(i)+1}-{int(i)+chapters_lot[novel]}.mp3"

        if os.path.exists(path):
            continue

        VOICE = get_voice(novel, voices)

        for a in range(i,i+chapters_lot[novel]):
            chapter = chapters[a]

            
            OUTPUT_FILE = f"{os_path}\\output_file\\{location}\\{novel}-{int(i)+1}-{int(i)+chapters_lot[novel]}.mp3"

            if "-" in chapter:
                text_chapter = chapter.replace("-"," ")
            elif "-" in chapter:
                text_chapter = chapter.replace("-"," ")


            if text == "":
                text += f"{text_chapter}.     "
            else:
                text += f".   {text_chapter}.     "


            text1 = main(chapter)
            text += text1
            if text1 == "done":
                print(text1, chapter)
                break

        print(text)

        if text == "done":
            pass
        else:
            communicate = edge_tts.Communicate(text, VOICE, pitch = "+5Hz",rate = "-5%")
            await communicate.save(OUTPUT_FILE)




def get_voice(novel, voices):


            voice_need = voice_list[novel]

            for voice in voices:
                # print(voice["FriendlyName"])
                if voice["FriendlyName"] == voice_need:
                    speak_voice = voice["ShortName"]
                    return speak_voice 

            
asyncio.run(tts())