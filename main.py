#Общая часть
from aiogram                            import types, Dispatcher, Bot               #тип данных телеграмма, диспетчер, бот
from aiogram.utils                      import executor                             #Запускает работу диспетчера
from aiogram.types                      import KeyboardButton, ReplyKeyboardMarkup  #Модуль для работы с клавиатурой
from aiogram.dispatcher                 import FSMContext                           #Класс используется для того чтобы в handler'e указать машинное состояние
from aiogram.dispatcher.filters.state   import State, StatesGroup                   #
from aiogram.contrib.fsm_storage.memory import MemoryStorage                        #Класс позволяет хранить данные в оперативной памяти 
from functions                          import *                                    #
import os       #Импортирует модуль os, чтобы мы могли прочитать наш TOKEN
import re       #Модуль рег. выражений
import pymysql  #Модуль управления БД

storage = MemoryStorage()
bot = Bot(token = '5605614034:AAHNoNXooC9AN-cXT2auLennD0qlfVFxsKY') #Токен бота
dp = Dispatcher(bot, storage=storage)                               #Передан экземпляр нашего бота

#Создание этапов для нового напоминания
class FSMCreateReminder(StatesGroup):
    description = State()   #Этап создания описания
    date_and_time = State() #Этап создания даты и время

#Создание этапов для удаления напоминания
class FSMDeleteReminder(StatesGroup):
    choice = State()   #Этап  

@dp.message_handler()                            #Означает событие, когда в наш чат кто-то что-то пишет
async def echo_message(message : types.Message): #Функция которая принимает смс от пользователя
    #Начать использование
    if re.fullmatch('/start', message.text):
        keyboard = ReplyKeyboardMarkup(resize_keyboard = True).add(KeyboardButton('Создать напоминание')).add(KeyboardButton('Мои напоминания'))
        await bot.send_message(chat_id= message.from_user.id, text='Привет.\nБот создан чтобы напомнить вам о ваших запланированных делах, которые вы можете добавлять в свой список напоминаний.', reply_markup=keyboard)


    #Создать напоминание
    elif re.fullmatch('Создать напоминание', message.text):
        keyboard = ReplyKeyboardMarkup(resize_keyboard = True).add(KeyboardButton('Меню')) #Создание клавиатурных кнопок
        #Создание состояния
        await FSMCreateReminder.description.set()
        await message.reply('Напишите о чем вам напомнить.') 
    #Мои напоминания
    elif re.fullmatch('Мои напоминания', message.text):
        keyboard = ReplyKeyboardMarkup(resize_keyboard = True).add(KeyboardButton('Редактировать')).add(KeyboardButton('Удалить')).add(KeyboardButton('Меню')) 
        await bot.send_message(chat_id= message.from_user.id, text='Список ваших напоминаний:', reply_markup=keyboard) #Отправка сообщения пользователю
        #Подключение базы данных
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='qwert123',
            database='reminder_bot_bd',
            cursorclass=pymysql.cursors.DictCursor
        )    
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM reminder_bot_bd.info_table WHERE `user_id` = '{message.from_user.id}' ORDER BY `date` ASC, `time` ASC")
            bd = cursor.fetchall()
            ansMsg = ''
            for i in range(len(bd)):
                ansMsg += str(i+1) + '. ' + bd[i]['date'] + ' ' + bd[i]['description'] + ' в ' + bd[i]['time'] + '\n'
            await message.answer(ansMsg)
        connection.close()
    #Удалить напоминание
    elif re.fullmatch('Удалить', message.text):
        keyboard = ReplyKeyboardMarkup(resize_keyboard = True).add(KeyboardButton('Меню')) #Создание клавиатурных кнопок
        await FSMDeleteReminder.choice.set()
        await message.answer('Выберите напоминание по списку, которое хотите удалить.')

    #Ловим первый ответ для создания напоминания 
    #Этап 1, создания описания
    @dp.message_handler(state=FSMCreateReminder.description)
    async def load_description(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['description'] = message.text
        #Вызов формы для заполнения даты и времени напоминания    
        form = mode_inline_keyboard()
        await bot.send_message(message.from_user.id, 'Форма заполнения даты и времени', reply_markup=form)
        #Переход в след. машинное состояние FSMCreateReminder.date_and_time
        await FSMCreateReminder.next()

    #Этап 2, создания даты и время
    @dp.callback_query_handler(state=FSMCreateReminder.date_and_time)
    async def buttons(call: types.CallbackQuery, state: FSMContext):
        #Изменение месяца
        if call.data.split('_')[1] == 'month':
            months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
            inlkb = mode_inline_keyboard(months[int(call.data.split('_')[0])], 'save_monthResult', 3, call['message']['reply_markup'])
            await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inlkb)
        #Изменение года
        elif call.data.split('_')[1] == 'year':
            if call.data.split('_')[0] == 'plus':
                inlkb = mode_inline_keyboard(str(int(call['message']['reply_markup']['inline_keyboard'][1][0]['text'])+1), 'save_yearResult', 1, call['message']['reply_markup'])
                await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inlkb)

            if call.data.split('_')[0] == 'minus':
                inlkb = mode_inline_keyboard(str(int(call['message']['reply_markup']['inline_keyboard'][1][0]['text'])-1), 'save_yearResult', 1, call['message']['reply_markup'])
                await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inlkb)
        #Изменение дня
        elif call.data.split('_')[1] == 'day':
            if call.data.split('_')[0] == 'plus':
                inlkb = mode_inline_keyboard(str(int(call['message']['reply_markup']['inline_keyboard'][8][0]['text'])+1), 'save_dayResult', 8, call['message']['reply_markup'])
                await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inlkb)

            if call.data.split('_')[0] == 'minus':
                inlkb = mode_inline_keyboard(str(int(call['message']['reply_markup']['inline_keyboard'][8][0]['text'])-1), 'save_dayResult', 8, call['message']['reply_markup'])
                await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inlkb)
        #Изменение часа
        elif call.data.split('_')[1] == 'hour':
            if call.data.split('_')[0] == 'plus':
                inlkb = mode_inline_keyboard(str(int(call['message']['reply_markup']['inline_keyboard'][10][0]['text'])+1), 'save_dayResult', 10, call['message']['reply_markup'])
                await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inlkb)

            if call.data.split('_')[0] == 'minus':
                inlkb = mode_inline_keyboard(str(int(call['message']['reply_markup']['inline_keyboard'][10][0]['text'])-1), 'save_dayResult', 10, call['message']['reply_markup'])
                await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inlkb)
        #Изменение минут
        elif call.data.split('_')[1] == 'minute':
            if call.data.split('_')[0] == 'plus':
                inlkb = mode_inline_keyboard(str(int(call['message']['reply_markup']['inline_keyboard'][11][0]['text'])+1), 'save_dayResult', 11, call['message']['reply_markup'])
                await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inlkb)

            if call.data.split('_')[0] == 'minus':
                inlkb = mode_inline_keyboard(str(int(call['message']['reply_markup']['inline_keyboard'][11][0]['text'])-1), 'save_dayResult', 11, call['message']['reply_markup'])
                await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=inlkb)
        #Сохранение
        elif call.data == 'save_but':
            # Дата для БД
            months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
            day = call['message']['reply_markup']['inline_keyboard'][8][0]['text']
            month = str(months.index(call['message']['reply_markup']['inline_keyboard'][3][0]['text'])+1)
            if len(call['message']['reply_markup']['inline_keyboard'][8][0]['text']) == 1:
                day = '0' + call['message']['reply_markup']['inline_keyboard'][8][0]['text']
            if len(str(months.index(call['message']['reply_markup']['inline_keyboard'][3][0]['text']))) == 1:
                month = '0' + str(months.index(call['message']['reply_markup']['inline_keyboard'][3][0]['text'])+1)
            #Конец состояния и сохранение в БД
            async with state.proxy() as data:
                #Добавление даты
                data['date'] = day + '.' + month + '.' + call['message']['reply_markup']['inline_keyboard'][1][0]['text']
                #Добавление времени
                data['time'] = call['message']['reply_markup']['inline_keyboard'][10][0]['text'] + ':' + call['message']['reply_markup']['inline_keyboard'][11][0]['text']
                await message.answer('Ваше напоминание создано: ' + data['date'] + ', ' + data['description'] + ' в ' + data['time'] + '.')   
                #Сохранение напоминания в БД
                #Подключение БД
                connection = pymysql.connect(
                    host='localhost',
                    port=3306,
                    user='root',
                    password='qwert123',
                    database='reminder_bot_bd',
                    cursorclass=pymysql.cursors.DictCursor
                )
                #Запись в БД
                with connection.cursor() as cursor:
                    cursor.execute(f"INSERT INTO reminder_bot_bd.info_table VALUES ('{message.from_user.id}', '{data['date']}', '{data['time']}', '{data['description']}')")
                    connection.commit()
                connection.close()
            #Закрыть состояние
            await state.finish()  
    #Ловим ответ на удаление
    @dp.message_handler(state=FSMDeleteReminder.choice)
    async def load_choice(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['choice'] = message.text
            #Подключение базы данных
            connection = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='qwert123',
                database='reminder_bot_bd',
                cursorclass=pymysql.cursors.DictCursor
            )    
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM reminder_bot_bd.info_table WHERE `user_id` = '{message.from_user.id}' ORDER BY `date` ASC, `time` ASC")
                bd = cursor.fetchall()
                #ansMsg = 'Ваш список напоминаний: \n'
                flag = False
                for i in range(len(bd)):
                    if (i+1) == int(data['choice']):
                        cursor.execute(f"DELETE FROM reminder_bot_bd.info_table WHERE `user_id` = '{message.from_user.id}' AND `date` = '{bd[i]['date']}' AND `time` = '{bd[i]['time']}' AND `description` = '{bd[i]['description']}'")
                        connection.commit()
                        keyboard = ReplyKeyboardMarkup(resize_keyboard = True).add(KeyboardButton('Создать напоминание')).add(KeyboardButton('Мои напоминания'))
                        await bot.send_message(chat_id= message.from_user.id, text='Это напоминание успешно удалено', reply_markup=keyboard)
                        ansMsg = 'Ваш новый список напоминаний: \n'
                        for i in range(len(bd)):
                            ansMsg += str(i+1) + '. ' + bd[i]['date'] + ' ' + bd[i]['description'] + ' в ' + bd[i]['time'] + '\n'
                        flag = True
                        
                # if flag == False:
                #     message.answer('К сожалению такого напоминания нет в списке, попробуйте еще раз.')
            connection.close()
        #Закрыть состояние
        await state.finish() 
    #Редактировать напоминание
    # elif re.fullmatch('Редактировать', message.text):
    #     await message.answer('Выберите напоминание по списку, которое хотите редактировать.')
    # #Выход в главное меню
    # elif re.fullmatch('Меню', message.text):
    #     keyboard = ReplyKeyboardMarkup(resize_keyboard = True).add(KeyboardButton('Создать напоминание')).add(KeyboardButton('Мои напоминания'))
    #     await message.answer('Вы вернулись в главное меню')
    # #Вывод несуществующих команд
    # else:
        # await message.answer('Возможно вы ввели неправильную команду.')

    

            # await bot.send_message(call.from_user.id, 'Введите описание напоминания: ')
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