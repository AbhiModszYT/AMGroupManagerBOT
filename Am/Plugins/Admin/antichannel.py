
import html

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext.filters import Filters

from Am.Handlers.annonymous import AdminPerms, user_admin
from Am.Handlers.decorators import Amcmd, Ammsg
from Am.Database.antichannel_sql import (
    antichannel_status,
    disable_antichannel,
    enable_antichannel,
)


@Amcmd(command="antichannelmode", group=100)
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
def set_antichannel(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    if len(args) > 0:
        s = args[0].lower()
        if s in ["yes", "on"]:
            enable_antichannel(chat.id)
            message.reply_html(f"Enabled AntiChannel in {html.escape(chat.title)}")
        elif s in ["off", "no"]:
            disable_antichannel(chat.id)
            message.reply_html(f"Disabled AntiChanenel in {html.escape(chat.title)}")
        else:
            message.reply_text(f"i could't understand {s}")
        return
    message.reply_html(
        f"AntiChannel setting is currently {antichannel_status(chat.id)} in {html.escape(chat.title)}"
    )


@Ammsg(Filters.chat_type.groups, group=110)
def eliminate_channel(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    bot = context.bot
    if not antichannel_status(chat.id):
        return
    if (
        message.sender_chat
        and message.sender_chat.type == "channel"
        and not message.is_automatic_forward
    ):
        message.delete()
        sender_chat = message.sender_chat
        bot.ban_chat_sender_chat(sender_chat_id=sender_chat.id, chat_id=chat.id)

