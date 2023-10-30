from Am import telethn as client
from Am.events import register
from Am import LOGGER


if 1 == 1:

    name = "Profile Photos"

    @register(pattern="^/poto ?(.*)")
    async def potocmd(event):

        """Gets the profile photos of replied users, channels or chats"""
        id = "".join(event.raw_text.split(maxsplit=2)[1:])

        user = await event.get_reply_message()

        chat = event.input_chat

        if user:

            photos = await event.client.get_profile_photos(user.sender)

        else:

            photos = await event.client.get_profile_photos(chat)

        if id.strip() == "":

            try:

                await event.client.send_file(event.chat_id, photos)

            except Exception as a:

                photo = await event.client.download_profile_photo(chat)

                await client.send_file(event.chat_id, photo)

        else:

            try:

                id = int(id)

                if id <= 0:

                    await event.reply("`ID number you entered is invalid`")

                    return

            except:

                await event.reply("`Are you Comedy Me ?`")

                return

            if int(id) <= (len(photos)):

                send_photos = await event.client.download_media(photos[id - 1])

                await client.send_file(event.chat_id, send_photos)

            else:

                await event.reply("`No photo found  , now u Die`")

                return