import tempfile
from yt_dlp import YoutubeDL
from yt_dlp import utils as ytutils
import shutil
import utile.utils
import os
import subprocess
import platform
import termcolor
import validators


def check_ffmpeg():
    ffmpeg_available = True
    try:
        if "windows" in platform.platform().lower():
            subprocess.check_output(['where', 'ffmpeg'])
        else:
            subprocess.check_output(['whereis', 'ffmpeg'])
    except:
        ffmpeg_available = False
    return ffmpeg_available


class yt_logger:
    def error(msg):
        pass

    def warning(msg):
        pass

    def debug(msg):
        pass


def execute(*urls, onlyaudio: bool = False):
    audio_only = onlyaudio
    urls = list(set(urls))
    if len(urls) == 0:
        print("No url was provided.")
        return
    
    for url in urls:
        if not validators.url(url):
            print("Invalid url {}. Removing it".format(termcolor.colored(url, "green")))
            urls.remove(url)
            
    if len(urls) == 0:
        print("No valid url left.")
        return
    
    print("Downloading {} url{}{}".format(
        termcolor.colored(len(urls), "green"),
        "s" if len(urls) > 1 else "",
        " (audio only)" if audio_only else ""
    ))
    if audio_only:
        if not check_ffmpeg():
            print("FFMPEG is not installed, but is required to download only audio.")
            return
    for url in urls:
        try:
            with tempfile.NamedTemporaryFile() as temp:
                temp.close()  # Because youtube_dl needs to access it
                file_destination = temp.name
                try:
                    with utile.utils.create_spinner() as context:
                        def hook(data: dict):
                            if data.get("status") == "downloading":
                                context.text = "ETA: {}, {} done".format(
                                    data["_eta_str"], data["_percent_str"])
                            elif data.get("status") == "finished":
                                context.text = "Finished{}".format(
                                    '. Converting to audio...' if audio_only else ''
                                )
                            else:
                                context.text = data.get("status")
                        opts = {
                            "quiet": True,
                            "logger": yt_logger,
                            "progress_hooks": [hook],
                            "outtmpl": file_destination,
                            'format': 'bestaudio/best' if audio_only else None,
                        }
                        if audio_only:
                            opts["postprocessors"] = [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192'
                            }]
                        ydl = YoutubeDL(opts)
                        with ydl:
                            context.text = "Extracting video infos from url {}...".format(
                                termcolor.colored(url, "green")
                            )
                            infos = ydl.extract_info(url, download=False)
                            context.text = "Downloading video '{}'...".format(
                                termcolor.colored(infos["title"], "green"))
                            ydl.download([url])
                            context.text = "Resolving filepath..."
                            if audio_only:
                                file_destination = os.path.join(
                                    os.path.dirname(file_destination), ".mp3")
                                ext = "mp3"
                            else:
                                ext = infos["ext"]

                            new_path = utile.utils.Directory.YOUTUBE_VIDEOS + os.sep + "".join([
                                c for c in infos["title"]
                                if c.isalpha() or c.isdigit() or c == ' ']).rstrip() + "." + ext
                            i = 1
                            while os.path.isfile(new_path):
                                new_path = utile.utils.Directory.YOUTUBE_VIDEOS + os.sep + "({}) ".format(i) + \
                                    "".join([
                                        c for c in infos["title"]
                                        if c.isalpha() or c.isdigit() or c == ' ']).rstrip() + "." + ext
                                i += 1
                            context.text = "Moving file..."
                            shutil.move(file_destination, new_path)
                            context.text = termcolor.colored("Done", "green")
                    print("\nDownloaded {}".format(
                        termcolor.colored(infos["title"], "green")))
                except Exception as e:
                    print("Could not download video (url: {}, error: {})".format(url, e))
        except PermissionError:
            print("The script is missing permissions to write temporary files")


MODULE = execute
