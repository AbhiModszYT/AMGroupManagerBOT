import html
from Am.Handlers.validation import (
    bot_admin,
    can_promote,
    connection_status,
    user_admin,
    ADMIN_CACHE,
)
from Am.Plugins.disable import DisableAbleCommandHandler
from Am import dispatcher, INSPECTOR
from Am.Handlers.extraction import extract_user
from telegram.ext import CallbackContext, CallbackQueryHandler, Filters, run_async
import Am.Database.mod_sql as sql
from Am.Plugins.Admin.log_channel import loggable
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.utils.helpers import mention_html
from telegram.error import BadRequest


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def mod(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    promoter = chat.get_member(user.id)

    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in INSPECTOR
    ):
        message.reply_text("You don't have the necessary rights to make any user moderator!")
        return

    if sql.is_modd(message.chat_id, user_id):
        message.reply_text(
            f"[{member.user['first_name']}](tg://user?id={member.user['id']}) is already moderator in {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.mod(message.chat_id, user_id)
    message.reply_text(
        f"[{member.user['first_name']}](tg://user?id={member.user['id']}) has been moderator in {chat_title}! They can mute, warn and ban any person.",
        parse_mode=ParseMode.MARKDOWN,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#MODERATOR\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@loggable
@user_admin
def dismod(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text("This user is an admin, they can't be unmod.")
        return ""
    if not sql.is_modd(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} isn't moderator yet!")
        return ""
    sql.dismod(message.chat_id, user_id)
    message.reply_text(
        f"{member.user['first_name']} is no longer moderator in {chat_title}."
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNMODERATOR\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@user_admin
def modd(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "The following users are moderators.\n"
    modd_users = sql.list_modd(message.chat_id)
    for i in modd_users:
        member = chat.get_member(int(i.user_id))
        msg += f"- `{i.user_id}`: {member.user['first_name']}\n"
    if msg.endswith("modd.\n"):
        message.reply_text(f"No users are moderator in {chat_title}.")
        return ""
    else:
        message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@user_admin
def modcheck(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    member = chat.get_member(int(user_id))
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    if sql.is_modd(message.chat_id, user_id):
        message.reply_text(
            f"{member.user['first_name']} is an moderator user. can ban, mute, and warn group members."
        )
    else:
        message.reply_text(
            f"{member.user['first_name']} is not an moderator user. They are affected by normal commands."
        )


def unmodall(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in INSPECTOR:
        update.effective_message.reply_text(
            "Only the chat owner can unmod all users at once."
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Unmod all users", callback_data="unmodall_user"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Cancel", callback_data="unmodall_cancel"
                    )
                ],
            ]
        )
        update.effective_message.reply_text(
            f"Are you sure you would like to UNMOD ALL users in {chat.title}? This action cannot be undone.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


def unmodall_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "unmodall_user":
        if member.status == "creator" or query.from_user.id in INSPECTOR:
            users = []
            modd_users = sql.list_modd(chat.id)
            for i in modd_users:
                users.append(int(i.user_id))
            for user_id in users:
                sql.dismod(chat.id, user_id)

        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")
            return 
        if member.status == "member":
            query.answer("You need to be admin to do this.")
    elif query.data == "unmodall_cancel":
        if member.status == "creator" or query.from_user.id in INSPECTOR:
            message.edit_text("Removing of all moderator users has been cancelled.")
            return ""
        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")
        if member.status == "member":
            query.answer("You need to be admin to do this.")


__help__ = """
Sometimes, you don't trust but want to make user manager of your group then you can make him/her moderator.
Maybe not enough to make them admin, but you might be ok with ban, mute, and warn not.
That's what modcheck are for - mod of trustworthy users to allow to manage your group.
*Admin commands:*
- `/modcheck`*:* Check a user's modcheck status in this chat.
- `/mod`*:* mod of a user can ban, mute, and warn.
- `/unmod`*:* Unmod of a user. They will now can't ban, mute and warn anAm.
- `/modlist`*:* List all mod users.
- `/unmodall`*:* Unmod *ALL* users in a chat. This cannot be undone.
"""

MOD = DisableAbleCommandHandler("mod", mod, run_async=True)
DISMOD = DisableAbleCommandHandler("unmod", dismod, run_async=True)
MODD = DisableAbleCommandHandler("modlist", modd, run_async=True)
MODCHECK = DisableAbleCommandHandler("modcheck", modcheck, run_async=True)
UNMODALL = DisableAbleCommandHandler("unmodall", unmodall, run_async=True)
UNMODALL_BTN = CallbackQueryHandler(unmodall_btn, pattern=r"unmodall_.*", run_async=True)

dispatcher.add_handler(MOD)
dispatcher.add_handler(DISMOD)
dispatcher.add_handler(MODD)
dispatcher.add_handler(MODCHECK)
dispatcher.add_handler(UNMODALL)
dispatcher.add_handler(UNMODALL_BTN)

__mod_name__ = "Moderator"
__command_list__ = ["mod", "unmod", "modd", "modecheck"]
__handlers__ = [MOD, DISMOD, MODD, MODCHECK]