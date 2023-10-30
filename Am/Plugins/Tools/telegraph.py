import os
from pyrogram import Client, filters
from pyrogram.types import Message
from telegraph import Telegraph, exceptions, upload_file

from Am import pbot as app

telegraph = Telegraph()
r = telegraph.create_account(short_name="Am")
auth_url = r["auth_url"]

@app.on_message(filters.command(["telegraph", "ttm", "tgt"]))
async def uptotelegraph(client: Client, message: Message):
    try:
        text = message.text.split(None, 1)[1]
    except IndexError:
        text = None

    msg = await message.reply_text("`Processing...`")

    if not message.reply_to_message:
        await msg.edit("**Reply to an image or text message.**")
        return

    if message.reply_to_message or message.reply_to_message.photo:
            file_path = await message.reply_to_message.download()
            try:
                media_url = upload_file(file_path)
            except exceptions.TelegraphException as exc:
                await msg.edit(f"**ERROR:** `{exc}`")
                os.remove(file_path)
                return
            await msg.edit(f"**Uploaded on** [Telegraph](https://telegra.ph/{media_url[0]})")
            os.remove(file_path)
      

    elif message.reply_to_message.text:
        page_title = text if text else client.me.first_name
        page_text = message.reply_to_message.text.replace("\n", "<br>")
        try:
            response = telegraph.create_page(page_title, html_content=page_text)
        except exceptions.TelegraphException as exc:
            await msg.edit(f"**ERROR:** `{exc}`")
            return
        await msg.edit(f"**Uploaded as** [Telegraph](https://telegra.ph/{response['path']})")

    else:
        await msg.edit("**Unsupported file type.**")
        return


__help__ = """
 ‣ `/tgm`: Get Telegraph Link Of Replied Media
 ‣ `/tgt`: Get Telegraph Link of Replied Text
"""

__mod_name__ = "Telegraph"


