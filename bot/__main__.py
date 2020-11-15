# coding = utf-8

import logging
import re
from asyncio import get_event_loop

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.exceptions import MessageToDeleteNotFound, Throttled

from badword import badworld_seach_
from config import TOKEN, internal_link, external_link

loop = get_event_loop()
bot = Bot(token=TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, loop=loop, storage=storage)
dp.middleware.setup(LoggingMiddleware())
logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s', level=logging.INFO)

readonly = False
max_len = 3600

async def text_check_func_(message):
	len_ok = True
	all_ok = True
	if len(message.text) > max_len:
		await bot.delete_message(message.chat.id, message.message_id)
		len_ok = False
	if len_ok:
		a = await bot.get_chat_member(message.chat.id, message.from_user.id)
		if readonly:
			if a.status != "administrator" and a.status != "creator":
				await bot.delete_message(message.chat.id, message.message_id)
				all_ok = False
		else:
			if a.status != "administrator" and a.status != "creator":
				text = await simple_filter(message.text)
				if len(text) != len(message.text):
					await bot.delete_message(message.chat.id, message.message_id)
					await bot.send_message(message.chat.id, "Пользователь {} {} отправил сообщение: \"{}\"".format(
						message.from_user.first_name, 
						message.from_user.last_name, 
						text
					))
					all_ok = False
				for entity in message.entities:
					if entity.type in ["text_link"]:
						try:
							await bot.delete_message(message.chat.id, message.message_id)
							await message.answer("Пользователь {} {} отправил сообщение (В сообщении было найдено text_link): \"{}\"".format(
								message.from_user.first_name, 
								message.from_user.last_name, 
								message.text
							))
						except MessageToDeleteNotFound:
							pass
	else:
		all_ok = False
	return all_ok

async def simple_filter(text):
	out_string_domain = re.sub(r'[\S]+\.(net|com|org|info|edu|gov|uk|de|ca|jp|fr|au|us|ru|ch|it|nel|se|no|es|mil|kz|ua|by|ly|porn|sex|name|icu|biz|tk|ml|gq|ga|life|int|arpa|cc|gg|pw|бел|рус|рф|укр|ads|active|app|apple|author|aws|band|bank|best|bet|blog|bot|me|build|buy|cafe|car|ceo|chat|site|dev|cloud|club|cool|data|design|docs|drive|tor|fun|game|gay|global|gold|host|jobs|like|live)[\S]*\s?', external_link, text)
	out_string_profile = re.sub(r'[\s](@|#)[\S]*\s?', ' {} '.format(internal_link), out_string_domain)
	final_string = await badworld_seach_(out_string_profile.lower())
	return final_string

@dp.message_handler(commands=['stat', 'stats', 'statistics'])
async def statistics(message: types.Message):
	check_result_is_ok = await text_check_func_(message)
	if check_result_is_ok:
		try:
			await dp.throttle('stat', rate=5)
		except Throttled:
			pass
		else:
			num_msg_ = str(message.message_id + 1)
			finish_string_stat = str('📊Статистика:\n✏️За всё время в чат было отправлено {} сообщений'.format(num_msg_))
			await message.reply(finish_string_stat)

@dp.message_handler(commands=['readonly'])
async def statistics(message: types.Message):
	check_result_is_ok = await text_check_func_(message)
	if bool(check_result_is_ok):
		try:
			await dp.throttle('readonly', rate=1)
		except Throttled:
			pass
		else:
			a = await bot.get_chat_member(int(message.chat.id), int(message.from_user.id))
			if str(a.status) == "creator" or str(a.status) == "administrator":
				global readonly
				if bool(readonly):
					readonly = False
					await message.reply("Readonly - Выключено")
				else:
					readonly = True
					await message.reply("Readonly - Включено")

@dp.message_handler(content_types=['text'])
async def handle_message_received(message):
	await text_check_func_(message)
	
@dp.message_handler(content_types=['NEW_CHAT_MEMBERS', 'LEFT_CHAT_MEMBER', 'PINNED_MESSAGE', 'NEW_CHAT_TITLE', 'NEW_CHAT_PHOTO', 'DELETE_CHAT_PHOTO', 'GROUP_CHAT_CREATED'])
async def handle_message_received(message):
	await bot.delete_message(message.chat.id, message.message_id)

async def shutdown(dispatcher: Dispatcher):
	await dispatcher.storage.close()
	await dispatcher.storage.wait_closed()

if __name__ == '__main__':
	executor.start_polling(dp, loop=loop, skip_updates=False, on_shutdown=shutdown)
