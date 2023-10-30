import os
import cv2
import pilgram
import random
import openai
from PIL import Image
from io import BytesIO
from Am import dispatcher
from Am.Plugins.disable import DisableAbleCommandHandler
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, run_async

# Copyright - All Copyrights of this file is belong to kushal

def beautify(update: Update, context: CallbackContext):
   bot = context.bot
   message = update.effective_message
   dltmsg = message.reply_text('Making Your Image Beautiful...wait!')
   try:
        if message.reply_to_message and message.reply_to_message.photo:
                file_id = message.reply_to_message.photo[-1].file_id
                newFile = context.bot.get_file(file_id)
                newFile.download("getBeautifyfile.png")
                im = Image.open("getBeautifyfile.png")

                Filters = [
                        pilgram._1977,
                        pilgram.aden,
                        pilgram.brannan,
                        pilgram.brooklyn,
                        pilgram.clarendon,
                        pilgram.earlybird,
                        pilgram.gingham,
                        pilgram.hudson,
                        pilgram.inkwell,
                        pilgram.kelvin,
                        pilgram.lark,
                        pilgram.lofi,
                        pilgram.maven,
                        pilgram.mayfair,
                        pilgram.moon,
                        pilgram.nashville,
                        pilgram.perpetua,
                        pilgram.reyes,
                        pilgram.rise,
                        pilgram.slumber,
                        pilgram.stinson,
                        pilgram.toaster,
                        pilgram.valencia,
                        pilgram.walden,
                        pilgram.willow,
                        pilgram.xpro2,
                    ]

                randFilter = random.choice(Filters)
                fname = "beautifyImage.png"
                randFilter(im).save(fname)
                ofile = open(fname, "rb")

                message.reply_photo(
                        ofile,
                        caption="Made By @Am_Robot",
                        parse_mode=ParseMode.HTML,
                        
                    )

                dltmsg.delete()
                if os.path.exists(fname):
                    os.remove(fname)
                if os.path.exists("getBeautifyfile.png"):
                    os.remove("getBeautifyfile.png")

        else:
            update.effective_message.reply_text(
                "Please reply to an image to Beautify Image.",
            )

   except Exception as e:
      message.reply_text(f'Error Report @Am_Support, {e}')


def sketch(update: Update, context: CallbackContext):
    bot = context.bot
    chat_id = update.effective_chat.id
    message = update.effective_message
    try:
        if message.reply_to_message and message.reply_to_message.photo:
                file_id = message.reply_to_message.photo[-1].file_id
                newFile = context.bot.get_file(file_id)
                newFile.download("getSketchfile.png")
                #reading image
                image = cv2.imread("getSketchfile.png")
                #converting BGR image to grayscale
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                #image inversion
                inverted_image = 255 - gray_image

                blurred = cv2.GaussianBlur(inverted_image, (21, 21), 0)
                inverted_blurred = 255 - blurred
                pencil_sketch = cv2.divide(gray_image, inverted_blurred, scale=120.0)


                filename = 'my_sketch.png'
                cv2.imwrite(filename, pencil_sketch)
                ofile = open(filename, "rb")
                bot.send_photo(chat_id, ofile)
                if os.path.exists("getSketchfile.png"):
                    os.remove("getSketchfile.png")
                if os.path.exists(filename):
                    os.remove(filename)

        else:
            update.effective_message.reply_text(
                "Please reply to an image to make a sketch.",
            )

    except Exception as e:
      message.reply_text(f'Error Report @Am_Support, {e}')


# def imagine(update: Update, context: CallbackContext):
#     bot = context.bot
#     chat_id = update.effective_chat.id
#     message = update.effective_message
#     args = message.text.split(" ", 1)


#     if len(args) == 1:
#         message.reply_text('Please provide text with command! EXAMPLE: /imagine a cat with wings')
#         return
#     try:
#         openai.api_key = "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"
#         prompt = args[1]
#         response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
#         image_url = response["data"][0]["url"]
#         bot.send_photo(chat_id, photo=image_url)

#     except Exception as e:
#       message.reply_text(f'Error Report @Am_Support, {e}')


__mod_name__ = "Image"

SKETCH_HANDLER = DisableAbleCommandHandler("sketch", sketch, run_async=True)
BEAUTIFY_HANDLER = DisableAbleCommandHandler(["beautify", "btfy"], beautify, run_async=True)
# IMAGINE_HANDLER = DisableAbleCommandHandler(["imagine", "make"], imagine, run_async=True)
dispatcher.add_handler(BEAUTIFY_HANDLER)
dispatcher.add_handler(SKETCH_HANDLER)
# dispatcher.add_handler(IMAGINE_HANDLER)