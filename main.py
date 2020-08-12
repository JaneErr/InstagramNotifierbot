#!venv/bin/python
import logging
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from sqlighter import SQLighter

from instagramwebapi import InstagramWebApi

logging.basicConfig(level=logging.INFO)

bot = Bot(token="1277931217:AAE9F3m_XTEG0KYt6nec3cRG06YMN1uPuVU")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = SQLighter()

instagramapi = InstagramWebApi()

class States(StatesGroup):
    subscribe_waiting_for_instagram_username = State()
    unsubscribe_waiting_for_instagram_username = State()

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    if (not db.user_exists(message.from_user.id)):
        db.add_user(message.from_user.id)

    await message.answer("Добро пожаловать!")

@dp.message_handler(commands=["subscribe"], state="*")
async def cmd_subscribe(message: types.Message):
    await message.answer("Введите никнейм пользователя в Instagram")
    await States.subscribe_waiting_for_instagram_username.set()


@dp.message_handler(state=States.subscribe_waiting_for_instagram_username, content_types=types.ContentTypes.TEXT)
async def subscribe_step_2(message: types.Message, state: FSMContext):
    if (instagramapi.userExist(message.text)):
        username = message.text
        id = instagramapi.getUserId(username)
        
        if (not db.instagram_user_exists(username)):
            last_post_id = instagramapi.getLastPostId(id)
            db.add_instagram_user(username, last_post_id, id)
        
        if (not db.subscriptions_exist(message.from_user.id, username)):
            db.subscribe(message.from_user.id, username)
            await message.answer("Вы подписались на https://www.instagram.com/" + message.text)
        else:
            await message.answer("Вы уже подписаны на https://www.instagram.com/" + message.text)
    else:
        await message.answer('Пользователь не найден. Попробуйте еще раз.')

    await state.finish()

@dp.message_handler(commands=["unsubscribe"], state="*")
async def cmd_unsubscribe(message: types.Message):
    await message.answer("Введите никнейм пользователя в Instagram")
    await States.unsubscribe_waiting_for_instagram_username.set()

@dp.message_handler(state=States.unsubscribe_waiting_for_instagram_username, content_types=types.ContentTypes.TEXT)
async def unsubscribe_step_2(message: types.Message, state: FSMContext):
    username = message.text
    if (db.instagram_user_exists(username)):
        if (db.subscriptions_exist(message.from_user.id, username)):
            db.unsubscribe(message.from_user.id, username)
            await message.answer("Вы отписались от https://www.instagram.com/" + message.text)
        else:
            await message.answer("Вы не подписаны на https://www.instagram.com/" + message.text)
    else:
        await message.answer("Пользователь не найден.")
    
    await state.finish()

@dp.message_handler(commands=["subscriptions"])
async def cmd_subscriptions(message: types.Message):
    users = db.get_subscriptions(message.from_user.id)
    if (bool(len(users))):
        list = []
        for user in users:
            list.append('<a href="https://www.instagram.com/' + user[0] + '">' + user[0] + '</a>')
        await message.answer("Вы подписаны на пользователей:\n" + '\n'.join(list), parse_mode="HTML")
    else:
        await message.answer("У вас нет подписок")

@dp.message_handler(commands=["test"])
async def cmd_test(message: types.Message):
    print(db.get_all_instagram_user_id())

async def mailing(timing):
    while True:
        await asyncio.sleep(timing)

        userlist = db.get_all_instagram_user_id()
        for user in userlist:
            last_post_id = instagramapi.getLastPostId(user[0])
            if (last_post_id != db.get_instagram_last_post_id(user[0])):
                last_post = instagramapi.getLastPost(user[0])
                users = db.get_subscribers(user[0])
                for u in users:
                    if (last_post['type'] == 'video'):
                        await bot.send_video(u[0], video=last_post['content'], caption=last_post['caption'], parse_mode='HTML')
                    else:
                        await bot.send_photo(u[0], photo=last_post['content'], caption=last_post['caption'], parse_mode='HTML')
                db.update_last_post_id(last_post_id,user[0])

if __name__ == "__main__":
    dp.loop.create_task(mailing(30))
    executor.start_polling(dp, skip_updates=True)