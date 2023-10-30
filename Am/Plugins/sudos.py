import html, os
import json
from typing import Optional

from Am import (
    DEV_USERS,
    OWNER_ID,
    INSPECTOR,
    REQUESTER,
    dispatcher,
)
from Am.Handlers.validation import (
    dev_plus,
    sudo_plus,
    whitelist_plus,
)
from Am.Plugins.disable import DisableAbleCommandHandler
from Am.Handlers.extraction import extract_user
from Am.Plugins.Admin.log_channel import gloggable
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, TelegramError, Update
from telegram.ext import CallbackContext, CommandHandler, run_async
from telegram.utils.helpers import mention_html

ELEVATED_USERS_FILE = os.path.join(os.getcwd(), "Am/elevated_users.json")



def check_user_id(user_id: int, context: CallbackContext) -> Optional[str]:
    bot = context.bot
    if not user_id:
        reply = "That...is a chat! baka ka omae?"

    elif user_id == bot.id:
        reply = "This does not work that way."

    else:
        reply = None
    return reply



@dev_plus
@gloggable
def addsudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE) as infile:
        data = json.load(infile)

    if user_id in INSPECTOR:
        message.reply_text("This member is already an Inspector")
        return ""

    if user_id in REQUESTER:
        rt += "Requested owner to promote an Inspector to Requester."
        data["req"].remove(user_id)
        REQUESTER.remove(user_id)

    data["ins"].append(user_id)
    INSPECTOR.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt
        + "\nSuccessfully set position of {} to Inspector!".format(
            user_member.first_name,
        ),
    )

    log_message = (
        f"#INSPECTOR\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
def addsupport(
    update: Update,
    context: CallbackContext,
) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE) as infile:
        data = json.load(infile)

    if user_id in INSPECTOR:
        rt += "Requested owner to demote this Inspector to Requester"
        data["ins"].remove(user_id)
        INSPECTOR.remove(user_id)

    if user_id in REQUESTER:
        message.reply_text("This user is already a Requester.")
        return ""

    data["req"].append(user_id)
    REQUESTER.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\n{user_member.first_name} was added as a Requester!",
    )

    log_message = (
        f"#REQUESTER\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@dev_plus
@gloggable
def removesudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE) as infile:
        data = json.load(infile)

    if user_id in INSPECTOR:
        message.reply_text("Requested Owner to demote this user to Civilian")
        INSPECTOR.remove(user_id)
        data["ins"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNINS\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message

    else:
        message.reply_text("This user is not an Inspector more!")
        return ""


@sudo_plus
@gloggable
def removesupport(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE) as infile:
        data = json.load(infile)

    if user_id in REQUESTER:
        message.reply_text("Requested Owner to demote this user to Civilian")
        REQUESTER.remove(user_id)
        data["req"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNREQ\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message

    else:
        message.reply_text("This user is not a Requester more!")
        return ""







@whitelist_plus
def supportlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>Collecting list of all Requesters..</code>", parse_mode=ParseMode.HTML,
    )
    reply = "<b>All Requester:</b>\n"
    for each_user in REQUESTER:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def sudolist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>Collecting list of all Inspectors..</code>", parse_mode=ParseMode.HTML,
    )
    true_sudo = list(set(INSPECTOR) - set(DEV_USERS))
    reply = "<b>Known Inspectors:</b>\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@sudo_plus
def devlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>Collecting list of all Devs..</code>", parse_mode=ParseMode.HTML,
    )
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "<b>All Developers:</b>\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)





SUDO_HANDLER = CommandHandler(("addsudo", "addins"), addsudo)
SUPPORT_HANDLER = CommandHandler(("addsupport", "addreq"), addsupport)
UNSUDO_HANDLER = CommandHandler(("removesudo", "removeins"), removesudo)
UNSUPPORT_HANDLER = CommandHandler(("removesupport", "removereq"), removesupport)
SUPPORTLIST_HANDLER = CommandHandler(["reqlist", "requester"], supportlist)
SUDOLIST_HANDLER = CommandHandler(["inslist", "inspector"], sudolist)
DEVLIST_HANDLER = CommandHandler(["devlist", "masters"], devlist)

dispatcher.add_handler(SUDO_HANDLER)
dispatcher.add_handler(SUPPORT_HANDLER)
dispatcher.add_handler(UNSUDO_HANDLER)
dispatcher.add_handler(UNSUPPORT_HANDLER)
dispatcher.add_handler(SUPPORTLIST_HANDLER)
dispatcher.add_handler(SUDOLIST_HANDLER)
dispatcher.add_handler(DEVLIST_HANDLER)

__mod_name__ = "Disasters"
__handlers__ = [
    SUDO_HANDLER,
    SUPPORT_HANDLER,
    UNSUDO_HANDLER,
    UNSUPPORT_HANDLER,
    SUPPORTLIST_HANDLER,
    SUDOLIST_HANDLER,
    DEVLIST_HANDLER,
]