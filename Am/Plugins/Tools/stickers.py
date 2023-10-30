import os
import math
from io import BytesIO
from cloudscraper import CloudScraper
import urllib.request as urllib
from urllib.parse import quote as urlquote

from Am.Functions.convert import convert_gif
from PIL import Image
from html import escape
from bs4 import BeautifulSoup

from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram import TelegramError
from telegram.ext import run_async, CallbackContext, CallbackQueryHandler
from telegram.utils.helpers import mention_html

from Am import dispatcher, REDIS, LOGGER
from Am.Plugins.disable import DisableAbleCommandHandler

combot_stickers_url = "https://combot.org/telegram/stickers?q="

scraper = CloudScraper()
def get_cbs_data(query, page, user_id):
    # returns (text, buttons)
    text = scraper.get(f'{combot_stickers_url}{urlquote(query)}&page={page}').text
    soup = BeautifulSoup(text, 'lxml')
    div = soup.find('div', class_='page__container')
    packs = div.find_all('a', class_='sticker-pack__btn')
    titles = div.find_all('div', 'sticker-pack__title')
    has_prev_page = has_next_page = None
    highlighted_page = div.find('a', class_='pagination__link is-active')
    if highlighted_page is not None and user_id is not None:
        highlighted_page = highlighted_page.parent
        has_prev_page = highlighted_page.previous_sibling.previous_sibling is not None
        has_next_page = highlighted_page.next_sibling.next_sibling is not None
    buttons = []
    if has_prev_page:
        buttons.append(InlineKeyboardButton(text='⬅️', callback_data=f'cbs_{page - 1}_{user_id}'))
    if has_next_page:
        buttons.append(InlineKeyboardButton(text='➡️', callback_data=f'cbs_{page + 1}_{user_id}'))
    buttons = InlineKeyboardMarkup([buttons]) if buttons else None
    text = f'Stickers for <code>{escape(query)}</code>:\nPage: {page}'
    if packs and titles:
        for pack, title in zip(packs, titles):
            link = pack['href']
            text += f"\n• <a href='{link}'>{escape(title.get_text())}</a>"
    elif page == 1:
        text = 'No results found, try a different term'
    else:
        text += "\n\nInterestingly, there's nothing here."
    return text, buttons


def cb_sticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    query = ' '.join(msg.text.split()[1:])
    if not query:
        msg.reply_text("Provide some term to search for a sticker pack.")
        return
    if len(query) > 50:
        msg.reply_text("Provide a search query under 50 characters")
        return
    if msg.from_user:
        user_id = msg.from_user.id
    else:
        user_id = None
    text, buttons = get_cbs_data(query, 1, user_id)
    msg.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=buttons)


def cbs_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    _, page, user_id = query.data.split('_', 2)
    if int(user_id) != query.from_user.id:
        query.answer('Not for you', cache_time=60 * 60)
        return
    search_query = query.message.text.split(
        '\n', 1)[0].split(maxsplit=2)[2][: -1]
    text, buttons = get_cbs_data(search_query, int(page), query.from_user.id)
    query.edit_message_text(
        text, parse_mode=ParseMode.HTML, reply_markup=buttons)
    query.answer()


def getsticker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message
    chat_id = update.effective_chat.id
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        with BytesIO() as file:
            file.name = 'sticker.png'
            new_file = bot.get_file(file_id)
            new_file.download(out=file)
            file.seek(0)
            bot.send_document(chat_id, document=file)
    else:
        update.effective_message.reply_text(
            "Please reply to a sticker for me to upload its PNG.",
        )


def kang(update, context):
    msg = update.effective_message
    user = update.effective_user
    args = context.args
    packnum = 0
    packname = "a" + str(user.id) + "_by_" + context.bot.username
    packname_found = 0
    max_stickers = 120

    while packname_found == 0:
        try:
            stickerset = context.bot.get_sticker_set(packname)
            if len(stickerset.stickers) >= max_stickers:
                packnum += 1
                packname = (
                    "a"
                    + str(packnum)
                    + "_"
                    + str(user.id)
                    + "_by_"
                    + context.bot.username
                )
            else:
                packname_found = 1
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                packname_found = 1

    kangsticker = "kangsticker.png"
    is_animated = False
    is_video = False
    # convert gif method
    is_gif = False
    file_id = ""

    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            if msg.reply_to_message.sticker.is_animated:
                is_animated = True
            elif msg.reply_to_message.sticker.is_video:
                is_video = True
            file_id = msg.reply_to_message.sticker.file_id
        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif (
            msg.reply_to_message.document
            and not msg.reply_to_message.document.mime_type == "video/mp4"
        ):
            file_id = msg.reply_to_message.document.file_id
        elif msg.reply_to_message.animation:
            file_id = msg.reply_to_message.animation.file_id
            is_gif = True
        else:
            msg.reply_text("Yea, I can't kang that.")
        kang_file = context.bot.get_file(file_id)
        if not is_animated and not (is_video or is_gif):
            kang_file.download("kangsticker.png")
        elif is_animated:
            kang_file.download("kangsticker.tgs")
        elif is_video and not is_gif:
            kang_file.download("kangsticker.webm")
        elif is_gif:
            kang_file.download("kang.mp4")
            convert_gif("kang.mp4")

        if args:
            sticker_emoji = str(args[0])
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji
        else:
            sticker_emoji = "😊"

        adding_process = msg.reply_text(
            "<b>Please wait...For a Moment</b>",
            parse_mode=ParseMode.HTML,
        )

        if not is_animated and not (is_video or is_gif):
            try:
                im = Image.open(kangsticker)
                maxsize = (512, 512)
                if (im.width and im.height) < 512:
                    size1 = im.width
                    size2 = im.height
                    if im.width > im.height:
                        scale = 512 / size1
                        size1new = 512
                        size2new = size2 * scale
                    else:
                        scale = 512 / size2
                        size1new = size1 * scale
                        size2new = 512
                    size1new = math.floor(size1new)
                    size2new = math.floor(size2new)
                    sizenew = (size1new, size2new)
                    im = im.resize(sizenew)
                else:
                    im.thumbnail(maxsize)
                if not msg.reply_to_message.sticker:
                    im.save(kangsticker, "PNG")
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    png_sticker=open("kangsticker.png", "rb"),
                    emojis=sticker_emoji,
                )
                edited_keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="View Pack", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                )
                adding_process.edit_text(
                    f"<b>Your sticker has been added!</b>"
                    f"\nEmoji is: {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )

            except OSError as e:

                print(e)
                return

            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        png_sticker=open("kangsticker.png", "rb"),
                    )
                    adding_process.delete()
                elif e.message == "Sticker_png_dimensions":
                    im.save(kangsticker, "PNG")
                    adding_process = msg.reply_text(
                        "<b>Please wait...For a Moment</b>",
                        parse_mode=ParseMode.HTML,
                    )
                    context.bot.add_sticker_to_set(
                        user_id=user.id,
                        name=packname,
                        png_sticker=open("kangsticker.png", "rb"),
                        emojis=sticker_emoji,
                    )
                    edited_keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="View Pack", url=f"t.me/addstickers/{packname}"
                                )
                            ]
                        ]
                    )
                    adding_process.edit_text(
                        f"<b>Your sticker has been added!</b>"
                        f"\nEmoji is: {sticker_emoji}",
                        reply_markup=edited_keyboard,
                        parse_mode=ParseMode.HTML,
                    )
                elif e.message == "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")
                elif e.message == "Stickers_too_much":
                    msg.reply_text(
                        "Max packsize reached.Press F to pay respecc.")
                elif e.message == "Internal Server Error: sticker set not found (500)":
                    edited_keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="View Pack", url=f"t.me/addstickers/{packname}"
                                )
                            ]
                        ]
                    )
                    msg.reply_text(
                        f"<b>Your sticker has been added!</b>"
                        f"\nEmoji is: {sticker_emoji}",
                        reply_markup=edited_keyboard,
                        parse_mode=ParseMode.HTML,
                    )
                print(e)

        elif is_animated:
            packname = "animated" + \
                str(user.id) + "_by_" + context.bot.username
            packname_found = 0
            max_stickers = 50
            while packname_found == 0:
                try:
                    stickerset = context.bot.get_sticker_set(packname)
                    if len(stickerset.stickers) >= max_stickers:
                        packnum += 1
                        packname = (
                            "animated"
                            + str(packnum)
                            + "_"
                            + str(user.id)
                            + "_by_"
                            + context.bot.username
                        )
                    else:
                        packname_found = 1
                except TelegramError as e:
                    if e.message == "Stickerset_invalid":
                        packname_found = 1
            try:
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    tgs_sticker=open("kangsticker.tgs", "rb"),
                    emojis=sticker_emoji,
                )
                edited_keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="View Pack", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                )
                adding_process.edit_text(
                    f"<b>Your stickers has been added!</b>"
                    f"\nEmoji is: {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )
            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        tgs_sticker=open("kangsticker.tgs", "rb"),
                    )
                    adding_process.delete()
                elif e.message == "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")
                elif e.message == "Internal Server Error: sticker set not found (500)":
                    edited_keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="View Pack", url=f"t.me/addstickers/{packname}"
                                )
                            ]
                        ]
                    )
                    adding_process.edit_text(
                        f"<b>Your sticker has been added!</b>"
                        f"\n Emoji is: {sticker_emoji}",
                        reply_markup=edited_keyboard,
                        parse_mode=ParseMode.HTML,
                    )
                print(e)

        elif is_video or is_gif:
            packname = "video" + str(user.id) + \
                "_by_" + context.bot.username
            packname_found = 0
            max_stickers = 50
            while packname_found == 0:
                try:
                    stickerset = context.bot.get_sticker_set(packname)
                    if len(stickerset.stickers) >= max_stickers:
                        packnum += 1
                        packname = (
                            "video"
                            + str(packnum)
                            + "_"
                            + str(user.id)
                            + "_by_"
                            + context.bot.username
                        )
                    else:
                        packname_found = 1
                except TelegramError as e:
                    if e.message == "Stickerset_invalid":
                        packname_found = 1
            try:
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    webm_sticker=open("kangsticker.webm", "rb"),
                    emojis=sticker_emoji,
                )
                edited_keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="View Pack", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                )
                adding_process.edit_text(
                    f"<b>Your sticker has been added!</b>"
                    f"\nEmoji is: {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )
            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        webm_sticker=open("kangsticker.webm", "rb"),
                    )
                    adding_process.delete()
                elif e.message == "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")
                elif e.message == "Internal Server Error: sticker set not found (500)":
                    edited_keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="View Pack", url=f"t.me/addstickers/{packname}"
                                )
                            ]
                        ]
                    )
                    adding_process.edit_text(
                        f"<b>Your sticker has been added!</b>"
                        f"\nEmoji is: {sticker_emoji}",
                        reply_markup=edited_keyboard,
                        parse_mode=ParseMode.HTML,
                    )
                print(e)

    elif args:
        try:
            try:
                urlemoji = msg.text.split(" ")
                png_sticker = urlemoji[1]
                sticker_emoji = urlemoji[2]
            except IndexError:
                sticker_emoji = "👌"
            urllib.urlretrieve(png_sticker, kangsticker)
            im = Image.open(kangsticker)
            maxsize = (512, 512)
            if (im.width and im.height) < 512:
                size1 = im.width
                size2 = im.height
                if im.width > im.height:
                    scale = 512 / size1
                    size1new = 512
                    size2new = size2 * scale
                else:
                    scale = 512 / size2
                    size1new = size1 * scale
                    size2new = 512
                size1new = math.floor(size1new)
                size2new = math.floor(size2new)
                sizenew = (size1new, size2new)
                im = im.resize(sizenew)
            else:
                im.thumbnail(maxsize)
            im.save(kangsticker, "PNG")
            msg.reply_photo(photo=open("kangsticker.png", "rb"))
            context.bot.add_sticker_to_set(
                user_id=user.id,
                name=packname,
                png_sticker=open("kangsticker.png", "rb"),
                emojis=sticker_emoji,
            )
            edited_keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="View Pack", url=f"t.me/addstickers/{packname}"
                        )
                    ]
                ]
            )
            adding_process.edit_text(
                f"<b>Your sticker has been added!</b>"
                f"\nEmoji is: {sticker_emoji}",
                reply_markup=edited_keyboard,
                parse_mode=ParseMode.HTML,
            )
        except OSError as e:
            msg.reply_text("I can only kang images m8.")
            print(e)
            return
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                makepack_internal(
                    update,
                    context,
                    msg,
                    user,
                    sticker_emoji,
                    packname,
                    packnum,
                    png_sticker=open("kangsticker.png", "rb"),
                )
                adding_process.delete()
            elif e.message == "Sticker_png_dimensions":
                im.save(kangsticker, "png")
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    png_sticker=open("kangsticker.png", "rb"),
                    emojis=sticker_emoji,
                )
                edited_keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="View Pack", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                )
                adding_process.edit_text(
                    f"<b>Your sticker has been added!</b>"
                    f"\nEmoji is: {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )
            elif e.message == "Invalid sticker emojis":
                msg.reply_text("Invalid emoji(s).")
            elif e.message == "Stickers_too_much":
                msg.reply_text(
                    "Max packsize reached.Press F to pay respect.")
            elif e.message == "Internal Server Error: sticker set not found (500)":
                msg.reply_text(
                    f"<b>Your sticker has been added!</b>"
                    f"\nEmoji is: {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )
            print(e)
    else:
        packs_text = "*Please reply to a sticker, or image to kang it! *\n"
        if packnum > 0:
            firstpackname = "a" + str(user.id) + \
                "_by_" + context.bot.username
            for i in range(0, packnum + 1):
                if i == 0:
                    packs = f"t.me/addstickers/{firstpackname}"
                else:
                    packs = f"t.me/addstickers/{packname}"
        else:
            packs = f"t.me/addstickers/{packname}"

        edited_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Sticker Pack", url=f"{packs}"),
                ],
            ]
        )
        msg.reply_text(
            packs_text, reply_markup=edited_keyboard, parse_mode=ParseMode.MARKDOWN
        )
    try:
        if os.path.isfile("kangsticker.png"):
            os.remove("kangsticker.png")
        elif os.path.isfile("kangsticker.tgs"):
            os.remove("kangsticker.tgs")
        elif os.path.isfile("kangsticker.webm"):
            os.remove("kangsticker.webm")
        elif os.path.isfile("kang.mp4"):
            os.remove("kang.mp4")
    except:
        pass


def makepack_internal(
    update,
    context,
    msg,
    user,
    emoji,
    packname,
    packnum,
    png_sticker=None,
    tgs_sticker=None,
    webm_sticker=None,
):
    name = user.first_name
    name = name[:50]
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            text="View Pack", url=f"t.me/addstickers/{packname}")]]
    )
    try:
        extra_version = ""
        if packnum > 0:
            extra_version = " " + str(packnum)
        if png_sticker:
            sticker_pack_name = (
                f"{name}'s sticker pack (@{context.bot.username})" +
                extra_version
            )
            success = context.bot.create_new_sticker_set(
                user.id,
                packname,
                sticker_pack_name,
                png_sticker=png_sticker,
                emojis=emoji,
            )
        if tgs_sticker:
            sticker_pack_name = (
                f"{name}'s animated pack (@{context.bot.username})" +
                extra_version
            )
            success = context.bot.create_new_sticker_set(
                user.id,
                packname,
                sticker_pack_name,
                tgs_sticker=tgs_sticker,
                emojis=emoji,
            )
        if webm_sticker:
            sticker_pack_name = (
                f"{name}'s video pack (@{context.bot.username})" +
                extra_version
            )
            success = context.bot.create_new_sticker_set(
                user.id,
                packname,
                sticker_pack_name,
                webm_sticker=webm_sticker,
                emojis=emoji,
            )

    except TelegramError as e:
        print(e)
        if e.message == "Sticker set name is already occupied":
            msg.reply_text(
                "<b>Your Sticker Pack is already created! </b>"
                "\n\nYou can now reply to images, stickers and animated sticker with /steal to add them to your pack"
                "\n\n<b>Send /stickers to find any sticker pack.</b>",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )
        elif e.message == "Peer_id_invalid" or "bot was blocked by the user":
            msg.reply_text(
                f"{context.bot.first_name} was blocked by you.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Unblock", url=f"t.me/{context.bot.username}"
                            )
                        ]
                    ]
                ),
            )
        elif e.message == "Internal Server Error: created sticker set not found (500)":
            msg.reply_text(
                "<b>Your Sticker Pack has been created! </b>"
                "\n\nYou can now reply to images, stickers and animated sticker with /steal to add them to your pack"
                "\n\n<b>Send /stickers to find sticker pack.</b>",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )
        return

    if success:
        msg.reply_text(
            "<b>Your Sticker Pack has been created! </b>"
            "\n\nYou can now reply to images, stickers and animated sticker with /steal to add them to your pack"
            "\n\n<b>Send /stickers to find sticker pack.</b>",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
    else:
        msg.reply_text(
            "Failed to create sticker pack.Possibly due to blek mejik.")


def getsticker(update, context):
    msg = update.effective_message
    chat_id = update.effective_chat.id
    if msg.reply_to_message and msg.reply_to_message.sticker:
        context.bot.sendChatAction(chat_id, "typing")
        update.effective_message.reply_text(
            "Hello"
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", Please check the file you requested below."
            "\nPlease use this feature wisely! ",
            parse_mode=ParseMode.HTML,
        )
        context.bot.sendChatAction(chat_id, "upload_document")
        file_id = msg.reply_to_message.sticker.file_id
        newFile = context.bot.get_file(file_id)
        newFile.download("sticker.png")
        context.bot.sendDocument(
            chat_id, document=open("sticker.png", "rb"))
        context.bot.sendChatAction(chat_id, "upload_photo")
        context.bot.send_photo(chat_id, photo=open("sticker.png", "rb"))

    else:
        context.bot.sendChatAction(chat_id, "typing")
        update.effective_message.reply_text(
            "Hello"
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", Please reply to sticker message to get sticker image",
            parse_mode=ParseMode.HTML,
        )


def stickerid(update, context):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", The sticker id you are replying is : \n <code>"
            + escape(msg.reply_to_message.sticker.file_id)
            + "</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", Please reply to sticker message to get id sticker",
            parse_mode=ParseMode.HTML,
        )


def delsticker(update, context):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        context.bot.delete_sticker_from_set(file_id)
        msg.reply_text(
            "Deleted! "
        )
    else:
        update.effective_message.reply_text(
            "Please reply to sticker message to del sticker"
        )


def add_fvrtsticker(update, context):
    bot = context.bot
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = context.args
    query = " ".join(args)
    if message.reply_to_message and message.reply_to_message.sticker:
        get_s_name = message.reply_to_message.sticker.set_name
        if not query:
            get_s_name_title = get_s_name
        else:
            get_s_name_title = query
        if get_s_name is None:
            message.reply_text(
                "Sticker is invalid! "
            )
        sticker_url = f"https: //t.me/addstickers/{get_s_name}"
        sticker_m = "<a href='{}'>{}</a>".format(
            sticker_url, get_s_name_title)
        check_pack = REDIS.hexists(
            f'fvrt_stickers2_{user.id}', get_s_name_title)
        if check_pack == False:
            REDIS.hset(f'fvrt_stickers2_{user.id}',
                        get_s_name_title, sticker_m)
            message.reply_text(
                f"<code>{sticker_m}</code> has been succesfully added into your favorite sticker packs list! ",
                parse_mode=ParseMode.HTML
            )
        else:
            message.reply_text(
                f"<code>{sticker_m}</code> is already exist in your favorite sticker packs list! ",
                parse_mode=ParseMode.HTML
            )

    else:
        message.reply_text(
            'Reply to any sticker! '
        )


def list_fvrtsticker(update, context):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    fvrt_stickers_list = REDIS.hvals(f'fvrt_stickers2_{user.id}')
    fvrt_stickers_list.sort()
    fvrt_stickers_list = "\n ".join(fvrt_stickers_list)
    if fvrt_stickers_list:
        message.reply_text(
            "{}'s favorite sticker packs: \n {}".format(user.first_name,
                                                         fvrt_stickers_list),
            parse_mode=ParseMode.HTML
        )
    else:
        message.reply_text(
            "You haven't added any sticker yet."
        )


def remove_fvrtsticker(update, context):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = context.args
    del_stick = " ".join(args)
    if not del_stick:
        message.reply_text(
            "Please give a your favorite sticker pack name to remove from your list.")
        return
    del_check = REDIS.hexists(f'fvrt_stickers2_{user.id}', del_stick)
    if not del_check == False:
        REDIS.hdel(f'fvrt_stickers2_{user.id}', del_stick)
        message.reply_text(
            f"<code>{del_stick}</code> has been succesfully deleted from your list.",
            parse_mode=ParseMode.HTML
        )
    else:
        message.reply_text(
            f"<code>{del_stick}</code> doesn't exist in your favorite sticker pack list.",
            parse_mode=ParseMode.HTML
        )


__help__ = """Stickers made easy with stickers module!

‣ `/stickers`: Find stickers for given term on combot sticker catalogue
‣ `/addsticker`, `/kang`, or `/steal`: Reply to a sticker to add it to your pack.
‣ `/delsticker`: Reply to a sticker in your pack to delete it.
‣ `/stickerid`: Reply to a sticker to get its file ID.
‣ `/getsticker`: Reply to a sticker to upload its raw PNG file.
‣ `/addfsticker`, `/afs <custom name>`: Reply to a sticker to add it to your favorite pack list with a custom name.
‣ `/myfsticker`, `/mfs`: Get a list of your favorite sticker packs.
‣ `/removefsticker`, `/rfs <custom name>`: Reply to a sticker to remove it from your favorite pack list.
‣ `/mirror`: Reply to any sticker to create a mirror image of it.
‣ `/bw`: Reply to a sticker to convert it to black and white.
‣ `/rotate 40`: Reply to a sticker to rotate it by the specified number of degrees.
‣ `/flip`: Reply to a sticker to flip it horizontally.

*Example:* `/addfsticker my cool pack`

"""
__mod_name__ = "Stickers"

KANG_HANDLER = DisableAbleCommandHandler(
    ["addsticker", "kang", "steal"], kang, pass_args=True, run_async=True)
DEL_HANDLER = DisableAbleCommandHandler(
    "delsticker", delsticker, run_async=True)
STICKERID_HANDLER = DisableAbleCommandHandler(
    "stickerid", stickerid, run_async=True)
ADD_FSTICKER_HANDLER = DisableAbleCommandHandler(
    ["addfsticker", "afs"], add_fvrtsticker, pass_args=True, run_async=True)
REMOVE_FSTICKER_HANDLER = DisableAbleCommandHandler(
    ["removefsticker", "rfs"], remove_fvrtsticker, pass_args=True, run_async=True)
MY_FSTICKERS_HANDLER = DisableAbleCommandHandler(
    ["myfsticker", "mfs"], list_fvrtsticker, run_async=True)
GETSTICKER_HANDLER = DisableAbleCommandHandler(
    "getsticker", getsticker, run_async=True)
STICKERS_HANDLER = DisableAbleCommandHandler(
    "stickers", cb_sticker, run_async=True)
CBSCALLBACK_HANDLER = CallbackQueryHandler(
    cbs_callback, pattern='cbs_', run_async=True)
dispatcher.add_handler(KANG_HANDLER)
dispatcher.add_handler(DEL_HANDLER)
dispatcher.add_handler(STICKERID_HANDLER)
dispatcher.add_handler(ADD_FSTICKER_HANDLER)
dispatcher.add_handler(REMOVE_FSTICKER_HANDLER)
dispatcher.add_handler(MY_FSTICKERS_HANDLER)
dispatcher.add_handler(GETSTICKER_HANDLER)
dispatcher.add_handler(STICKERS_HANDLER)
dispatcher.add_handler(CBSCALLBACK_HANDLER)
