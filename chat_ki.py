import requests
from bs4 import BeautifulSoup
import edge_tts
import os
import asyncio
import concurrent.futures
import regex as re
import ki

# keyboard immortal
chapters = ki.chapters
novel = "KI"
base_url = f"https://novelbin.com/b/keyboard-immortal-novel/"
location = novel.lower()

chapters_lot = {
    "KI": 2,
    "SS": 3
}

voice_list = {
    "KI": "Microsoft Andrew Online (Natural) - English (United States)",
    "SS": "Microsoft Steffan Online (Natural) - English (United States)"
}


batch = 2


def fetch_chapter(chapter):
    """Function to scrape the text for a given chapter."""
    new_text = ""
    try:
        chapter = chapter.lower()
        url = f"{base_url}{chapter}"
        response = requests.get(url)
        if response.status_code == 404:
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
        new_text = new_text.replace("\\", "")
        return new_text
    except Exception as e:
        return "continue"


def scrape_chapters_in_threads(chapters_to_convert):
    """Use multithreading to scrape all chapters concurrently."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_chapter, chapters_to_convert))
    return results


async def generate_audio(chapter_text, voice, output_file, semaphore):
    """Function to generate audio for a given chapter text, limited by semaphore."""
    async with semaphore:  # Ensures only 2 tasks run in parallel
        communicate = edge_tts.Communicate(chapter_text, voice, pitch="+5Hz", rate="-5%")
        await communicate.save(output_file)


async def tts() -> None:
    """Main function to convert scraped chapters to speech in parallel."""
    voices = await edge_tts.list_voices()
    os_path = os.getcwd()

    # Get the latest chapter to convert
    for chapter in reversed(chapters):
        chapter = chapter.split("-")[1]
        if ":" in chapter:
            chapter = chapter.replace(":", "")
        if int(chapter) % int(chapters_lot[novel]) == 0:
            chapters_to_convert = chapter
            break

    folder_path = f"{os_path}/output_file/{location}"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Semaphore to limit concurrency to 2 tasks at a time
    semaphore = asyncio.Semaphore(batch)

    chapters_range = range(0, int(chapters_to_convert), chapters_lot[novel])

    # Process chapters in chunks using threads for scraping
    tasks = []
    for i in chapters_range:
        text = ""

        path = f"{os_path}/output_file/{location}/{novel}-{int(i)+1}-{int(i)+chapters_lot[novel]}.mp3"
        if os.path.exists(path):
            continue

        VOICE = get_voice(novel, voices)

        chapters_to_convert = [chapters[a] for a in range(i, i+chapters_lot[novel])]
        # Use multithreading to fetch chapters concurrently
        chapters_texts = scrape_chapters_in_threads(chapters_to_convert)

        # Process fetched chapters
        for chapter, text1 in zip(chapters_to_convert, chapters_texts):
            if text1 == "done":
                print(text1, chapter)
                break

            if "-" in chapter:
                text_chapter = chapter.replace("-", " ")
            else:
                text_chapter = chapter

            text += f"{text_chapter}    .{text1}"

        print(text)

        if text == "done":
            pass
        else:
            # Schedule audio generation in parallel with limited concurrency
            OUTPUT_FILE = f"{os_path}/output_file/{location}/{novel}-{int(i)+1}-{int(i)+chapters_lot[novel]}.mp3"
            task = asyncio.create_task(generate_audio(text, VOICE, OUTPUT_FILE, semaphore))
            tasks.append(task)

    # Wait for all audio generation tasks to complete
    await asyncio.gather(*tasks)


def get_voice(novel, voices):
    """Function to get the required voice."""
    voice_need = voice_list[novel]
    for voice in voices:
        if voice["FriendlyName"] == voice_need:
            return voice["ShortName"]


# Run the TTS function
asyncio.run(tts())
