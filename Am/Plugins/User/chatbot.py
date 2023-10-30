import json
import re
import os
import html
import requests
import Am.Database.chatbot_sql as sql
import openai
import random


from time import sleep
from telegram import ParseMode
from Am import dispatcher, updater, SUPPORT_CHAT
from Am.Plugins.Admin.log_channel import gloggable
from telegram import (
    CallbackQuery,
    Chat,
    MessageEntity,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ParseMode,
    Update,
    Bot,
    User,
)

from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    DispatcherHandlerStop,
    Filters,
    MessageHandler,
    run_async,
)

from telegram.error import BadRequest, RetryAfter, Unauthorized

from Am.Handlers.filters import CustomFilters
from Am.Handlers.validation import user_admin, user_admin_no_reply
from Am.Handlers.alternate import typing_action
from telegram.utils.helpers import mention_html, mention_markdown, escape_markdown


@user_admin_no_reply
@gloggable
def Amrm(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        try:
            is_Am = sql.rem_Am(chat.id)
        except Exception as e:
            update.effective_message.edit_text(f"error occured: {e}")
            return

        if is_Am:
            is_Am = sql.rem_Am(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"AI_DISABLED\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "Chatbot disable by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )

    return ""


@user_admin_no_reply
@gloggable
def Amadd(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"add_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_Am = sql.set_Am(chat.id)
        if is_Am:
            try:
                is_Am = sql.set_Am(user_id)
            except Exception as e:
                update.effective_message.edit_text(f"error occured: {e}")
                return
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"AI_ENABLE\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "Chatbot enable by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )

    return ""


@user_admin
@gloggable
def Am(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.effective_message
    msg = f"Choose an option"
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="Enable", callback_data="add_chat({})")],
            [InlineKeyboardButton(text="Disable", callback_data="rm_chat({})")],
        ]
    )
    message.reply_text(
        msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


def Am_message(context: CallbackContext, message):
    reply_message = message.reply_to_message
    if message.text.lower() == "poppy":
        return True
    if message.chat.type == 'private':
        return True
    
    if reply_message:
        if reply_message.from_user.id == context.bot.get_me().id:
            return True
    else:
        return False


# Define the rules for different types of messages
rules = {
    'greeting': ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'howdy'],
    'compliment': ['beautiful', 'nice', 'lovely', 'stunning', 'gorgeous', 'amazing', 'wonderful'],
    'flirtation': ['hug', 'kiss', 'date', 'cuddle', 'snuggle', 'miss you', 'you\'re so cute', 'love'],
    'joke': ['haha', 'lol', 'funny', 'that\'s a good one', 'you crack me up', 'I can\'t stop laughing'],
    'small talk': ['how are you', 'what\'s up', 'what\'s new', 'how was your day', 'what are you doing', 'nice weather today'],
    'timepass': ['okay', 'cool', 'nice', 'alright', 'got it', 'thanks'],
    'unknown': ['I don\'t understand', 'can you clarify', 'what do you mean', 'sorry, I don\'t know', 'could you please rephrase that'],
    'abuse': ['fuck','motherfucker','bitch', 'pussy', 'dick', 'vagina','motherchod', 'gandu', 'bhosdike', 'chutiya', 'loda', 'bahanchod', 'chut', 'loda', 'behanchod', 'matherchod', 'randi', 'jhatu', 'jhat', 'lund', 'lawde', 'boobs' ]
    }



def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot
    # Check if the chat has enabled the chatbot
    is_Am_enabled = sql.is_Am(chat_id)
    if not is_Am_enabled:
        return
    # Set up OpenAI API key and models
    openai.api_key = "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"
    if message.text and not message.document:
        try:
            if not Am_message(context, message):
                return
            bot.send_chat_action(chat_id, action="typing")

            message_text = message.text.strip().lower()


            # Set a threshold to detect timepass messages
            threshold = 30
            small_threshold =  10

            prompt = message_text
            temperature = random.uniform(0.5, 1.0)


            # Check if the message is a timepass or a serious question
            if len(message_text) <= threshold:
                is_timepass = any(word in message_text for word in rules['timepass'])
                if is_timepass:
                    # Use Kora API to generate response
                    Amurl = requests.get("https://kora-api.vercel.app/chatbot/message=" + message_text)
                    Am = json.loads(Amurl.text)['reply']
                else:
                    for rule, words in rules.items():
                        if any(word in message_text for word in words):
                            # Use Kora API to generate response for certain rules
                            Amurl = requests.get("https://kora-api.vercel.app/chatbot/message=" + message_text)
                            Am = json.loads(Amurl.text)['reply']
                            break
                    else:
                        if len(message_text) <= small_threshold:
                            Am_url = f"https://kora-api.vercel.app/chatbot/message={message_text}"
                            Am = json.loads(requests.get(Am_url).text)['reply']
                        else:
                        # If none of the rules match, randomly choose between Kora and OpenAI API
                            if random.random() < 0.3:
                                Am_url = f"https://kora-api.vercel.app/chatbot/message={message_text}"
                                Am = json.loads(requests.get(Am_url).text)['reply']
                            else:
                                # Use OpenAI API to generate response for unknown intentions
                                response = openai.Completion.create(
                                    model="text-davinci-003",
                                    prompt=message_text,
                                    temperature=temperature,
                                    max_tokens=500,
                                    top_p=0,
                                    frequency_penalty=0,
                                    presence_penalty=0.6,
                                )
                                Am = response.choices[0].text
            else:
                # Use OpenAI API to generate response for serious questions
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=500,
                    top_p=0,
                    frequency_penalty=0,
                    presence_penalty=0.6,
                )
                Am = response.choices[0].text

            # Send the translated response to the user
            message.reply_text(Am)

        except Exception as e:
            # Log the error and send a message to the user that there was a problem
            context.bot.send_message(chat_id=chat_id, text=f"Sorry, I encountered an error: {str(e)}")


def list_all_chats(update: Update, context: CallbackContext):
    chats = sql.get_all_Am_chats()
    text = "<b>Am-Enabled Chats</b>\n"
    for chat in chats:
        try:
            x = context.bot.get_chat(int(*chat))
            name = x.title or x.first_name
            text += f"• <code>{name}</code>\n"
        except (BadRequest, Unauthorized):
            sql.rem_Am(*chat)
        except RetryAfter as e:
            sleep(e.retry_after)
    update.effective_message.reply_text(text, parse_mode="HTML")


__help__ = """We have highly artificial intelligence chatbot of telegram which provides you real and attractive experience of chatting.
*Admins only Commands*:
  ‣ `/Chatbot`*:* Shows chatbot control panel
  """

__mod_name__ = "Chatbot"


CHATBOTK_HANDLER = CommandHandler("ChatBot", Am, run_async=True)
ADD_CHAT_HANDLER = CallbackQueryHandler(Amadd, pattern=r"add_chat", run_async=True)
RM_CHAT_HANDLER = CallbackQueryHandler(Amrm, pattern=r"rm_chat", run_async=True)
CHATBOT_HANDLER = MessageHandler(
    Filters.text
    & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!") & ~Filters.regex(r"^\/")),
    chatbot,
    run_async=True,
)
LIST_ALL_CHATS_HANDLER = CommandHandler(
    "allchats", list_all_chats, filters=CustomFilters.dev_filter, run_async=True
)

dispatcher.add_handler(ADD_CHAT_HANDLER)
dispatcher.add_handler(CHATBOTK_HANDLER)
dispatcher.add_handler(RM_CHAT_HANDLER)
dispatcher.add_handler(LIST_ALL_CHATS_HANDLER)
dispatcher.add_handler(CHATBOT_HANDLER)

__handlers__ = [
    ADD_CHAT_HANDLER,
    CHATBOTK_HANDLER,
    RM_CHAT_HANDLER,
    LIST_ALL_CHATS_HANDLER,
    CHATBOT_HANDLER,
]
