import os

import telebot
from loguru import logger

from src.utils.io import read_json, write_json
from src.utils.keyboards import main_keyboard


class Bot():
	def __init__(self, bot_token) -> None:
		self.bot = telebot.TeleBot(bot_token)
		self.handler()
		self.data = []

	def run(self):
		logger.info('bot started')
		self.data = read_json('src/data/messages.json')
		self.bot.infinity_polling()
		write_json(self.data, 'src/data/messages.json')
		logger.info('bot finished')
	
	def handler(self):
		@self.bot.message_handler(commands=['start', 'help'])
		def send_welcome(message):
			logger.info(f'_________________________________\nUser with id: [{message.from_user.id}], username: [{message.from_user.username}] said:\n{message.text} \n')
			self.bot.reply_to(message, "Say something to answer you")
			self.data.append(message.json)

		@self.bot.message_handler(func=lambda m: m.text in main_keyboard.keys)	
		def key_response(message):
			logger.info(f'_________________________________\nUser with id: [{message.from_user.id}], username: [{message.from_user.username}] said:\n{message.text} \n')
			self.data.append(message.json)
			#Replace exclusive action for each key
			if message.text == 'Active':
				self.bot.send_message(message.chat.id, f'Action not assigned to <{message.text}> key')
			if message.text == 'Setting':
				self.bot.send_message(message.chat.id, f'Action not assigned to <{message.text}> key')
			if message.text == 'Info':
				self.bot.send_message(message.chat.id, f'Action not assigned to <{message.text}> key')
			if message.text == 'Contact us':
				self.bot.send_message(message.chat.id, f'Action not assigned to <{message.text}> key')

		@self.bot.message_handler(func=lambda m: True)
		def echo_all(message):
			logger.info(f'_________________________________\nUser with id: [{message.from_user.id}], username: [{message.from_user.username}] said:\n{message.text} \n')
			self.bot.send_message(message.chat.id, message.text, reply_markup=main_keyboard)
			self.data.append(message.json)



if __name__ == '__main__':
	bot = Bot(os.environ['bot_token'])
	bot.run()
