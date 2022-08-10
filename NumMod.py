from .. import loader, utils
import asyncio, pytz, re, telethon
from telethon.tl.types import MessageEntityTextUrl
import json as JSON
from datetime import datetime, date, time

class NumMod(loader.Module):
	"Облегчает жизнь смертным."
	strings={"name": "NumMod"}
	
	async def client_ready(self, client, db):
		self.db = db
		if not self.db.get("NumMod", "exUsers", False):
			self.db.set("NumMod", "exUsers", [])
		if not self.db.get("NumMod", "infList", False):
			self.db.set("NumMod", "infList", {})
		
	async def зcmd(self, message):
		"Заражает по списку.\nВ качестве аргументов используй числа или первые символы строки.\nИспользуй:.з (аргумент) (аргумент) (аргумент)..."
		reply = await message.get_reply_message()
		a = reply.text
		exlist = self.db.get("NumMod", "exUsers")
		count_st = 0
		count_hf = 0
		if not reply:
			await message.edit('<b>Нет реплая❗️</b>')
			return
		args = utils.get_args_raw(message)
		list_args=[]
		if not args:
			await message.edit('<b>ID не обнаружен❗️</b>')
			return
		for i in args.split(' '):
			if '-' in i:
				ot_do = i.split('-')
				try:
					for x in range(int(ot_do[0]),int(ot_do[1])+1):
						list_args.append(str(x))
				except:
					await message.respond('<b>Используй правильно функцию "от-до"</b>❗️')
					return
			else:
				list_args.append(i)
		lis = a.splitlines()
		for start in list_args:
			for x in lis:
				if x.lower().startswith(str(start.lower())):
					count_st = 1
					if 'href="' in x:
						count_hf = 1
						b=x.find('href="')+6
						c=x.find('">')
						link = x[b:c]
						if link.startswith('tg'):
							list = '@' + link.split('=')[1]
							if list in exlist:
								await message.reply(f'<b>Исключение</b>: <code>{list}</code>')
							else:
								await message.reply(f'Заразить {list}')
							break
						elif link.startswith('https://t.me'):
							a ='@' + str(link.split('/')[3])
							if a in exlist:
								await message.reply(f'<b>Исключение</b>: <code>{a}</code>')
							else:
								await message.reply(f'Заразить {a}')
							break
						else:
							await message.reply('<b>Ты дурак⁉️</b>')
							break
			await asyncio.sleep(5)
		await message.delete() 
				
		if not count_st:
			await message.edit('<b>Не найдено ни одного совпадения в начале строк с аргументами❗️</b>')
			
		elif not count_hf:
			await message.edit('<b>Не найдено ни одной ссылки❗️</b>')
			
		elif len(list_args) >= 3:
			await message.respond('<b>Заражения успешно завершены.</b>')
			
	async def оcmd(self, message):
		"Заражает всех по реплаю.\n Используй: .о (на чье то сообщение 'Заразить @id')"
		reply = await message.get_reply_message()
		exlist = self.db.get("NumMod", "exUsers")
		if not reply:
			await message.edit('Нет реплая❗️')
			return
		json = JSON.loads(reply.to_json())
		for i in range(0, len(reply.entities) ):
			try:
				link = json["entities"][i]["url"]
				if link.startswith('tg'):
					list = '@' + link.split('=')[1]
					if list in exlist:
						await message.reply(f'<b>Исключение</b>: <code>{list}</code>')
					else:
						await message.reply('заразить ' + list)
				elif link.startswith('https://t.me'):
					a ='@' + str(link.split('/')[3])
					if a in exlist:
						await message.reply(f'<b>Исключение</b>: <code>{a}</code>')
					else:
						await message.reply(f'Заразить {a}')
				else:
					await message.reply('<b>Ты ввел хуйню⁉️</b>')
			except:
				await message.reply("Заразить " + reply.raw_text[json["entities"][i]["offset"]:json["entities"][i]["offset"]+json["entities"][i]["length"]] )
			await asyncio.sleep(5)
		await message.delete() 
		
	async def exnumcmd(self, message):
		"Добавляет исключения в модуль.\nИспользуй:  .exnum (@id/user)"
		args = utils.get_args_raw(message)
		exlistGet = self.db.get("NumMod", "exUsers")
		exlist = exlistGet.copy()
		if not args:
			if len(exlist) < 1:
				await message.edit('<b>Список исключений пуст❗️</b>')
				return
			exsms = ''
			count = 0
			for i in exlist:
				count+=1
				exsms+=f'<b>{count}.</b> <code>{i}</code>\n'
			message = await utils.answer(message, exsms)
			return
		if args == 'clear':
			exlist.clear()
			self.db.set("NumMod", "exUsers", exlist)
			await message.edit('<b>Список исключений очистен.</b>')
			return
		if len(args.split(' ')) > 1 or args[0] != '@':
			await message.edit('Количество аргументов <b>больше</b> одного, либо начинается <b>не</b> со знака <code>@</code>❗️')
			return
		if args in exlist:
			exlist.remove(args)
			self.db.set("NumMod", "exUsers", exlist)
			await message.edit(f'<b>Пользователь</b> <code>{args}</code> <b>исключён.</b>')
			return
		exlist.append(args)
		self.db.set("NumMod", "exUsers", exlist)
		await message.edit(f'<b>Пользователь</b> <code>{args}</code> <b>добавлен.</b>')
		
	async def zarlistcmd(self, message):
		""" Лист ваших заражений.\nИспользуй: .zarlist (@id/user) (цифра) (аргумент)\nДля удаления: .zarlist (@id/user)\nАргументы:\n-k — Добавить тысячу к числу.\n-f — Поиск по @id/user.\n-r — Добавляет в список по реплаю."""
		args = utils.get_args_raw(message)
		infList = self.db.get("NumMod", "infList")
		timezone = "Europe/Kiev"
		vremya = datetime.now(pytz.timezone(timezone)).strftime("%d.%m")
		try:
			args_list = args.split(' ')
		except:
			pass
		if not args:
			if not infList:
				await utils.answer(message, "Лист заражений <b>пуст</b>❗️")
				return
			sms = ''
			for key, value in infList.items():
				sms+=f'<b>• <code>{key}</code> — <code>{value[0]}</code> [<i>{value[1]}</i>]</b>\n'
			await utils.answer(message, sms)
			return
		if not '-r' in args.lower():
			if args_list[0] == "clear":
				infList.clear()
				self.db.set("NumMod", "infList", infList)
				await utils.answer(message, "Лист заражений <b>очищен</b>.")
			elif args_list[0] in infList and '-f' in args.lower():
				user = infList[args_list[0]]
				await utils.answer(message, f"<b>• <code>{args_list[0]}</code> — <code>{user[0]}</code> [<i>{user[1]}</i>]</b>")
				await asyncio.sleep(5)
			elif len(args_list) == 1 and args_list[0] in infList:
				infList.pop(args_list[0])
				self.db.set("NumMod", "infList", infList)
				await utils.answer(message, f"<b>Пользователь</b> <code>{args}</code> <b>удалён из списка.</b>")
				await asyncio.sleep(3)
			elif args_list[0][0] != '@':
				await utils.answer(message, '<b>Это не</b> <code>@id/user</code>❗️')
			else:
				try:
					user, count = str(args_list[0]), float(args_list[1])
				except:
					await utils.answer(message, "<b>Не правильный аргумент либо этого @id нету в списке❗️</b>")
					return
				k = ''
				if '-k' in args.lower():
					k+='k'
				infList[user] = [str(count)+k, vremya]
				self.db.set("NumMod", "infList", infList)
				await utils.answer(message, f"Пользователь <code>{user}</code> добавлен в список заражений.\nЧисло: <code>{count}</code>{k}\nДата: <b>{vremya}</b>")
				await asyncio.sleep(5)
			await message.delete()
		else:
			reply = await message.get_reply_message()
			if not reply: 
				return await utils.answer(message, 'Реплай должен быть на смс ириса "<b>...подверг заражению...</b>"❗️')
			elif reply.sender_id != 707693258 and not 'подверг заражению' in reply.text:
				return await utils.answer(message, 'Реплай должен быть на смс ириса "<b>...подверг заражению...</b>"❗️')
			else: #☣
				text = reply.text
				x = text.index('☣')+4
				count = text[x:].split(' ', maxsplit=1)[0]
				x = text.index('user?id=') + 8
				user = '@' + text[x:].split('"', maxsplit=1)[0]
				infList[user] = [str(count), vremya]
				self.db.set("NumMod", "infList", infList)
				await utils.answer(message, f"<b>Пользователь</b> <code>{user}</code> <b>добавлен в список заражений.</b>\n<b>Число</b>: <code>{count}</code>\n<b>Дата</b>: <b>{vremya}</b>")

	async def numfiltercmd(self, message):
		"""Доверенность.\nИспользуй: .numfilter (аргумент) (id или реплай) \nВызови команду, чтобы просмотреть аргументы."""
		args = utils.get_args_raw(message)
		reply = await message.get_reply_message()
		filter_and_users = self.db.get("NumMod", "numfilter", {'users': [], 'filter': None, 'status': False})
		if not args:
			return await utils.answer(message, f"-sU — добавить|удалить юзеров(не больше 10), на которых будет триггериться фильтр(ид|реплай).\n[{', '.join(list('<code>' + i + '</code>' for i in filter_and_users['users']))}]\n-sF — установить фильтр. Допустим один.\n<code>{filter_and_users['filter'] if filter_and_users['filter'] else '❌Не установлен.'}</code>\n-t — запустить|остановить.\n<b>{'✅Запущен' if filter_and_users['status'] else '❌Остановлен'}.</b>\n\nРаботает так:\n[фильтр] (уеби|бей|зарази[ть]) (1-10) ((@id|user)|link(даже полный линк ид'а))\n[фильтр] лечись|вакцин[ау]|купи[ть] вакцину\n[фильтр] покажи|жертв[ыу]|жерт[ва]")
		args = args.split(' ', maxsplit=1)
		if len(args) == 1 and not reply and args[0] != '-t':
			return await utils.answer(message, '❌ Нет 2 аргумента и реплая.')
		elif args[0] == '-sU':
			try:
				user_id = args[1]
				if not user_id.isdigit():
					return await utils.answer(message, 'Это не ид.')
			except:
				user_id = str(reply.sender_id)
			if user_id in filter_and_users['users']:
				filter_and_users['users'].remove(user_id)
				await utils.answer(message, f"✅ Ид <code>{user_id}</code> удалён.")
			elif len(filter_and_users['users']) <= 10:
				filter_and_users['users'].append(user_id)
				await utils.answer(message, f"✅ Ид <code>{user_id}</code> добавлен.")
			else:
				return await utils.answer(message, '❌ Превышен лимит в 10 юзеров.')
			return self.db.set("NumMod", "numfilter", filter_and_users)
		elif args[0] == '-sF':
			try:
				filter_and_users['filter'] = args[1].lower().strip()
				self.db.set("NumMod", "numfilter", filter_and_users)
				return await utils.answer(message, f"✅ Фильтр ~~~ <code>{args[1]}</code> ~~~ успешно установлен!")
			except:
				return await utils.answer(message, "Где 2 аргумент❓")
		elif args[0] == '-t':
			if filter_and_users['status']:
				filter_and_users['status'] = False
				self.db.set("NumMod", "numfilter", filter_and_users)
				return await utils.answer(message, "❌ Фильтр остановлен.")
			else:
				filter_and_users['status'] = True
				self.db.set("NumMod", "numfilter", filter_and_users)
				return await utils.answer(message, "✅ Фильтр запущен.")
		else:
			return await utils.answer(message, "❌ Неизвестный аргумент.")

	async def watcher(self, message):
		if not isinstance(message, telethon.tl.types.Message): return
		filter_and_users = self.db.get("NumMod", "numfilter", {'users': [], 'filter': None, 'status': False})
		user_id = str(message.sender_id)
		if not filter_and_users['filter'] or not filter_and_users['status'] or user_id not in filter_and_users['users'] or message.is_private: return
		text = message.raw_text.lower()
		if not text.startswith(filter_and_users['filter']): return
		send_mes = re.search(r"(?P<z>уеби\s|бей\s|зарази[ть]{,2}\s)(?P<lvl>[1-9]?[0]?\s)?(?P<link>@[0-9a-z_]+|(?:https?://)?t\.me/[0-9a-z_]+|tg://openmessage\?user_id=(?P<id>[0-9]+))", text)
		if send_mes:
			send_mes = send_mes.groupdict()
			send_mes['link'], send_mes['id'] = '@'+send_mes['id'] if send_mes['id'] else send_mes['link'], ''
			send_mes['z'] = 'Заразить '
			send_mes['lvl'] = send_mes['lvl'] if send_mes['lvl'] else ''
			mes = ''.join(send_mes.values())
			await message.respond(mes)
		send_mes = re.search(r"покажи|жертв[ыу]|жерт[ва]{,2}", text)
		if send_mes: await message.respond('Мои жертвы')
		else:
			send_mes = re.search(r"лечись|вакцин[ау]|купи[ть]{,2}", text)
			if send_mes: await message.respond('.Купить вакцину')
		
