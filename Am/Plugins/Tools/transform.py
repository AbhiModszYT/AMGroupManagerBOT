import os

from PIL import Image
from PIL import ImageOps

from Am import telethn as bot
from Am.events import register

TEMP_DOWNLOAD_DIRECTORY = ""

Converted = TEMP_DOWNLOAD_DIRECTORY + "sticker.webp"

async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if (
                DocumentAttributeFilename(file_name="AnimatedSticker.tgs")
                in reply_message.media.document.attributes
            ):
                return False
            if (
                reply_message.gif
                or reply_message.video
                or reply_message.audio
                or reply_message.voice
            ):
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False

    if not data or data is None:
        return False
    else:
        return data


@register(pattern="^/(mirror|flip|ghost|bw|poster)$")
async def transform(event):
    if not event.reply_to_msg_id:
        await event.reply("`Reply to Any media...")
        return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        await event.reply("`reply to a image/sticker.")
        return
    await bot.download_file(reply_message.media)
    msg = await event.reply("`Downloading Media...")
    if event.is_reply:
        data = await check_media(reply_message)
        if isinstance(data, bool):
            await msg.edit("`Unsupported Files....")
            return
    else:
        await event.reply("`Reply to Any Media Sur.")
        return

    try:
        await msg.edit("`Transforming this image...")
        cmd = event.pattern_match.group(1)
        file_name = "gambar.png"
        downloaded_file_name = os.path.join(TEMP_DOWNLOAD_DIRECTORY, file_name)
        transform = await bot.download_media(
            reply_message,
            downloaded_file_name,
        )
        im = Image.open(transform).convert("RGB")
        if cmd == "mirror":
            IMG = ImageOps.mirror(im)
        elif cmd == "flip":
            IMG = ImageOps.flip(im)
        elif cmd == "ghost":
            IMG = ImageOps.invert(im)
        elif cmd == "bw":
            IMG = ImageOps.grayscale(im)
        elif cmd == "poster":
            IMG = ImageOps.posterize(im, 2)
        IMG.save(Converted, quality=95)
        await event.client.send_file(event.chat_id,
                                     Converted,
                                     reply_to=event.reply_to_msg_id)
        os.remove(transform)
        os.remove(Converted)
    except BaseException:
        pass


@register(pattern="^/rotate(?: |$)(.*)")
async def rotate(event):
    if not event.reply_to_msg_id:
        await event.reply("`Reply to any media..")
        return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        await event.reply("`reply to a image/sticker.")
        return
    await bot.download_file(reply_message.media)
    msg1 = await event.reply("`Downloading Media...")
    if event.is_reply:
        data = await check_media(reply_message)
        if isinstance(data, bool):
            await msg1.edit("`Unsupported Files....")
            return
    else:
        await event.reply("`Reply to Any Media Sur.")
        return
    await msg1.edit("`Rotating your media...")
    try:
        value = int(event.pattern_match.group(1))
        if value > 360:
            raise ValueError
    except ValueError:
        value = 90
    file_name = "gambar.png"
    downloaded_file_name = os.path.join(TEMP_DOWNLOAD_DIRECTORY, file_name)
    rotate = await bot.download_media(
        reply_message,
        downloaded_file_name,
    )
    im = Image.open(rotate).convert("RGB")
    IMG = im.rotate(value, expand=1)
    IMG.save(Converted, quality=95)
    await event.client.send_file(event.chat_id,
                                 Converted,
                                 reply_to=event.reply_to_msg_id)
    os.remove(rotate)
    os.remove(Converted)


__mod_name__ = "Editer"