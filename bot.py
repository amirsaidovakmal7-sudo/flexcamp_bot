import telebot
import time
import buttons
from amocrm.v2 import tokens, Lead
from config import TOKEN

tokens.default_token_manager(
    client_id="xxx-xxx-xxxx-xxxx-xxxxxxx",
    client_secret="xxxx",
    subdomain="subdomain",
    redirect_url="https://xxxx/xx",
    storage=tokens.FileTokensStorage(),  # by default FileTokensStorage
)
tokens.default_token_manager.init(code="..very long code...", skip_error=True)

group_id = -1003960414454


bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Добро пожаловать в летний лагерь Flex Camp!')
    bot.send_chat_action(user_id, 'typing')
    time.sleep(4)
    bot.send_message(user_id, 'Наш лагерь с уклоном на английский язык ❤️ \n\n'
                              'Мы находимся на Таваксае 🏔 \n'
                              'Трансфер с нас! 🚗 \n\n'
                              'Деток принимаем с 6 до 16 лет \n'
                              'У нас есть 8 крутых современных кружков ( роботехника, спорт, клуб дебатов и т.д...) \n\n'
                              'Наша программа уникальна тем, что ее собрали лучшие психологи и специалисты с образования, именно поэтому ваш ребенок через квесты, задачи и награды, будет принимать много полезных навыков💪 \n\n'
                              'Хогвартс 1 смена - 3.290.000 \n'
                              'Остальные ( роблокс, осд, игра в кальмара и т.д) - 3.690.000 \n\n'
                              'Смена длится 10 дней🧸 \n'
                              'Подскажите, пожалуйста, вам подходят наши условия, могу рассказать о них подробнее, ценовая категория, локация ?☺️')
    bot.send_chat_action(user_id, 'typing')
    time.sleep(2)
    bot.send_message(user_id, 'Отправьте свой номер телефона, мы свяжемся с вами для предоставления большей информации ☺️',
                     reply_markup=buttons.get_number())
    bot.register_next_step_handler(message, get_phone_number)



def get_phone_number(message):
    user_id = message.from_user.id
    if message.contact:
        user_phone = message.contact.phone_number
        user_username = message.from_user.username
        bot.send_chat_action(user_id, 'typing')
        time.sleep(2)
        bot.send_message(user_id, 'Спасибо! Наш специалист свяжется с вами в ближайшее время',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        text = (f'Новый клиент! (заявка из телеграм бота) \n\n'
                f'Номер телефона: {user_phone} \n'
                f'Телеграм юзер: @{user_username} \n')

        bot.send_message(group_id, text)
        #Lead.objects.create(name=user_username, phone=user_phone)
    else:
        bot.send_message(user_id, 'Отправьте номер через кнопку!')
        bot.register_next_step_handler(message, get_phone_number)


bot.polling(non_stop=True)