from Am import dispatcher
from telegram.ext import CallbackContext
from telegram import Update
from Am.Plugins.disable import DisableAbleCommandHandler


def handwrite(update:Update, context: CallbackContext):
    bot = context.bot
    message = update.effective_message
    chat_id = update.effective_chat.id
    args = message.text.split(" ", 1)
    
    if not message.reply_to_message:
        if len(args) == 1:
            message.reply_text('You should provide me text also.\nExample: `/write i am writing this message`')
            return
        m = message.reply_text("Writing your text...")
        text = args[1]
        photo = "https://apis.xditya.me/write?text=" + text
        bot.send_photo(chat_id, photo=photo)
        m.delete()
    else:
        lol = message.reply_to_message.text
        name = lol.split(None, 0)[0].replace(" ", "%20")
        m =  bot.send_message(message.chat.id, "writing your message..")
        photo = "https://apis.xditya.me/write?text=" + name
        bot.send_photo(chat_id, photo=photo)
        m.delete()

WRITE_HANDLER = DisableAbleCommandHandler("write", handwrite, run_async=True)
dispatcher.add_handler(WRITE_HANDLER)

__mod_name__ = "Write"

__help__ = """Write the given text on white page with pen 🖊
 ‣ `/write <text>` *:* The write command can be used to generate an image of the specified text written on a white page with a pen. This can be useful for creating a more personal or handwritten look for text, such as in a note or letter.
 """