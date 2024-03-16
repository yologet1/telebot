import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import time
import logging

TOKEN = "6022409228:AAGbNGISgdiREWtNU5GXIv-u8Nh1OPmg3Zs"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

# Создаем базу данных
conn = sqlite3.connect('words2.db')
c = conn.cursor()

# Проверяем, существует ли таблица
c.execute('''CREATE TABLE IF NOT EXISTS words
             (word text, meaning text)''')
conn.commit()
conn.close()

question_limit = 30
asked_questions = 0
correct_answers = 0
incorrect_answers = 0

async def get_random_word():
    conn = sqlite3.connect('words2.db')
    c = conn.cursor()
    c.execute("SELECT * FROM words ORDER BY RANDOM() LIMIT 1")
    word, meaning = c.fetchone()
    conn.close()
    return word, meaning

async def get_random_meanings(n):
    conn = sqlite3.connect('words2.db')
    c = conn.cursor()
    c.execute(f"SELECT meaning FROM words ORDER BY RANDOM() LIMIT {n}")
    meanings = [row[0] for row in c.fetchall()]
    conn.close()
    return meanings

async def send_question(message: types.Message):
    global asked_questions
    if asked_questions >= question_limit:
        await bot.send_message(message.chat.id, f"Вы ответили на все вопросы. Викторина завершена. Правильных ответов: {correct_answers}, Неправильных ответов: {incorrect_answers}")
        return

    word, correct_meaning = await get_random_word()
    incorrect_meanings = await get_random_meanings(2)
    options = [correct_meaning] + incorrect_meanings
    random.shuffle(options)
    keyboard = InlineKeyboardMarkup()
    for option in options:
        if option == correct_meaning:
            keyboard.add(InlineKeyboardButton(option, callback_data='correct'))
        else:
            keyboard.add(InlineKeyboardButton(option, callback_data='incorrect'))
    await bot.send_message(message.chat.id, f'К чему подходит данное описание "{word}"?', reply_markup=keyboard)
    asked_questions += 1

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    global asked_questions, correct_answers, incorrect_answers
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    logging.info(f'{user_id=} {user_full_name=}', {time.asctime()})
    await message.reply(f"Привет, {user_full_name}! Я бот, который поможет тебе запомнить слова и их значения.")
    asked_questions = 0  # Сброс счетчика вопросов при старте
    correct_answers = 0  # Сброс счетчика правильных ответов при старте
    incorrect_answers = 0  # Сброс счетчика неправильных ответов при старте

@dp.message_handler(commands=['subject1'])
async def quiz_handler(message: types.Message):
    await send_question(message)  # Задаем первый вопрос

@dp.callback_query_handler(lambda c: c.data == 'correct')
async def correct_answer_handler(callback_query: types.CallbackQuery):
    global correct_answers
    correct_answers += 1
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Правильно!')
    await send_question(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == 'incorrect')
async def incorrect_answer_handler(callback_query: types.CallbackQuery):
    global incorrect_answers
    incorrect_answers += 1
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Неправильно!')
    await send_question(callback_query.message)

# Функция для запуска бота
async def run_polling():
    await dp.start_polling()

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp)


















