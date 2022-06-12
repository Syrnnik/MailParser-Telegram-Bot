import email
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from configparser import ConfigParser
from MailsDB import MailsDB
from KeyBoards import *
from uuid import uuid4
from hashlib import sha256
# from MailParser import MailParser
import time
from datetime import datetime as dt


# mailConf = ConfigParser()
# mailConf.read("./mailConf.ini")

config = ConfigParser()
config.read("./botConf.ini")

token = config.get('TeleBot', 'token')


bot = TeleBot(token=token)

parseMode = "Markdown"

mails = MailsDB()
# mailParser = MailParser()


mail_is_busy = "Эта почта уже подключена."
wrong_pass_msg = "Неверный пароль"
confirm_password_msg = "Введите пароль для подтверждения"


def get_username(user: object):
    username = f"{user.first_name} {user.last_name}"
    return username

def get_mail_host(email: str):
    host = 'imap.' + email.split('@')[1]
    return host

def get_salt():
    salt = uuid4().hex
    return salt

def hash_password(telegram_id: int, password: str):
    salt = get_salt()
    return sha256(str(telegram_id).encode() + salt.encode() + password.encode()).hexdigest() + ":" + salt

def check_password(telegram_id: int, email: str, user_password: str):
    hashed_password = mails.getPasswordHashByEmail(email)
    password, salt = hashed_password.split(':')
    return password == sha256(str(telegram_id).encode() + salt.encode() + user_password.encode()).hexdigest()

def get_mail_info(email: str, content: bool, attaches: bool):
    # TODO: add 'active' and 'email_number' params
    mail_info = f"""
Адрес: {email}
Содержимое: _{"включено" if content else "отключено"}_
Прикреплённые файлы: _{"включены" if attaches else "отключены"}_
"""
    return mail_info


#*#####################*#
#*######  START  ######*#
#*#####################*#

@bot.message_handler(commands=['start', 'help'])
def start(msg):
    user_id = msg.from_user.id
    # print(msg)
    # print(msg.from_user)

    info_msg = """
/help - вызвать это меню.
/newemail - подключить почту для получения писем.
/myуmails - посмотреть список подключённых почт.
/changeemail `<номер_почты>` - изменить адрес почты.
/changepass `<номер_почты>` - сменить пароль от почты.
/attacheson `<номер_почты>` - включить прикрепление файлов из письма.
/attachesoff `<номер_почты>` - отключить прикрепление файлов из письма.
/removeemail `<номер_почты>` - отключить почту.
/runsession `<номер_почты>` - включить получение писем.
/stopsession `<номер_почты>` - выключить получение писем.

`<номер_почты>` можно узнать в профиле
"""

    return bot.send_message(user_id, info_msg, parse_mode=parseMode)


#*####################*#
#*####  NEW MAIL  ####*#
#*####################*#

@bot.message_handler(commands=['newemail'])
def newemail(msg):
    user_id = msg.from_user.id
    
    reply_msg = bot.send_message(user_id, "Введите адрес почты")
    return bot.register_next_step_handler(reply_msg, enter_email)

def enter_email(msg):
    user_id = msg.from_user.id
    email = msg.text

    if mails.getUserByEmail(user_id):
        return bot.send_message(user_id, mail_is_busy)

    reply_msg = bot.send_message(user_id, "Теперь назовите пароль от почты")
    return bot.register_next_step_handler(reply_msg, enter_password, reply_msg.id, email)

def enter_password(msg, pass_msg_id: int, email: str):
    user_id = msg.from_user.id
    password = msg.text
    bot.delete_message(user_id, msg.id)
    bot.delete_message(user_id, pass_msg_id)
    # username = get_username(msg.from_user)

    mails.add(
        telegram_id=user_id,
        email=email,
        password_hash=hash_password(user_id, password),
        active=True,
        show_content=True,
        show_attaches=True
    )

    mail_info = get_mail_info(email=email, content=mails.showContent(email), attaches=mails.showAttaches(email))

    keyboard = getMailKeyboard(
        content=mails.showContent(email),
        attaches=mails.showAttaches(email)
    )
    

    return bot.send_message(user_id, mail_info, reply_markup=keyboard, parse_mode=parseMode)

#^ Functions for callbacks ^#
def get_callback_mail_info(callback: object):
    user_id = callback.from_user.id
    msg_id = callback.message.id
    email = callback.message.text.split('\n')[1].split(' ')[1]
    return user_id, msg_id, email

def get_edited_mail_content(email: str):
    mail_info = get_mail_info(email=email, content=mails.showContent(email), attaches=mails.showAttaches(email))

    keyboard = getMailKeyboard(
        content=mails.showContent(email),
        attaches=mails.showAttaches(email)
    )
    
    return mail_info, keyboard

#^######################^#
#^###  Show Content  ###^#
#^######################^#

@bot.callback_query_handler(func=lambda call: call.data == "on_content")
def on_mail_content(callback):
    bot.answer_callback_query(callback.id)
    user_id, msg_id, email = get_callback_mail_info(callback)
    
    mails.setContentByEmail(email, True)
    mail_info, keyboard = get_edited_mail_content(email)
    
    return bot.edit_message_text(mail_info, user_id, msg_id, reply_markup=keyboard, parse_mode=parseMode)

@bot.callback_query_handler(func=lambda call: call.data == "off_content")
def off_mail_content(callback):
    bot.answer_callback_query(callback.id)
    user_id, msg_id, email = get_callback_mail_info(callback)
    
    mails.setContentByEmail(email, False)
    mail_info, keyboard = get_edited_mail_content(email)
    
    return bot.edit_message_text(mail_info, user_id, msg_id, reply_markup=keyboard, parse_mode=parseMode)

#^#######################^#
#^###  Show Attaches  ###^#
#^#######################^#

@bot.callback_query_handler(func=lambda call: call.data == "off_attaches")
def off_mail_attaches(callback):
    bot.answer_callback_query(callback.id)
    user_id, msg_id, email = get_callback_mail_info(callback)
    
    mails.setAttachesByEmail(email, False)
    mail_info, keyboard = get_edited_mail_content(email)

    return bot.edit_message_text(mail_info, user_id, msg_id, reply_markup=keyboard, parse_mode=parseMode)

@bot.callback_query_handler(func=lambda call: call.data == "on_attaches")
def off_mail_attaches(callback):
    bot.answer_callback_query(callback.id)
    user_id, msg_id, email = get_callback_mail_info(callback)
    
    mails.setAttachesByEmail(email, True)
    mail_info, keyboard = get_edited_mail_content(email)
    
    return bot.edit_message_text(mail_info, user_id, msg_id, reply_markup=keyboard, parse_mode=parseMode)

#^######################^#
#^###  Change Email  ###^#
#^######################^#

@bot.callback_query_handler(func=lambda call: call.data == "change_email")
def change_user_email(callback):
    bot.answer_callback_query(callback.id)
    user_id, _, old_email = get_callback_mail_info(callback)
    
    reply_msg = bot.send_message(user_id, "Введите новый адрес почты")
    return bot.register_next_step_handler(reply_msg, change_email, old_email)

def change_email(msg, old_email: str):
    user_id = msg.from_user.id
    new_email = msg.text
    
    reply_msg = bot.send_message(user_id, confirm_password_msg)
    return bot.register_next_step_handler(reply_msg, confirm_password, reply_msg.id, old_email, new_email)
    
def confirm_password(msg, pass_msg_id: int, old_email: str, new_email: str):
    user_id = msg.from_user.id
    bot.delete_message(user_id, msg.id)
    bot.delete_message(user_id, pass_msg_id)
    
    if check_password(telegram_id=user_id, email=old_email, user_password=msg.text):
        mails.changeEmail(old_email, new_email)
        bot.send_message(user_id, "Адрес почты успешно изменён")
        
        mail_info, keyboard = get_edited_mail_content(new_email)
        return bot.send_message(user_id, mail_info, reply_markup=keyboard, parse_mode=parseMode)
    
    else:
        return bot.send_message(user_id, wrong_pass_msg)

#^#########################^#
#^###  Change Password  ###^#
#^#########################^#

@bot.callback_query_handler(func=lambda call: call.data == "change_pass")
def change_user_pass(callback):
    bot.answer_callback_query(callback.id)
    user_id, _, email = get_callback_mail_info(callback)
    
    reply_msg = bot.send_message(user_id, "Введите старый пароль")
    return bot.register_next_step_handler(reply_msg, confirm_old_password, email)

def confirm_old_password(msg, email: str):
    user_id = msg.from_user.id
    old_pass = msg.text
    bot.delete_message(user_id, msg.id)
    
    if check_password(telegram_id=user_id, email=email, user_password=old_pass):
        reply_msg = bot.send_message(user_id, "Введите новый пароль")
        return bot.register_next_step_handler(reply_msg, change_pass, email)
    
    else:
        return bot.send_message(user_id, wrong_pass_msg)
    
def change_pass(msg, email: str):
    user_id = msg.from_user.id
    hashed_password = hash_password(user_id, msg.text)
    bot.delete_message(user_id, msg.id)
    
    mails.changePassword(email, hashed_password)
    
    return bot.send_message(user_id, "Пароль успешно изменён")

#^######################^#
#^###  Remove Email  ###^#
#^######################^#

@bot.callback_query_handler(func=lambda call: call.data == "remove_email")
def remove_user_mail(callback):
    bot.answer_callback_query(callback.id)
    user_id, _, email = get_callback_mail_info(callback)
    
    reply_msg = bot.send_message(user_id, confirm_password_msg)
    return bot.register_next_step_handler(reply_msg, remove_email, email)

def remove_email(msg, email: str):
    user_id = msg.from_user.id
    password = msg.text
    bot.delete_message(user_id, msg.id)
    
    if check_password(telegram_id=user_id, email=email, user_password=password):
        mails.removeByEmail(email)
        return bot.send_message(user_id, "Почта успешно удалена")
    
    else:
        return bot.send_message(user_id, wrong_pass_msg)

# TODO: add turn on/off email listen function

#*###################*#
#*####  PROFILE  ####*#
#*###################*#

# TODO: user emails list

@bot.message_handler(commands=['myemails'])
def myemails(msg):
    user_id = msg.from_user.id
    
    user_emails = mails.getEmailsByTelegramId(user_id)
    print(user_emails)
    
    get_mail_info
    
    user_info = """Список подключённых почт

"""
    
    return bot.send_message(user_id, user_info, parse_mode=parseMode)

# @bot.message_handler(commands=['profile'])
# def profile(msg):
#     user_id = msg.from_user.id

#     if not checkMail(user_id):
#         return bot.send_message(user_id, "You're not registered. Send /register to to create profile.", parse_mode="Markdown")

#     user_name = mailConf.get(str(user_id), 'username')
#     user_pass = mailConf.get(str(user_id), 'password')

#     email_info = f"""*Your email profile:*
# username - `{user_name}`
# password - `{user_pass}`
# """

#     return bot.send_message(user_id, email_info, parse_mode="Markdown")


# @bot.message_handler(commands=['runsession'])
# def update_mail(msg):
#     user_id = msg.from_user.id

#     if not checkMail(user_id):
#         return bot.send_message(user_id, "You're not registered. Send /register to to create profile.", parse_mode="Markdown")

#     user_host = mailConf.get(str(user_id), 'host')
#     user_name = mailConf.get(str(user_id), 'username')
#     user_pass = mailConf.get(str(user_id), 'password')

#     email_info = f"""*Email info:*
# username - `{user_name}`
# password - `{user_pass}`
# """

#     bot.send_message(user_id, f"Session is started.\n\n{email_info}\nSend /stopsession to finish session.", parse_mode="Markdown")

#     global proc
#     proc = True
#     mailParser.login(user_host, user_name, user_pass)

#     while proc:
#         photos, videos, music, docs = mailParser.get_mail_attaches()

#         for photo in photos:
#             bot.send_photo(user_id, photo, timeout=10000)

#         for video in videos:
#             bot.send_video(user_id, video, timeout=50000)

#         for mus in music:
#             bot.send_audio(user_id, mus, timeout=10000)

#         for doc in docs:
#             bot.send_document(user_id, doc, timeout=50000)

#         time.sleep(30)
    
#     return mailParser.logout()


# @bot.message_handler(commands=['stopsession'])
# def end_update(msg):
#     user_id = msg.from_user.id

#     if not checkMail(user_id):
#         return bot.send_message(user_id, "You're not registered. Send /register to to create profile.", parse_mode="Markdown")

#     global proc
#     proc = False

#     return bot.send_message(user_id, "Session is ended. Send /startsession to start session.", parse_mode="Markdown")


print("I'm ready!!")
bot.polling()