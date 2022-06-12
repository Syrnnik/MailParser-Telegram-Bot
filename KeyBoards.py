from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


off_content_btn = InlineKeyboardButton("Отключить содержимое", callback_data="off_content")
on_content_btn = InlineKeyboardButton("Включить содержимое", callback_data="on_content")

off_attaches_btn = InlineKeyboardButton("Отключить файлы", callback_data="off_attaches")
on_attaches_btn = InlineKeyboardButton("Включить файлы", callback_data="on_attaches")

change_email_btn = InlineKeyboardButton("Изменить адрес", callback_data="change_email")
change_pass_btn = InlineKeyboardButton("Изменить пароль", callback_data="change_pass")

remove_email_btn = InlineKeyboardButton("Удалить почту", callback_data="remove_email")


def getMailKeyboard(content: bool, attaches: bool, change_email: bool = True, change_pass: bool = True, remove_email: bool = True):
    keyboard = InlineKeyboardMarkup()
        
    if content:
        keyboard.add(off_content_btn)
    else:
        keyboard.add(on_content_btn)
        
    if attaches:
        keyboard.add(off_attaches_btn)
    else:
        keyboard.add(on_attaches_btn)
    
    if change_email:
        keyboard.add(change_email_btn)
        
    if change_pass:
        keyboard.add(change_pass_btn)
        
    if remove_email:
        keyboard.add(remove_email_btn)
        
    return keyboard
