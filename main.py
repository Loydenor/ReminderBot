#Общая часть
from aiogram import types, Dispatcher
from aiogram.utils import executor
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram import Bot, Dispatcher
import os # Импортирует модуль os, чтобы мы могли прочитать наш TOKEN
import re
import pymysql

bot = Bot(token = '5605614034:AAHNoNXooC9AN-cXT2auLennD0qlfVFxsKY')
dp = Dispatcher(bot) # Передан экземпляр нашего бота


@dp.message_handler() #Означает событие, когда в наш чат кто-то что-то пишет
async def echo_message(message : types.Message): #Функция которая принимает смс от пользователя
    if re.fullmatch('/start', message.text):
        keyboard = ReplyKeyboardMarkup(resize_keyboard = True).add(KeyboardButton('/Создать_напоминание')).add(KeyboardButton('/Мои_напоминания'))
        await message.answer('Привет.\nБот создан чтобы напомнить вам о ваших запланированных делах, которые вы можете добавлять в свой список напоминаний.')
    
    elif re.fullmatch('/Создать_напоминание', message.text):
        await message.answer('Напишите о чем вам напомнить.')

    elif re.fullmatch('/Мои_напоминания', message.text):
        await message.answer('Список ваших напоминаний:')  
    

        # connection = pymysql.connect(
        #     host='localhost',
        #     port=3306,
        #     user='root',
        #     password='qwert123',
        #     database='reminder_bot_bd',
        #     cursorclass=pymysql.cursors.DictCursor
        # )
        
        # with connection.cursor() as cursor:
        #     try:
        #         cursor.execute(f"INSERT INTO reminder_bot_bd.info_table VALUES('{message.from_user.id}', '0', '0', 'fdf')")
        #         connection.commit()
        #     except: pass
        #     cursor.execute(f"SELECT * FROM reminder_bot_bd.info_table")
        #     bd = cursor.fetchall()
        #     print(bd)
        # connection.close()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)