import html, re
import time
import json
from datetime import datetime
from io import BytesIO

from telegram import ParseMode,  InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest, TelegramError, Unauthorized
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    run_async,
)
from telegram.utils.helpers import mention_html

import Am.Database.global_bans_sql as sql
from Am.Database.users_sql import get_user_com_chats, get_all_chats
from Am.Handlers.decorators import Ammsg
from Am import (
    DEV_USERS,
    EVENT_LOGS,
    OWNER_ID,
    INSPECTOR,
    JOIN_LOGGER,
    SUPPORT_CHAT,
    REQUESTER,
    dispatcher,
)
from Am.Handlers.validation import (
    dev_plus,
    is_user_admin,
    support_plus,
    user_admin,
)
from Am.Handlers.extraction import (
    extract_user,
    extract_user_and_text,
)
from Am.Handlers.misc import send_to_list

GBAN_ENFORCE_GROUP = 6
STRICT_GBAN = True

GBAN_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Need to be inviter of a user to kick it from a basic group",
    "Chat_admin_required",
    "Only the creator of a basic group can kick group administrators",
    "Channel_private",
    "Not in the chat",
    "Can't remove chat owner",
}

UNGBAN_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Method is available for supergroup and channel chats only",
    "Not in the chat",
    "Channel_private",
    "Chat_admin_required",
    "Peer_id_invalid",
    "User not found",
}


@support_plus
def gban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect.."
        )
        return

    if int(user_id) in DEV_USERS:
        message.reply_text(
            "That user is part of the Am Team!\nI can't act against our own."
        )
        return

    if int(user_id) in INSPECTOR:
        message.reply_text(
            "Issei! Show em power of the inspector!"
        )
        return

    if int(user_id) in REQUESTER:
        message.reply_text(
            "Trying to gban a Am servant?, you got a death wish or something?")
        return

    if user_id == bot.id:
        message.reply_text("That's what you want? You hate me that much?")
        return

    if user_id in [777000, 1087968824]:
        message.reply_text("Fool! You can't attack Telegram's native tech!")
        return

    try:
        user_chat = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return ""
        else:
            return

    if user_chat.type != 'private':
        message.reply_text("That's not a user!")
        return

    if sql.is_user_gbanned(user_id):

        if not reason:
            message.reply_text(
                "This user is already gbanned; I'd change the reason, but you haven't given me one..."
            )
            return

        old_reason = sql.update_gban_reason(
            user_id, user_chat.username or user_chat.first_name, reason)
        if old_reason:
            message.reply_text(
                "Master! this user is already gbanned, for the following reason:\n"
                "<code>{}</code>\n"
                "I've gone and updated it with your new reason!".format(
                    html.escape(old_reason)),
                parse_mode=ParseMode.HTML)

        else:
            message.reply_text(
                "Master!, this user is already gbanned, but had no reason set; I've gone and updated it!"
            )

        return


    message.reply_text("Your Gban Request has been sent to our Inpectors. have patience for approval.")
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="Approve Gban", 
                callback_data=f"a_gban({user_id})({reason})")
            
        ],
        [
            InlineKeyboardButton(
                text="Close Case", 
                callback_data="close_case({})")
        ]
        
        ])

    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if chat.type != 'private':
        chat_origin = "<b>{} ({})</b>\n".format(
            html.escape(chat.title), chat.id)
    else:
        chat_origin = "<b>{}</b>\n".format(chat.id)

    log_message = (
        f"*New Gban Request in AMBOT*\n"
        f"#GBAN_REQUEST\n"
        f"<b>Originated from:</b> <code>{chat_origin}</code>\n"
        f"<b>Request Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Banned User:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"<b>Banned User ID:</b> <code>{user_chat.id}</code>\n"
        f"<b>Event Stamp:</b> <code>{current_time}</code>")

    if reason:
        if chat.type == chat.SUPERGROUP and chat.username:
            log_message += f"\n<b>Reason:</b> <a href=\"https://telegram.me/{chat.username}/{message.message_id}\">{reason}</a>"
        else:
            log_message += f"\n<b>Reason:</b> <code>{reason}</code>"


    bot.send_message(JOIN_LOGGER, log_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    
    if EVENT_LOGS:
        try:
            log = bot.send_message(
                EVENT_LOGS, log_message, parse_mode=ParseMode.HTML)
        except BadRequest as excp:
            log = bot.send_message(
                EVENT_LOGS, log_message +
                "\n\nFormatting has been disabled due to an unexpected error.")

    else:
        send_to_list(bot, INSPECTOR + REQUESTER, log_message, html=True)



@dev_plus
def closecase(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    user = update.effective_user
    match = re.match(r"close_case\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
    
        update.effective_message.edit_text(
                "Case Closed by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )


@dev_plus
def agban(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    query = update.callback_query
    user = update.effective_user
    message = update.effective_message
    match = re.match(r"a_gban\((.+?)\)\((.+?)\)", query.data)
    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if match:
        user_id = match.group(1)
        print(user_id)
        user_chat = bot.get_chat(user_id)
        print(user_chat)
        username = user_chat.username or user_chat.first_name
        reason = match.group(2)
        print(reason)
        sql.gban_user(user_id, username, reason)       
        chats = get_user_com_chats(user_id)
        gbanned_chats = 0

        for chat in chats:
            chat_id = int(chat)

            # Check if this group has disabled gbans
            if not sql.does_chat_gban(chat_id):
                continue

            try:
                bot.ban_chat_member(chat_id, user_id)
                gbanned_chats += 1

            except BadRequest as excp:
                if excp.message in GBAN_ERRORS:
                    pass
                else:
                    message.reply_text(f"Could not gban due to: {excp.message}")
                    if EVENT_LOGS:
                        bot.send_message(
                            EVENT_LOGS,
                            f"Could not gban due to {excp.message}",
                            parse_mode=ParseMode.HTML)
                    else:
                        send_to_list(bot, INSPECTOR + REQUESTER,
                                    f"Could not gban due to: {excp.message}")
                    sql.ungban_user(user_id)
                    return
            except TelegramError:
                pass

        send_to_list(
                bot,
                INSPECTOR,
                f"Gban complete! (User {mention_html(user_chat.id, user_chat.first_name)} banned in <code>{gbanned_chats}</code> chats)",
                html=True)

        end_time = time.time()

        update.effective_message.edit_text(
                "Gban Request Accepted by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )

        log_message = (
        f"*Gban Request Approved*\n"
        f"#GBAN_APPROVED\n"
        f"<b>Approved By:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Banned User:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"<b>Banned User ID:</b> <code>{user_chat.id}</code>\n"
        f"<b>Event Stamp:</b> <code>{current_time}</code>")

        if EVENT_LOGS:
            try:
                log = bot.send_message(
                    EVENT_LOGS, log_message, parse_mode=ParseMode.HTML)
            except BadRequest as excp:
               log = bot.send_message(
                    EVENT_LOGS, log_message +
                    "\n\nFormatting has been disabled due to an unexpected error.")

        else:
            send_to_list(bot, INSPECTOR + REQUESTER, log_message, html=True)


        if EVENT_LOGS:
            log.edit_text(
                log_message + f"\n<b>Chats affected:</b> <code>{gbanned_chats}</code>",
                parse_mode=ParseMode.HTML,
            )
        else:
            send_to_list(
                bot,
                INSPECTOR,
                f"Gban complete! (User banned in <code>{gbanned_chats}</code> chats)",
                html=True,
            )

        try:
            bot.send_message(
                user_id, "#EVENT"
                "You have been marked as Malicious and as such have been banned from any future groups we manage. get some life bruh."
                f"\n<b>Reason:</b> <code>{html.escape(reason)}</code>"
                f"</b>Appeal Chat:</b> @AM_YTSUPPORT",
                parse_mode=ParseMode.HTML)
        except:
            pass  # bot probably blocked by user




        

@dev_plus
def scan(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return

    if int(user_id) in DEV_USERS:
        message.reply_text(
            "That user is part of the Association\nI can't act against our own.",
        )
        return

    if int(user_id) in INSPECTOR:
        message.reply_text(
            "I spy, with my little eye... a disaster! Why are you guys turning on each other?",
        )
        return

    if int(user_id) in REQUESTER:
        message.reply_text(
            "OOOH someone's trying to gban a Requester! *grabs popcorn*",
        )
        return


    if user_id == bot.id:
        message.reply_text("You uhh...want me to punch myself?")
        return

    if user_id in [777000, 1087968824]:
        message.reply_text("Fool! You can't attack Telegram's native tech!")
        return

    try:
        user_chat = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return ""
        else:
            return

    if user_chat.type != "private":
        message.reply_text("That's not a user!")
        return

    if sql.is_user_gbanned(user_id):

        if not reason:
            message.reply_text(
                "This user is already gbanned; I'd change the reason, but you haven't given me one...",
            )
            return

        old_reason = sql.update_gban_reason(
            user_id, user_chat.username or user_chat.first_name, reason,
        )
        if old_reason:
            message.reply_text(
                "This user is already gbanned, for the following reason:\n"
                "<code>{}</code>\n"
                "I've gone and updated it with your new reason!".format(
                    html.escape(old_reason),
                ),
                parse_mode=ParseMode.HTML,
            )

        else:
            message.reply_text(
                "This user is already gbanned, but had no reason set; I've gone and updated it!",
            )

        return

    onIt = message.reply_text("On it!")

    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if chat.type != "private":
        chat_origin = f"<b>{html.escape(chat.title)} ({chat.id})</b>\n"
    else:
        chat_origin = f"<b>{chat.id}</b>\n"

    log_message = (
        f"#GBANNED\n"
        f"<b>Originated from:</b> <code>{chat_origin}</code>\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Banned User:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"<b>Banned User ID:</b> <code>{user_chat.id}</code>\n"
        f"<b>Event Stamp:</b> <code>{current_time}</code>"
    )

    if reason:
        if chat.type == chat.SUPERGROUP and chat.username:
            log_message += f'\n<b>Reason:</b> <a href="https://telegram.me/{chat.username}/{message.message_id}">{reason}</a>'
        else:
            log_message += f"\n<b>Reason:</b> <code>{reason}</code>"

    if EVENT_LOGS:
        try:
            log = bot.send_message(EVENT_LOGS, log_message, parse_mode=ParseMode.HTML)
        except BadRequest as excp:
            log = bot.send_message(
                EVENT_LOGS,
                log_message
                + "\n\nFormatting has been disabled due to an unexpected error.",
            )

    else:
        send_to_list(bot, INSPECTOR + REQUESTER, log_message, html=True)

    sql.gban_user(user_id, user_chat.username or user_chat.first_name, reason)

    chats = get_all_chats()

    gbanned_chats = 0

    for chat in chats:
        chat_id = chat.chat_id
        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            bot.ban_chat_member(chat_id, user_id)
            gbanned_chats += 1
            onIt.edit_text(f"User {user_chat.first_name} banned in {gbanned_chats} chats")
            time.sleep(0.1)

        except BadRequest as excp:
            if excp.message in GBAN_ERRORS:
                pass
            else:
                message.reply_text(f"Could not gban due to: {excp.message}")
                if EVENT_LOGS:
                    bot.send_message(
                        EVENT_LOGS,
                        f"Could not gban due to {excp.message}",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    send_to_list(
                        bot, INSPECTOR + REQUESTER, f"Could not gban due to: {excp.message}",
                    )
                sql.ungban_user(user_id)
                return
        except TelegramError:
            pass

    if EVENT_LOGS:
        log.edit_text(
            log_message + f"\n<b>Chats affected:</b> <code>{gbanned_chats}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        send_to_list(
            bot,
            INSPECTOR + REQUESTER,
            f"Gban complete! (User banned in <code>{gbanned_chats}</code> chats)",
            html=True,
        )

    end_time = time.time()
    gban_time = round((end_time - start_time), 2)

    if gban_time > 60:
        gban_time = round((gban_time / 60), 2)
        message.reply_text("Done! Gbanned.", parse_mode=ParseMode.HTML)
    else:
        message.reply_text("Done! Gbanned.", parse_mode=ParseMode.HTML)

    try:
        bot.send_message(
            user_id,
            "#EVENT"
            "You have been marked as Malicious and as such have been banned from any future groups we manage."
            f"\n<b>Reason:</b> <code>{html.escape(user.reason)}</code>"
            f"</b>Appeal Chat:</b> @AM_YTSUPPORT",
            parse_mode=ParseMode.HTML,
        )
    except:
        pass  # bot probably blocked by user



@support_plus
def ungban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return

    user_chat = bot.get_chat(user_id)
    if user_chat.type != "private":
        message.reply_text("That's not a user!")
        return

    if not sql.is_user_gbanned(user_id):
        message.reply_text("This user is not gbanned!")
        return

    ungb = message.reply_text(f"I'll give {user_chat.first_name} a second chance, globally.")

    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if chat.type != "private":
        chat_origin = f"<b>{html.escape(chat.title)} ({chat.id})</b>\n"
    else:
        chat_origin = f"<b>{chat.id}</b>\n"

    log_message = (
        f"#UNGBANNED\n"
        f"<b>Originated from:</b> <code>{chat_origin}</code>\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Unbanned User:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"<b>Unbanned User ID:</b> <code>{user_chat.id}</code>\n"
        f"<b>Event Stamp:</b> <code>{current_time}</code>"
    )

    if EVENT_LOGS:
        try:
            log = bot.send_message(EVENT_LOGS, log_message, parse_mode=ParseMode.HTML)
        except BadRequest as excp:
            log = bot.send_message(
                EVENT_LOGS,
                log_message
                + "\n\nFormatting has been disabled due to an unexpected error.",
            )
    else:
        send_to_list(bot, INSPECTOR + REQUESTER, log_message, html=True)

    chats = get_all_chats(user_id)
    ungbanned_chats = 0

    for chat in chats:
        chat_id = chat.chat_id

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status == "kicked":
                bot.unban_chat_member(chat_id, user_id)
                ungbanned_chats += 1
                ungb.edit_text(f"User {user_chat.first_name} is Unbaned in {ungbanned_chats} Chats")

        except BadRequest as excp:
            if excp.message in UNGBAN_ERRORS:
                pass
            else:
                message.reply_text(f"Could not un-gban due to: {excp.message}")
                if EVENT_LOGS:
                    bot.send_message(
                        EVENT_LOGS,
                        f"Could not un-gban due to: {excp.message}",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    bot.send_message(
                        OWNER_ID, f"Could not un-gban due to: {excp.message}",
                    )
                return
        except TelegramError:
            pass

    sql.ungban_user(user_id)

    if EVENT_LOGS:
        log.edit_text(
            log_message + f"\n<b>Chats affected:</b> {ungbanned_chats}",
            parse_mode=ParseMode.HTML,
        )
    else:
        send_to_list(bot, INSPECTOR + REQUESTER, "un-gban complete!")

    end_time = time.time()
    ungban_time = round((end_time - start_time), 2)

    if ungban_time > 60:
        ungban_time = round((ungban_time / 60), 2)
        message.reply_text(f"Person has been un-gbanned. Took {ungban_time} min")
    else:
        message.reply_text(f"Person has been un-gbanned. Took {ungban_time} sec")



@support_plus
def gbanlist(update: Update, context: CallbackContext):
    banned_users = sql.get_gban_list()

    if not banned_users:
        update.effective_message.reply_text(
            "There aren't any gbanned users! You're kinder than I expected...",
        )
        return
    
    data = []
    for user in banned_users:
        a = {'user_id': user["user_id"], 'reason': user["reason"] or ""}
        data.append(a)
    # print(data)
    with BytesIO(str.encode(json.dumps(data))) as output:
        output.name = "gbanlist.json"
        update.effective_message.reply_document(
            document=output,
            filename="gbanlist.json",
            caption="Here is the list of currently gbanned users.",
        )



def check_and_ban(update, user_id, should_message=True):


    if sql.is_user_gbanned(user_id):
        update.effective_chat.ban_member(user_id)
        if should_message:
            text = (
                f"<b>Alert</b>: this user is globally banned.\n"
                f"<code>*bans them from here*</code>.\n"
                f"<b>Appeal chat</b>: @AM_YTSUPPORT\n"
                f"<b>User ID</b>: <code>{user_id}</code>"
            )
            user = sql.get_gbanned_user(user_id)
            if user["reason"]:
                text += (
                    f"\n<b>Ban Reason:</b> <code>{html.escape(user['reason'])}</code>"
                )
            update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


@Ammsg(
    (Filters.all & Filters.chat_type.groups),
    can_disable=False,
    group=GBAN_ENFORCE_GROUP,
)
def enforce_gban(update: Update, context: CallbackContext):
    # Not using @restrict handler to avoid spamming - just ignore if cant gban.
    bot = context.bot
    try:
        restrict_permission = update.effective_chat.get_member(
            bot.id,
        ).can_restrict_members
    except Unauthorized:
        return
    if sql.does_chat_gban(update.effective_chat.id) and restrict_permission:
        user = update.effective_user
        update.effective_chat
        msg = update.effective_message

        if user and not is_user_admin(update, user.id):
            check_and_ban(update, user.id)
            return

        if msg.new_chat_members:
            new_members = update.effective_message.new_chat_members
            for mem in new_members:
                check_and_ban(update, mem.id)

        if msg.reply_to_message:
            user = msg.reply_to_message.from_user
            if user and not is_user_admin(update, user.id):
                check_and_ban(update, user.id, should_message=False)



@user_admin
def gbanstat(update: Update, context: CallbackContext):
    args = context.args
    if len(args) > 0:
        if args[0].lower() in ["on", "yes"]:
            sql.enable_gbans(update.effective_chat.id)
            update.effective_message.reply_text(
                "Antispam is now enabled ✅\n"
                "I am now protecting your group from potential remote threats!",
            )
        elif args[0].lower() in ["off", "no"]:
            sql.disable_gbans(update.effective_chat.id)
            update.effective_message.reply_text(
                "Antispam is now disabled ❌",
            )
    else:
        update.effective_message.reply_text(
            "Give me some arguments to choose a setting! on/off, yes/no!\n\n"
            "Your current setting is: {}\n"
            "When True, any gbans that happen will also happen in your group. "
            "When False, they won't, leaving you at the possible mercy of "
            "spammers.".format(sql.does_chat_gban(update.effective_chat.id)),
        )


def __stats__():
    return f"• {sql.num_gbanned_users()} gbanned users."


def __user_info__(user_id):
    is_gbanned = sql.is_user_gbanned(user_id)
    text = "Malicious: <b>{}</b>"
    if user_id in [777000, 1087968824]:
        return ""
    if user_id == dispatcher.bot.id:
        return ""
    if int(user_id) in INSPECTOR + REQUESTER:
        return ""
    if is_gbanned:
        text = text.format("Yes")
        user = sql.get_gbanned_user(user_id)
        if user.reason:
            text += f"\n<b>Reason:</b> <code>{html.escape(user.reason)}</code>"
        text += f"\n<b>Appeal Chat:</b> @AM_YTSUPPORT"
    else:
        text = text.format("???")
    return text


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return f"This chat is enforcing *gbans*: `{sql.does_chat_gban(chat_id)}`."


__help__ = """*Admins only*:
‣ `/antispam <on/off/yes/no>`: Toggles our antispam technology or returns your current settings.

Anti-Spam is used by bot developers to ban spammers across all groups. This helps protect you and your groups by removing spam flooders as quickly as possible.
*Note:* Users can appeal gbans or report spammers at `@Am_Support`."""

GBAN_HANDLER = CommandHandler("gban", gban, run_async=True)
SCAN_HANDLER = CommandHandler("scan", scan, run_async=True)

CALLBACK_QUERY_HANDLER = CallbackQueryHandler(agban, pattern=r"a_gban", run_async=True)
CASE_CALLBACK_QUERY_HANDLER = CallbackQueryHandler(closecase, pattern=r"close_case", run_async=True)

UNGBAN_HANDLER = CommandHandler("ungban", ungban, run_async=True)
GBAN_LIST = CommandHandler("gbanlist", gbanlist, run_async=True)

GBAN_STATUS = CommandHandler("antispam", gbanstat, filters=Filters.chat_type.group, run_async=True)

GBAN_ENFORCER = MessageHandler(Filters.all & Filters.chat_type.group, enforce_gban, run_async=True)

dispatcher.add_handler(GBAN_HANDLER)
dispatcher.add_handler(SCAN_HANDLER)
dispatcher.add_handler(CALLBACK_QUERY_HANDLER)
dispatcher.add_handler(CASE_CALLBACK_QUERY_HANDLER)
dispatcher.add_handler(UNGBAN_HANDLER)
dispatcher.add_handler(GBAN_LIST)
dispatcher.add_handler(GBAN_STATUS)

__mod_name__ = "Anti-Spam"
__handlers__ = [GBAN_HANDLER, UNGBAN_HANDLER, GBAN_LIST, GBAN_STATUS]

if STRICT_GBAN:  # enforce GBANS if this is set
    dispatcher.add_handler(GBAN_ENFORCER, GBAN_ENFORCE_GROUP)
    __handlers__.append((GBAN_ENFORCER, GBAN_ENFORCE_GROUP))
