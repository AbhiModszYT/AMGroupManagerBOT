import asyncio
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from Am import OWNER_ID, pbot as app
from Am.Database.users_sql import get_all_chats, get_all_users
from pyrogram.errors import FloodWait

AMBOT = 6204761408

@app.on_message(filters.command("promo"))
async def broadcast(client, message: Message):
    if message.from_user.id != OWNER_ID and message.from_user.id != AMBOT:
        await message.reply_text("You're not my owner.")
        return

    reply_msg = message.reply_to_message
    if reply_msg:
        text = reply_msg.text or ""
        caption = reply_msg.caption or ""
        chats = get_all_chats() or []
        users = get_all_users()
        failed = 0
        failed_user = 0
        sent = 0
        sent_user = 0
        start_message = await message.reply_text(text="Broadcast started...")
        if reply_msg.photo:
            photo = reply_msg.photo.file_id
            for chat in chats:
                try:
                    await app.send_photo(chat_id=int(chat.chat_id), photo=photo, caption=caption, reply_markup=reply_msg.reply_markup)
                    await asyncio.sleep(0.1)
                    sent += 1
                except FloodWait as e:
                    failed += 1
                except Exception as e:
                    failed +=1

            for user in users:
                try:
                    await app.send_photo(chat_id=int(user.user_id), photo=photo, caption=caption, reply_markup=reply_msg.reply_markup)
                    await asyncio.sleep(0.1)
                    sent_user += 1
                except FloodWait as e:
                    failed_user += 1
                except Exception as e:
                    failed_user +=1


            await start_message.edit_text(
        text=f"Broadcast complete.\nGroups Count: {sent}\n Users Count: {sent_user} \nGroups failed: {failed}.\nUsers failed: {failed_user}.",
    )
            return

        elif reply_msg.reply_markup:
            for chat in chats:
                try:
                    await app.send_message(chat_id=chat.chat_id, text=text, reply_markup=reply_msg.reply_markup)
                    await asyncio.sleep(0.1)
                    sent += 1
                except FloodWait as e:
                    failed += 1
                except Exception as e:
                    failed +=1

            for user in users:
                try:
                    await app.send_message(chat_id=user.user_id, text=text, reply_markup=reply_msg.reply_markup)
                    await asyncio.sleep(0.1)
                    sent_user += 1
                except FloodWait as e:
                    failed_user += 1
                except Exception as e:
                    failed_user +=1


            await start_message.edit_text(
        text=f"Broadcast complete.\nGroups Count: {sent}\n Users Count: {sent_user} \nGroups failed: {failed}.\nUsers failed: {failed_user}.",
    )
            return
        else:
            for chat in chats:
                try:
                    await app.send_message(
                        chat_id=int(chat.chat_id),
                        text=text,
                        disable_web_page_preview=False,
                    )
                    await asyncio.sleep(0.1)
                    sent += 1
                except FloodWait as e:
                    failed += 1
                except Exception as e:
                    failed +=1

            for user in users:
                try:
                    await app.send_message(
                        chat_id=int(user.user_id),
                        text=text,
                        disable_web_page_preview=False,
                    )
                    await asyncio.sleep(0.1)
                    sent_user += 1
                except FloodWait as e:
                    failed_user += 1
                except Exception as e:
                    failed_user +=1
            await start_message.edit_text(
        text=f"Broadcast complete.\nGroups Count: {sent}\n Users Count: {sent_user} \nGroups failed: {failed}.\nUsers failed: {failed_user}.",
    )
            return
        
                
    else:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.reply_text("Please provide some text to broadcast.")
            return

        text = args[1]

        keyboard = [
            [
                InlineKeyboardButton("Groups", callback_data="promogroups"),
                InlineKeyboardButton("Users", callback_data="promousers"),
            ],
            [
                InlineKeyboardButton("Broadcast to All", callback_data="promoall")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await message.reply_text(
            text=text,
            reply_markup=reply_markup,
            quote=False,
        )

@app.on_callback_query()
async def process_callback_data(client, callback_query: CallbackQuery):
    action = callback_query.data
    message = callback_query.message

    await callback_query.answer()

    to_group = False
    to_user = False

    if action == "promogroups":
        to_group = True
    elif action == "promousers":
        to_user = True
    elif action == "promoall":
        to_group = to_user = True
    else:
        return

    chats = get_all_chats() or []
    users = get_all_users()
    failed = 0
    failed_user = 0
    sent = 0
    sent_user = 0
    await callback_query.message.edit_text(text="Broadcast started...")
    text = message.text
    if to_group:
        for chat in chats:
            try:
                await app.send_message(
                    chat_id=int(chat.chat_id),
                    text=text,
                    disable_web_page_preview=False,
                )
                await asyncio.sleep(0.1)
                sent += 1
            except FloodWait as e:
                failed += 1
            except Exception as e:
                failed +=1

    if to_user:
        for user in users:
            try:
                await app.send_message(
                    chat_id=int(user.user_id),
                    text=text,
                    disable_web_page_preview=False,
                )
                await asyncio.sleep(0.1)
                sent_user += 1
            except FloodWait as e:
                failed_user += 1
            except Exception as e:
                failed_user +=1

    await callback_query.message.edit_text(
        text=f"Broadcast complete.\nGroups Count: {sent}\n Users Count: {sent_user} \nGroups failed: {failed}.\nUsers failed: {failed_user}.",
    )
