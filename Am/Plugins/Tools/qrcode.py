import os
import asyncio

import qrcode
import barcode
from barcode.writer import ImageWriter

from bs4 import BeautifulSoup

from Am import LOGGER
from Am.events import register


@register(pattern="^/decode$")
async def parseqr(qr_e):
    """For /decode command, get QR Code/BarCode content from the replied photo."""
    downloaded_file_name = await qr_e.client.download_media(
        await qr_e.get_reply_message())
    # parse the Official ZXing webpage to decode the QRCode
    command_to_exec = [
        "curl", "-X", "POST", "-F", "f=@" + downloaded_file_name + "",
        "https://zxing.org/w/decode"
    ]
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    os.remove(downloaded_file_name)
    if not t_response:
        LOGGER.info(e_response)
        LOGGER.info(t_response)
        return await qr_e.reply("Failed to decode.")
    soup = BeautifulSoup(t_response, "html.parser")
    qr_contents = soup.find_all("pre")[0].text
    await qr_e.reply(qr_contents)


@register(pattern="/barcode(?: |$)([\s\S]*)")
async def bq(event):
    """For /barcode command, genrate a barcode containing the given content."""
    await event.reply("`Processing..`")
    input_str = event.pattern_match.group(1)
    message = "SYNTAX: `/barcode <long text to include>`"
    reply_msg_id = event.message.id
    if input_str:
        message = input_str
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        reply_msg_id = previous_message.id
        if previous_message.media:
            downloaded_file_name = await event.client.download_media(
                previous_message)
            m_list = None
            with open(downloaded_file_name, "rb") as fd:
                m_list = fd.readlines()
            message = ""
            for m in m_list:
                message += m.decode("UTF-8") + "\r\n"
            os.remove(downloaded_file_name)
        else:
            message = previous_message.message
    else:
        return event.reply("SYNTAX: `/barcode <long text to include>`")

    bar_code_type = "code128"
    try:
        bar_code_mode_f = barcode.get(bar_code_type,
                                      message,
                                      writer=ImageWriter())
        filename = bar_code_mode_f.save(bar_code_type)
        await event.client.send_file(event.chat_id,
                                     filename,
                                     reply_to=reply_msg_id)
        os.remove(filename)
    except Exception as e:
        return await event.reply(str(e))
    await event.delete()


@register(pattern="/makeqr(?: |$)([\s\S]*)")
async def make_qr(makeqr):
    """For /makeqr command, make a QR Code containing the given content."""
    input_str = makeqr.pattern_match.group(1)
    message = "SYNTAX: `/makeqr <long text to include>`"
    reply_msg_id = None
    if input_str:
        message = input_str
    elif makeqr.reply_to_msg_id:
        previous_message = await makeqr.get_reply_message()
        reply_msg_id = previous_message.id
        if previous_message.media:
            downloaded_file_name = await makeqr.client.download_media(
                previous_message)
            m_list = None
            with open(downloaded_file_name, "rb") as file:
                m_list = file.readlines()
            message = ""
            for media in m_list:
                message += media.decode("UTF-8") + "\r\n"
            os.remove(downloaded_file_name)
        else:
            message = previous_message.message

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(message)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("img_file.webp", "PNG")
    await makeqr.client.send_file(makeqr.chat_id,
                                  "img_file.webp",
                                  reply_to=reply_msg_id)
    os.remove("img_file.webp")
    await makeqr.delete()



__help__ = """
 ‣ `/beautify or /btfy `*:*  The `/beautify` or `/btfy` command is used to apply filters to an image. This can be used to enhance the appearance of a photo or to create a more artistic effect.
 ‣ `/sktech `*:*  The `/sketch`command is used to convert an image into a pencil sketch. This can be used to create a more artistic or hand-drawn look for a photo.
 
 The `/makeqr` command is used to generate a QR code, which is a type of barcode that can be scanned with a smartphone to quickly access a website or other content. To decode the content of a QR code, the `/decode` command can be used on a photo of the QR code.
 ‣ `/makeqr <content>`
Usage: Make a QR Code from the given content.
Example: /makeqr www.google.com
Note: use `/decode` <reply to barcode/qrcode> to get decoded content.

The `/barcode` command is similar to the `/makeqr` command, but it generates a standard barcode instead of a QR code. Like with QR codes, the `/decode` command can be used to retrieve the content of a barcode from a photo.
 ‣ `/barcode <content>`
Usage: Make a BarCode from the given content.
Example: /barcode www.google.com"
Note: use `/decode` <reply to barcode/qrcode> to get decoded content.
"""

__mod_name__ = "Special"