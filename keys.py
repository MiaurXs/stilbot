from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


"""   Клавиатура   """
btn1K = KeyboardButton(text='Регистрация')
btn2K = KeyboardButton(text='Снять reviewer(a) - доступно только teamlead(у)')
btn3K = KeyboardButton(text='Назначить reviewer(a) - доступно только teamlead(у)')
btn4K = KeyboardButton(text='Удалить учётную запись')
#btn5K = KeyboardButton(text='Запланировать отпуск - доступно только teamlead(у)')
keyboardBtns = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2).add(btn1K,
                                                                                                  btn2K,
                                                                                                  btn3K,
                                                                                                  btn4K,
                                                                                                  #btn5K,
                                                                                                  )
# Resize_keyboard=True - позволяет автоматически уменьшить размер кнопок
# One_time_keyboard=True - убирает клавиатуру после нажатия на клавишу
# Row_width - количество кнопок в одном ряду
