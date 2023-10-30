from Am import pbot as app
from pyrogram import filters
import replicate
import base64
import requests
import json

import os
os.environ['REPLICATE_API_TOKEN'] = 'r8_CvDWPZN7Swzvy6H8Tl6qfHoJdrjq7Dd1tMO7X'


def get_ai_image(base64_image_string):
    headers = {
        "Connection": "keep-alive",
        "phone_gid": "2862114434",
        "Accept": "application/json, text/plain, */*",
        "User-Agent":
        "Mozilla/5.0 (Linux; Android 7.1.2; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 com.meitu.myxj/11270(android7.1.2)/lang:ru/isDeviceSupport64Bit:false MTWebView/4.8.5",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://titan-h5.meitu.com",
        "X-Requested-With": "com.meitu.meiyancamera",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://titan-h5.meitu.com/",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    params = {
        "api_key": "237d6363213c4751ba1775aba648517d",
        "api_secret": "b7b1c5865a83461ea5865da3ecc7c03d",
    }

    json_data = {
        "parameter": {
            "rsp_media_type": "url",
            "strength": 0.45,
            "guidance_scale": 7.5,
            "prng_seed": "-1",
            "num_inference_steps": "50",
            "extra_prompt": "",
            "extra_negative_prompt": "",
            "random_generation": "False",
            "type": "1",
            "type_generation": "True",
            "sensitive_words": "white_kimono",
        },
        "extra": {},
        "media_info_list": [
            {
                "media_data": base64_image_string,
                "media_profiles": {
                    "media_data_type": "jpg",
                },
            },
        ],
    }

    response = requests.post(
        "https://openapi.mtlab.meitu.com/v1/stable_diffusion_anime",
        params=params,
        headers=headers,
        json=json_data,
    )

    return json.loads(response.content)


def get_ai_text(base64_image_string, text):

    headers = {
        "Connection": "keep-alive",
        "phone_gid": "2862114434",
        "Accept": "application/json, text/plain, */*",
        "User-Agent":
        "Mozilla/5.0 (Linux; Android 7.1.2; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 com.meitu.myxj/11270(android7.1.2)/lang:ru/isDeviceSupport64Bit:false MTWebView/4.8.5",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://titan-h5.meitu.com",
        "X-Requested-With": "com.meitu.meiyancamera",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://titan-h5.meitu.com/",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    params = {
        "api_key": "237d6363213c4751ba1775aba648517d",
        "api_secret": "b7b1c5865a83461ea5865da3ecc7c03d",
    }

    json_data = {
        "parameter": {
            "rsp_media_type": "url",
            "strength": 0.45,
            "guidance_scale": 7.5,
            "prng_seed": "-1",
            "num_inference_steps": "50",
            "extra_prompt": text,
            "extra_negative_prompt": "",
            "random_generation": "False",
            "type": "1",
            "type_generation": "True",
            "sensitive_words": "white_kimono",
        },
        "extra": {},
        "media_info_list": [
            {
                "media_data": base64_image_string,
                "media_profiles": {
                    "media_data_type": "jpg",
                },
            },
        ],
    }

    response = requests.post(
        "https://openapi.mtlab.meitu.com/v1/stable_diffusion_anime",
        params=params,
        headers=headers,
        json=json_data,
    )

    return json.loads(response.content)
import time

@app.on_message(filters.command(["generate", "prompt", "imagine"]))
def mangadown(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format : /generate camel drinking water from bottle")
        return
    msg = msgs[1]

    # Initialize progress bar
    progress = 0
    total_progress = 100

    # Send initial progress message
    progress_message = message.reply_text("Generating image... ({:.0f}%)".format(progress))

    bad_words = ['pussy', 'dildo', 'milf', 'dick', 'cock', 'vagine', 'penis', 'boobs', 'fuck', 'fucking', 'ass', 'porn', 'nude', 'boob', 'nipple', 'nipples', 'xxx', 'sex', 'bikini', 'riding', 'naked', 'tit', 'tits', 'bigboobs', 'bigboob', 'smallboob', 'smallboobs','without clothes', 'nudes']
    for word in bad_words:
        if word in msg.lower():
            message.reply_text("WARNING: The use of inappropriate language or imagery is not permitted and may result in account blacklisted from bot.")
            return
    
    progress += 25

    try:
        
        model = replicate.models.get("cjwbw/dreamshaper")
        version = model.versions.get(
            "ed6d8bee9a278b0d7125872bddfb9dd3fc4c401426ad634d8246a660e387475b")
        # Update progress message
        progress_message.edit_text("Image processed... ({:.0f}%)".format(progress))
        output = version.predict(
            prompt=f"{msg}",
            negative_prompt="canvas frame, cartoon, 3d, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), wierd colors, blurry,  (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy, 3d render ENSD: 31337, naked, nude, nudity, nsfw, royalty, royals, cropped head",
            width=576,
            height=576,
            num_inference_steps = 50,
            guidance_scale = 7.5,
            scheduler = "K_EULER_ANCESTRAL"
            )

        
        progress += 40

        for x in output:
            # Update progress message
            progress_message.edit_text("Near to generate image... ({:.0f}%)".format(progress))
            progress += 35/len(output)

            message.reply_photo(
                photo=f"{x}",
                caption=
                f"**Prompt** - `{msg}`\n**Requested by [{message.from_user.first_name}](tg://user?id={message.from_user.id})**\nJoin @Am_Support"
            )

            app.send_message(
                -1001691751309,
                text=
                f"**Prompt** - `{msg}` \n**Requested by [{message.from_user.first_name}](tg://user?id={message.from_user.id})** {message.link}"
            )
            app.send_photo(-1001691751309, photo=x)

        # Update progress message
        progress_message.edit_text("Image generated! ({:.0f}%)".format(total_progress))
        time.sleep(1) # Give time for progress message to be seen before deleting
        progress_message.delete()

    except Exception as e:
        message.reply_text(f"⚠️ {e}\n Please Try Again")
        progress_message.delete()


@app.on_message(filters.command(["animate"]))
def mangadup(client, message):
    # Check if a photo is attached to the message
    if not message.reply_to_message or not message.reply_to_message.photo:
        message.reply_text("Please reply to an image.")
    else:
        # Get the photo and optional text
        reply = message.reply_to_message
        photo = reply.photo
        text = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else None
        
        # Show a loading message while processing the image
        loading_message = message.reply_text("Please wait 10-15 seconds...")
        
        # Download the photo in memory
        photo_file = client.download_media(photo.file_id, in_memory=True)
        photo_bytes = bytes(photo_file.getbuffer())
        
        # Encode the photo in base64
        base64_image_string = base64.b64encode(photo_bytes).decode("utf-8")

        if text:
            # Generate AI-generated image with text
            ai_image = get_ai_text(base64_image_string, text)["media_info_list"][0]["media_data"]
            message.reply_photo(
                photo=ai_image,
                caption=f"Hello **[{message.from_user.first_name}](tg://user?id={message.from_user.id})**\nJoin @Am_Support"
            )
            # Send the original message and generated image to a channel
            app.send_message(
                -1001691751309,
                f"{reply.link}\n{text} - by {message.from_user.first_name} (@{message.from_user.username})"
            )
            app.send_photo(
                -1001691751309,
                photo=ai_image,
                caption=f"{reply.link} - by {message.from_user.first_name} (@{message.from_user.username})"
            )
        else:
            # Generate AI-generated image
            ai_image = get_ai_image(base64_image_string)["media_info_list"][0]["media_data"]
            message.reply_photo(
                photo=ai_image,
                caption=f"Requested by - **[{message.from_user.first_name}](tg://user?id={message.from_user.id})**\nJoin @Am_Support"
            )
            # Send the original message and generated image to a channel
            app.send_message(
                -1001691751309,
                f"{reply.link} - \nby {message.from_user.first_name} \nUsername - @{message.from_user.username} \nUser Id - {message.from_user.id}"
            )
            app.send_photo(
                -1001691751309,
                photo=ai_image,
                caption=f"{reply.link}\nRequested by {message.from_user.first_name} (@{message.from_user.username})"
            )
        
        # Forward the original message to a channel
        try:
            reply.forward(-1001691751309)
        except Exception as e:
            app.send_photo(
                -1001691751309,
                photo=photo_file,
                caption=f"{reply.link} \nRequested by {message.from_user.first_name} (@{message.from_user.username})"
            )
        loading_message.delete()


__help__ = """
The `/generate text`command allows you to create an image with the given text. This image is created using Artificial Intelligence (AI) technology, which uses algorithms to generate images based on the text provided.
 ‣ `/generate create a cow on rocket`
 ‣ `/imagine create a cow on rocket`
 ‣ `/prompt create a cow on rocket`

The `/animate` command takes a user's image and creates an anime character of it. This is done by using AI to analyze the image and create a cartoon-like version of it.
 ‣ `/animate` reply to image 
"""

__mod_name__ = "Make Image"
