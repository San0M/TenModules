# meta developer: @Im_Tensh1

import io

from telethon import types

from .. import loader, utils


@loader.tds
class SaverMod(loader.Module):
    strings = {"name": "SvNudes"}

    async def client_ready(self, client, db):
        self.db = db

    @loader.owner
    async def scmd(self, m: types.Message):
        ".s <reply> - скачать фото"
        reply = await m.get_reply_message()
        if not reply or not reply.media or not reply.media.ttl_seconds:
            return await m.edit("s")
        await m.delete()
        new = io.BytesIO(await reply.download_media(bytes))
        new.name = reply.file.name
        await m.client.send_file("me", new)

    @loader.owner
    async def svcmd(self, m: types.Message):
        "Переключить режим автозагрузки фото в лс"
        new_val = not self.db.get("Saver", "state", False)
        self.db.set("Saver", "state", new_val)
        await utils.answer(m, f"<b>[Saver]</b> <pre>{new_val}</pre>")

    async def watcher(self, m: types.Message):

        if (
            m
            and m.media
            and m.media.ttl_seconds
            and self.db.get("Saver", "state", False)
        ):
            new = io.BytesIO(await m.download_media(bytes))
            new.name = m.file.name
            await m.client.send_file(
                "me",
                new,
                caption=f"<b>[Saver] Нюдсы от</b> {f'@{m.sender.username}' if m.sender.username else m.sender.first_name} | <pre>{m.sender.id}</pre>\n"
                f"Время таймера: <code>{m.media.ttl_seconds}sec</code>",
            )
