# requires: aiohttp

import asyncio
import hashlib
import time
from socket import socket

import aiohttp
from telethon import types

from .. import loader, utils


@loader.tds
class DuinoMinerMod(loader.Module):
    "DuinoMiner"

    strings = {
        "name": "DuinoMiner",
        "msg": "<b>[DuinoMiner]</b> {}",
    }
    
    soc = socket()

    @staticmethod
    async def get_pool() -> tuple:
        async with aiohttp.ClientSession() as s, s.get("https://server.duinocoin.com/getPool") as r:
            j = await r.json()
            return (j['ip'], j['port'])

    async def minecmd(self, m: types.Message):
        nickname = utils.get_args_raw(m)
        if not nickname:
            return await utils.answer(m, self.strings("msg").format("Укажи ник для майнинга"))
        while True:
            try:
                m = await utils.answer(m, self.strings("msg").format("Ищем лучший пул для майнинга..."))
                try:
                    NODE_ADDRESS, NODE_PORT = await self.get_pool()
                except Exception as e:
                    NODE_ADDRESS, NODE_PORT = "server.duinocoin.com", 2813
                    m = await utils.answer(m, self.strings("msg").format("Всё пошло к ебени матери, юзаем дефолт сервер"))
                self.soc.connect((str(NODE_ADDRESS), int(NODE_PORT)))
                server_version = self.soc.recv(100).decode()
                m = await utils.answer(m, self.strings("msg").format(f"Сервер: {server_version}"))
                while True:
                    self.soc.send(bytes(
                        "JOB,"
                        + str(nickname),
                        encoding="utf8"))
                    # Receive work
                    job = self.soc.recv(1024).decode().rstrip("\n")
                    m = await utils.answer(m, self.strings("msg").format("Есть ворк, ебашим!"))
                    job = job.split(",")
                    difficulty = job[2]

                    hashingStartTime = time.time()
                    base_hash = hashlib.sha1(str(job[0]).encode('ascii'))
                    temp_hash = None

                    for result in range(100 * int(difficulty) + 1):
                        # Calculate hash with difficulty
                        temp_hash = base_hash.copy()
                        temp_hash.update(str(result).encode('ascii'))
                        ducos1 = temp_hash.hexdigest()

                        # If hash is even with expected hash result
                        if job[1] == ducos1:
                            hashingStopTime = time.time()
                            timeDifference = hashingStopTime - hashingStartTime
                            hashrate = result / timeDifference

                            # Send numeric result to the server
                            self.soc.send(bytes(
                                str(result)
                                + ","
                                + str(hashrate)
                                + ",FTG-Miner",
                                encoding="utf8"))

                            # Get feedback about the result
                            feedback = self.soc.recv(1024).decode().rstrip("\n")
                            # If result was good
                            if feedback == "GOOD":
                                m = await utils.answer(m, self.strings("msg").format(f"Заебись шара! Спид {int(hashrate/1000)}kH/s | Сложна на {difficulty}"))
                                break
                            # If result was incorrect
                            elif feedback == "BAD":
                                m = await utils.answer(m, self.strings("msg").format(f"Хуйня шара! Спид {int(hashrate/1000)}kH/s | Сложна на {difficulty}"))
                                break
                await asyncio.sleep(1)
            except Exception as e:
                m = await utils.answer(m, self.strings("msg").format(f"Уебался об тумбочку! Останавливаюсь нахуй\n\n{e}"))
                break
