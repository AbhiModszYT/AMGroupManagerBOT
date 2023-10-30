import requests
import json, os
from io import BytesIO
from Am import dispatcher
from telegram.error import BadRequest
from Am.Plugins.disable import DisableAbleCommandHandler
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, run_async
from requests.structures import CaseInsensitiveDict




def paste(update: Update, context: CallbackContext):
    args = context.args
    bot = context.bot
    message = update.effective_message

    if message.reply_to_message:
        if message.reply_to_message.document:
            try:
                file_id = message.reply_to_message.document.file_id
            except BadRequest:
                message.reply_text(
                    "Try downloading and uploading the file yourself again, This one seem broken to me!"
                )
                return

            with BytesIO() as file:
                file.name = 'getpastefile.txt'
                new_file = bot.get_file(file_id)
                new_file.download(out=file)
                file.seek(0)
                data = file.readline()
        else:
            data = message.reply_to_message.text 


    elif len(args) >= 1:
        data = message.text.split(None, 1)[1]

    else:
        message.reply_text("What am I supposed to do with this?")
        return
    
    data = str(data)
    uri = "https://spaceb.in/api/v1/documents"
    # Replace newline characters with HTML line breaks
    data = data.replace("\n", "<br>")

    # Construct the JSON object containing the data and the file extension
    cont = {}
    cont['content'] = data
    cont['Extension'] = 'txt'
    data = json.dumps(cont)
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    resp = requests.post(uri, headers=headers, data=data)
    result = resp.json()["payload"]
    key = result["id"]
    url = f"https://spaceb.in/{key}"
    reply_text = f"Pasted to *Spacebin* : {url}"

    message.reply_text(
        reply_text, parse_mode=ParseMode.MARKDOWN
    )

    if os.path.exists(file.name):
               os.remove(file.name)



PASTE_HANDLER = DisableAbleCommandHandler("paste", paste, run_async=True)
dispatcher.add_handler(PASTE_HANDLER)

__command_list__ = ["paste"]
__handlers__ = [PASTE_HANDLER]