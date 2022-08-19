import os

import telebot
from loguru import logger

from src.constants import states
from src.db import db
from src.utils.keyboards import exit_keyboard, main_keyboard


class Bot():
    def __init__(self, bot_token):
        self.bot = telebot.TeleBot(bot_token)
        self.handler()

    def run(self):
        logger.info('bot started')
        self.bot.infinity_polling()
        logger.info('bot finished')
    
    def handler(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            logger.info(
                f"\nUser data: [{message.from_user.id}], [{message.from_user.username}] said:\n{message.text}\n"
                )

            db.users.update_one(
                {'from.id': message.from_user.id}, {'$set': message.json}, upsert=True
                )             
            self.update_state(message.from_user.id, states.start)
            self.bot.send_message(message.chat.id, "Press a button", reply_markup=main_keyboard)

        #Replace exclusive action for each key
        @self.bot.message_handler(func=lambda m: m.text == 'Connect to stranger')	
        def connect_key(message):
            logger.info(
                f"\nUser data: [{message.from_user.id}], [{message.from_user.username}] said:\n{message.text}\n"
                )
            user = db.users.find_one({
                'from.id': message.from_user.id
                })                
            if user['state'] == states.connecting:
                self.bot.send_message(message.chat.id, f'Wait until a stranger also press the <Connect to stranger> button', 
                    reply_markup=exit_keyboard)
                return

            if user['state'] == states.connected:
                self.bot.send_message(message.chat.id, f'You are already connected to a stranger', 
                    reply_markup=exit_keyboard)
                return

            self.update_state(message.from_user.id, states.connecting)
            self.bot.send_message(message.chat.id, f'Connecting to a stranger', reply_markup=exit_keyboard)                    
            other_user = db.users.find_one({
                'state': states.connecting,
                'from.id': {'$ne': message.from_user.id}
                })
            if other_user:
                self.update_state(message.from_user.id, states.connected)
                self.update_state(other_user['from']['id'], states.connected)
                db.users.update_one(
                    {'from.id': message.from_user.id},
                    {'$set': {'connected_to': other_user['from']['id']}}
                )
                db.users.update_one(
                    {'from.id': other_user['from']['id']},
                    {'$set': {'connected_to':  message.from_user.id}} 
                )
                self.bot.send_message(
                    message.from_user.id, 'You are connected to a stranger.\nI will send whatever you type to that stranger', reply_markup=exit_keyboard
                    )
                self.bot.send_message(
                    other_user['from']['id'], 'You are connected to a stranger.\nI will send anything you type to the stranger', reply_markup=exit_keyboard
                    )

        @self.bot.message_handler(func=lambda m: m.text == 'Exit')	
        def connect_key(message):
            logger.info(
                f"\nUser data: [{message.from_user.id}], [{message.from_user.username}] said:\n{message.text}\n"
                )
            user = db.users.find_one({
                'from.id': message.from_user.id
                })
            if user['state'] == states.start: 
                self.bot.send_message(message.chat.id, 'Press a button', reply_markup=main_keyboard)
                return

            if user['state'] == states.connecting:
                self.update_state(message.from_user.id, states.start)
                self.bot.send_message(message.chat.id, 'Search canceled\nPress a button',
                    reply_markup=main_keyboard)
                return

            self.update_state(message.from_user.id, states.start)
            self.update_state(user['connected_to'], states.start)

            self.bot.send_message(
                message.chat.id, 
                f'You left the chat',
                reply_markup=main_keyboard
                )
            self.bot.send_message(
                user['connected_to'], 
                f'You have left the chat beacuse the stranger left the chat',
                reply_markup=main_keyboard
                )

            db.users.update_one(
                {'from.id': user['connected_to']},
                {'$set': {'connected_to':  None}}
            )
            user['connected_to'] = None

        @self.bot.message_handler(func=lambda m: True)
        def echo_all(message):
            logger.info(
                f"\nUser data: [{message.from_user.id}], [{message.from_user.username}] said:\n{message.text}\n"
                )
            user = db.users.find_one({
                'from.id': message.from_user.id
                })
            if user['state'] != states.connected:
                self.bot.send_message(
                    message.chat.id, 
                    "You're not connected to anyone",
                    reply_markup=main_keyboard
                    )
                return               

            self.bot.send_message(
                user['connected_to'], f'Stranger said:\n{message.text}', reply_markup=exit_keyboard
                )

    def update_state(self, user_id, state):
        db.users.update_one(
                {'from.id':user_id}, {'$set': {'state': state}}, upsert=True
                )


if __name__ == '__main__':
    bot = Bot(os.environ['bot_token'])
    bot.run()
