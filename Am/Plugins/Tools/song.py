import time
import os
import requests
import wget
import textwrap

from Am import dispatcher, pbot
from pyrogram import filters
from Am.Plugins.disable import DisableAbleCommandHandler
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, run_async
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


@pbot.on_message(filters.command(["song", "music"]))
def song(client, message):

    message.delete()
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    deep = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    m = message.reply("◯ Processing Query... Please Wait!...")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        # print(results)
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)

        duration = results[0]["duration"]
        results[0]["url_suffix"]
        views = results[0]["views"]

    except Exception as e:
        m.edit(
            "✖️ Found Nothing. Sorry.\n\nTry another keyword or maybe spell it properly."
        )
        print(str(e))
        return
    m.edit("`Downloading Song... Please wait ⏳`")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f"🎧**Title:** {title[:25]}\n⏳**Duration:** `{duration}`\n👀**Views:** `{views}`\n👤**Requested By** {deep}"
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
        message.reply_audio(
            audio_file,
            caption=rep,
            thumb=thumb_name,
            title=title,
            duration=dur,
        )
        m.delete()
    except Exception as e:
        m.edit(
            f"**Downloading Error, Report this at​ ➢ [Support Chat](t.me/{SUPPORT_CHAT}) 💕**\n\**Error:** {e}"
        )
        print(e)

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)


def video(update: Update, context: CallbackContext):
    bot = context.bot
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = message.text.split(" ", 1)

    if len(args) == 1:
        message.reply_text('Provide video Name also like `/video on my way`!')
        return
    else:
        pass

    urlissed = args[1]

    pablo = bot.send_message(
        message.chat.id, textwrap.dedent(
            f"Getting {urlissed} From Youtube Servers. Please Wait.")
    )
    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    thums = mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    

    try:
        is_downloading = True
        with YoutubeDL(opts) as ytdl:
            infoo = ytdl.extract_info(url, False)
            duration = round(infoo["duration"] / 60)

            if duration > 10:
                pablo.edit_text(
                    f"❌ Videos longer than 10 minute(s) aren't allowed, the provided video is {duration} minute(s)"
                )
                is_downloading = False
                return
            ytdl_data = ytdl.extract_info(url, download=True)

    except Exception as e:
        pablo.edit_text(f"*Failed To Download* \n*Error :* `{str(e)}`")
        is_downloading = False
        return

    c_time = time.time()
    file_stark = f"{ytdl_data['id']}.mp4"
    capy = textwrap.dedent(
        f"*Video Name ➠* `{thum}` \n*Requested For :* `{urlissed}` \n*Channel :* `{thums}` \n*Link :* `{mo}`")
    bot.send_video(
        chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        # file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,
        parse_mode=ParseMode.MARKDOWN,
    )
    pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)


__mod_name__ = "Music"

__help__ = """ *Now Donwload and hear/watch song on telegram*
 ‣ `/song on my way`*:* it will down song from youtube server for you
 ‣ `/video born alone die alone` *:* download video from youtube

"""


VIDEO_HANDLER = DisableAbleCommandHandler("video", video, run_async=True)

dispatcher.add_handler(VIDEO_HANDLER)
