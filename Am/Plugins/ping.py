import time
from typing import List


from platform import python_version, uname
from telethon import version, events
import psutil, shutil, time, sys, platform

import requests
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, run_async

from Am import StartTime, dispatcher, telethn, OWNER_ID
from Am.Handlers.validation import sudo_plus
from Am.Plugins.disable import DisableAbleCommandHandler

sites_list = {
    "Telegram": "https://api.telegram.org",
    "Kaizoku": "https://animekaizoku.com",
    "Kayo": "https://animekayo.com",
    "Jikan": "https://api.jikan.moe/v3",
}


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


def ping_func(to_ping: List[str]) -> List[str]:
    ping_result = []

    for each_ping in to_ping:

        start_time = time.time()
        site_to_ping = sites_list[each_ping]
        r = requests.get(site_to_ping)
        end_time = time.time()
        ping_time = str(round((end_time - start_time), 2)) + "s"

        pinged_site = f"<b>{each_ping}</b>"

        if each_ping == "Kaizoku" or each_ping == "Kayo":
            pinged_site = f'<a href="{sites_list[each_ping]}">{each_ping}</a>'
            ping_time = f"<code>{ping_time} (Status: {r.status_code})</code>"

        ping_text = f"{pinged_site}: <code>{ping_time}</code>"
        ping_result.append(ping_text)

    return ping_result


 
@sudo_plus
def ping(update: Update, context: CallbackContext):
    msg = update.effective_message

    start_time = time.time()
    message = msg.reply_text("Pinging...")
    end_time = time.time()
    telegram_ping = str(round((end_time - start_time) * 1000, 3)) + " ms"
    uptime = get_readable_time((time.time() - StartTime))

    message.edit_text(
        "PONG!!\n"
        "<b>Time Taken:</b> <code>{}</code>\n"
        "<b>Service uptime:</b> <code>{}</code>".format(telegram_ping, uptime),
        parse_mode=ParseMode.HTML,
    )


 
@sudo_plus
def pingall(update: Update, context: CallbackContext):
    to_ping = ["Kaizoku", "Kayo", "Telegram", "Jikan"]
    pinged_list = ping_func(to_ping)
    pinged_list.insert(2, "")
    uptime = get_readable_time((time.time() - StartTime))

    reply_msg = "⏱Ping results are:\n"
    reply_msg += "\n".join(pinged_list)
    reply_msg += "\n<b>Service uptime:</b> <code>{}</code>".format(uptime)

    update.effective_message.reply_text(
        reply_msg, parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )




def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor



async def psu(event):
    if event.sender_id == OWNER_ID:            
        uname = platform.uname()
        softw = "**System Information**\n"
        softw += f"`System   : {uname.system}`\n"
        softw += f"`Release  : {uname.release}`\n"
        softw += f"`Version  : {uname.version}`\n"
        softw += f"`Machine  : {uname.machine}`\n"

        # CPU Cores
        cpuu = "**CPU Info**\n"
        cpuu += "`Physical cores   : " + str(psutil.cpu_count(logical=False)) + "`\n"
        cpuu += "`Total cores      : " + str(psutil.cpu_count(logical=True)) + "`\n"
        # CPU frequencies
        cpufreq = psutil.cpu_freq()
        cpuu += f"`Max Frequency    : {cpufreq.max:.2f}Mhz`\n"
        cpuu += f"`Min Frequency    : {cpufreq.min:.2f}Mhz`\n"
        cpuu += f"`Current Frequency: {cpufreq.current:.2f}Mhz`\n\n"
        # CPU usage
        cpuu += "**CPU Usage Per Core**\n"
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
            cpuu += f"`Core {i}  : {percentage}%`\n"
        cpuu += "\n**Total CPU Usage**\n"
        cpuu += f"`All Core: {psutil.cpu_percent()}%`\n"
        # RAM Usage
        svmem = psutil.virtual_memory()
        memm = "**Memory Usage**\n"
        memm += f"`Total     : {get_size(svmem.total)}`\n"
        memm += f"`Available : {get_size(svmem.available)}`\n"
        memm += f"`Used      : {get_size(svmem.used)} ({svmem.percent}%)`\n"
        # Disk Usage
        dtotal, dused, dfree = shutil.disk_usage(".")
        disk = "**Disk Usage**\n"
        disk += f"`Total     : {get_size(dtotal)}`\n"
        disk += f"`Free      : {get_size(dused)}`\n"
        disk += f"`Used      : {get_size(dfree)}`\n"
        # Bandwidth Usage
        bw = "**Bandwith Usage**\n"
        bw += f"`Upload  : {get_size(psutil.net_io_counters().bytes_sent)}`\n"
        bw += f"`Download: {get_size(psutil.net_io_counters().bytes_recv)}`\n"
        help_string = f"{str(softw)}\n"
        help_string += f"{str(cpuu)}\n"
        help_string += f"{str(memm)}\n"
        help_string += f"{str(disk)}\n"
        help_string += f"{str(bw)}\n"
        help_string += "**Engine Info**\n"
        help_string += f"`Python {sys.version}`\n"
        help_string += f"`Telethon {version.__version__}`"
        await event.reply(help_string)

    else:
        await event.reply("Only my owner have access of this command")


PING_HANDLER = DisableAbleCommandHandler("ping", ping, run_async=True)
PINGALL_HANDLER = DisableAbleCommandHandler("pingall", pingall, run_async=True)
SYSTEM_HANDLER = psu, events.NewMessage(pattern="^[!/]system$")


dispatcher.add_handler(PING_HANDLER)
dispatcher.add_handler(PINGALL_HANDLER)
telethn.add_event_handler(*SYSTEM_HANDLER)

__command_list__ = ["ping", "pingall", "system"]
__handlers__ = [PING_HANDLER, PINGALL_HANDLER, SYSTEM_HANDLER]