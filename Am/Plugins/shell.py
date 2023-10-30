import subprocess

from Am import LOGGER, dispatcher
from Am.Handlers.validation import dev_plus
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler
from telegram.ext.dispatcher import run_async


import subprocess

MAX_REPLY_LENGTH = 3000

@dev_plus
def shell(update: Update, context: CallbackContext):
    message = update.effective_message
    command_args = message.text.split(" ", 1)
    if len(command_args) == 1:
        message.reply_text("No command to execute was given.")
        return
    command_string = command_args[1]

    try:
        process = subprocess.Popen(
            command_string,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
    except Exception as e:
        message.reply_text(f"An error occurred while executing the command: {e}")
        return

    stdout, stderr = process.communicate()
    reply = ""

    stdout_str = stdout.decode()
    stderr_str = stderr.decode()

    if stdout_str:
        reply += f"*Stdout*\n`{stdout_str}`\n"
        LOGGER.info(f"Shell - {command_string} - {stdout_str}")
    if stderr_str:
        reply += f"*Stderr*\n`{stderr_str}`\n"
        LOGGER.error(f"Shell - {command_string} - {stderr_str}")

    if len(reply) > MAX_REPLY_LENGTH:
        with open("shell_output.txt", "w") as file:
            file.write(reply)
        with open("shell_output.txt", "rb") as doc:
            context.bot.send_document(
                document=doc,
                filename=doc.name,
                reply_to_message_id=message.message_id,
                chat_id=message.chat_id,
            )
    else:
        message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


SHELL_HANDLER = CommandHandler(["sh"], shell, run_async=True)
dispatcher.add_handler(SHELL_HANDLER)
__mod_name__ = "Shell"
__command_list__ = ["sh"]
__handlers__ = [SHELL_HANDLER]