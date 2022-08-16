from telebot import types


def make_keyboard(*args, row_width=2, resize_keyboard=True):
        
    markup = types.ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=resize_keyboard)
    keys = map(types.KeyboardButton, args)
    markup.add(*keys)
    markup.keys = args
    return markup

#Add your keyboards
main_keyboard = make_keyboard('Active', 'Setting', 'Info', 'Contact us')
