__version__ = (1, 0, 0)
"""
    █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
    █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█

    Copyright 2022 t.me/hikariatama
    Licensed under the Creative Commons CC BY-NC-ND 4.0

    Full license text can be found at:
    https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode

    Human-friendly one:
    https://creativecommons.org/licenses/by-nc-nd/4.0
"""

# <3 title: BCheck
# <3 pic: https://img.icons8.com/fluency/48/000000/cat-eyes.png
# <3 desc: Bulk chat phone number leakage check

from .. import loader, utils
import asyncio
import requests
import json

from telethon.tl.types import *
# requires: requests


@loader.tds
class BCheckMod(loader.Module):
    """Bulk chat phone number leakage check"""
    strings = {
        "name": "BCheck",
       'checking': '<b>Checking chat...</b>',
       'check_in_progress': 'Check in progress...',
       'search_header': "Search result: ",
       'not_found': "Result: <code>Not found</code>",
       'check_started': 'Starting check in chat'
    }

    async def bcheckcmd(self, message):
        """Check all chat members for leaked numbers"""
        await utils.answer(message, self.strings('checking'))

        check_result = self.strings('search_header', message)

        async for user in message.client.iter_participants(message.to_id):
            dt = requests.get(
                'http://api.murix.ru/eye?v=1.2&uid=' + str(user.id)).json()
            # await message.reply("<code>" + json.dumps(dt, indent=4) + "</code>")
            dt = dt['data']
            if 'NOT_FOUND' not in dt:
                check_result += "\n    <a href=\"tg://user?id=" + str(user.id) + "}\">" + (str(
                    user.first_name) + " " + str(user.last_name)).replace(' None', "") + "</a>: <code>" + dt + "</code>"
                await message.edit(check_result + '\n\n' + self.strings('check_in_progress'))
            await asyncio.sleep(1)

        if check_result == self.strings('search_header', message):
            check_result = self.strings('not_found', message)

        await message.edit(check_result)

    async def bchecksilentcmd(self, message):
        """Silent mode of bcheck"""
        await message.delete()
        msg = await message.client.send_message('me', self.strings('check_started', message))
        check_result = self.strings('search_header', message)

        async for user in message.client.iter_participants(message.to_id):
            dt = requests.get(
                'http://api.murix.ru/eye?v=1.2&uid=' + str(user.id)).json()
            # await message.reply("<code>" + json.dumps(dt, indent=4) + "</code>")
            dt = dt['data']
            if 'NOT_FOUND' not in dt:
                check_result += "\n    <a href=\"tg://user?id=" + str(user.id) + "}\">" + (str(
                    user.first_name) + " " + str(user.last_name)).replace(' None', "") + "</a>: <code>" + dt + "</code>"
                await msg.edit(check_result + '\n\n' + self.strings('check_in_progress', message))
            await asyncio.sleep(1)

        if check_result == self.strings('search_header', message):
            check_result = self.strings('not_found', message)

        await msg.edit(check_result)
