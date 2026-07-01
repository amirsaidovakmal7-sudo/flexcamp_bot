from telebot import types
def get_number():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Отправить номер телефона 📞', request_contact=True)
    kb.add(button1)
    return kb