# coding = utf-8
# 17:16 12.11.2020

# Всі коментарі прибрав, код максимально очистив і оптимізував.

import logging
import re
import string
from asyncio import get_event_loop, sleep

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentType
from aiogram.utils.exceptions import Throttled, MessageToDeleteNotFound
from aiogram.utils.helper import Helper, HelperMode, ListItem
from pymysql import connect

from badword import badworld_seach_
from config import DB_HOST, DB_NAME, DB_PASS, DB_USER, TOKEN

loop = get_event_loop()
bot = Bot(token=TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, loop=loop, storage=storage)
dp.middleware.setup(LoggingMiddleware())
logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s', level=logging.INFO)

readonly = False
max_len = 3000

async def text_check_func_(text_, first_name, last_name, message_id, chat_id, from_user_id, message):
	len_ok = True
	all_ok = True
	if len(text_) > max_len:
		await bot.delete_message(int(chat_id), int(message_id))
		len_ok = False
		all_ok = False
	if bool(len_ok):
		a = await bot.get_chat_member(int(chat_id), int(from_user_id))
		if bool(readonly):
			if str(a.status) != "administrator" and str(a.status) != "creator":
				await bot.delete_message(int(chat_id), int(message_id))
				all_ok = False
		else:
			if str(a.status) != "administrator" and str(a.status) != "creator":
				text = await simple_filter(text_)
				if len(text) != len(text_):
					await bot.delete_message(int(chat_id), int(message_id))
					await bot.send_message(int(chat_id), str("Пользователь {} {} отправил сообщение: \"{}\"".format(
						str(first_name), 
						str(last_name), 
						str(text)
					)))
					all_ok = False
				for entity in message.entities:
					if entity.type in ["text_link"]:
						try:
							await bot.delete_message(int(message.chat.id), int(message.message_id))
							await message.answer(str("Пользователь {} {} отправил сообщение (В сообщении было найдено text_link): \"{}\"".format(
								str(message.from_user.first_name), 
								str(message.from_user.last_name), 
								str(message.text)
							)))
						except MessageToDeleteNotFound:
							pass
	return all_ok

async def simple_filter(text):
	out_string_domain = str(re.sub(r'[\S]+\.(net|com|org|info|edu|gov|uk|de|ca|jp|fr|au|us|ru|ch|it|nel|se|no|es|mil|kz|ua|by|ly|porn|sex|name|icu|biz|tk|ml|gq|ga|life|int|arpa|cc|gg|pw|бел|рус|рф|укр|ads|active|app|apple|author|aws|band|bank|best|bet|blog|bot|me|build|buy|cafe|car|ceo|chat|site|dev|cloud|club|cool|data|design|docs|drive|tor|fun|game|gay|global|gold|host|jobs|like|live)[\S]*\s?','(ссылка удалена)',str(text)))
	out_string_profile = str(re.sub(r'[\s](@|#)[\S]*\s?',' (ссылка удалена) ',str(out_string_domain)))
	final_string = await badworld_seach_(str(out_string_profile.lower()))
	logging.info("String filtered.")
	return str(final_string)

@dp.message_handler(commands=['stat', 'stats', 'statistics'])
async def statistics(message: types.Message):
	check_result_is_ok = await text_check_func_(
		str(message.text),
		str(message.from_user.first_name),
		str(message.from_user.last_name),
		int(message.message_id),
		int(message.chat.id),
		int(message.from_user.id),
		message
	)
	if bool(check_result_is_ok):
		try:
			await dp.throttle('stat', rate=5)
		except Throttled:
			pass
		else:
			num_msg_ = str(int(message.message_id) + 1)
			finish_string_stat = str('📊Статистика:\n✏️За всё время в чат было отправлено {} сообщений\n\n@xo_chat_bot'.format(num_msg_))
			await message.reply(str(finish_string_stat))

@dp.message_handler(commands=['readonly'])
async def statistics(message: types.Message):
	check_result_is_ok = await text_check_func_(
		str(message.text),
		str(message.from_user.first_name),
		str(message.from_user.last_name),
		int(message.message_id),
		int(message.chat.id),
		int(message.from_user.id),
		message
	)
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
	await text_check_func_(
		str(message.text),
		str(message.from_user.first_name),
		str(message.from_user.last_name),
		int(message.message_id),
		int(message.chat.id),
		int(message.from_user.id),
		message
	)

async def shutdown(dispatcher: Dispatcher):
	await dispatcher.storage.close()
	await dispatcher.storage.wait_closed()

if __name__ == '__main__':
	executor.start_polling(dp, loop=loop, skip_updates=False, on_shutdown=shutdown)
