import os
import openai
import requests
import subprocess

# openapi key from https://platform.openai.com/account/api-keys
openai_api_key = ""
# elevenlabs key from https://beta.elevenlabs.io/speech-synthesis click your profile pic -> Profile
elevenlabs_key_api_key = ""
# path to ffmpeg executable download from here https://ffmpeg.org/
path_to_ffmpeg_command = "ffmpeg.exe"


def make_voice(base_path: str, text=None):
    if text is None:
        with open(base_path + "\\text.txt", "r") as file:
            text = file.read()

    elevenlabs_key = elevenlabs_key_api_key

    voice_id = "pNInz6obpgDQGcFmaJgB"

    data = {
        "text": text,
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0
        }
    }
    session = requests.Session()
    session.debug = True

    with session.post(
                "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id,
                json=data,
                headers={
                    "xi-api-key": elevenlabs_key,
                    "accept": "audio/mpeg",
                    "Content-Type": "application/json"
                },
                stream=True
            ) as r:
        r.raise_for_status()
        with open(base_path + "\\audio.mp3", "wb+") as file:
            for chunk in r.iter_content(chunk_size=8192):
                file.write(chunk)


def make_video(base_path: str):
    cmd = [
        path_to_ffmpeg_command, "-loop", "1",
        "-i", base_path + "\\image.png", "-i", base_path + "\\audio.mp3",
        "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-shortest", base_path + "\\video.mp4"
    ]

    output = subprocess.run(cmd, capture_output=True)
    print(output.stdout.decode())


def make_image(base_path, prompt):
    openai.api_key = openai_api_key

    response = openai.Image.create(
      prompt="Charcoal image of " + prompt,
      n=1,
      size="1024x1024"
    )

    image_url = response['data'][0]['url']
    image_response = requests.get(image_url)
    with open(base_path + "\\image.png", "wb+") as file:
        file.write(image_response.content)
    print(image_url)


def make_text(base_path, prompt):
    openai.api_key = openai_api_key

    response = openai.Completion.create(
      model="text-davinci-003",
      prompt="Write a sonnet about " + prompt,
      temperature=0.3,
      max_tokens=200,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )
    text = response['choices'][0]['text']
    print(text)
    with open(base_path + "\\text.txt", "w+") as file:
        file.write(text)
    return text


def main(path, prompt):
    text = make_text(path, prompt)
    make_image(path, prompt)
    make_voice(path, text)
    make_video(path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(sys.argv[1])
        path = sys.argv[1].replace(" ", "_").lower()
        path = safe_path = os.path.normpath(path)
        print(path)
        os.mkdir(path)
        main(path, sys.argv[1])
    else:
        print("No args")
