import asyncio
from aiogram import Bot, Dispatcher, F 
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder
import database
from dotenv import load_dotenv
import os
load_dotenv()


TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(TOKEN)
dp = Dispatcher()
pool = None

class FileStates(StatesGroup):
    waiting_photo = State()
    waiting_audio = State()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! 👋\n\n"

        "/get_photo — сохранить фото\n"
        "/send_photo — отправить фото\n\n"

        "/get_audio — сохранить аудио\n"
        "/send_audio — отправить аудио\n\n"

        "/files — мои файлы"
    )


# @dp.message(F.photo)
# async def send_foto(message: Message):
#     photo = message.photo[-1]
#     await message.answer_photo(photo=photo.file_id, caption=f"File id: {photo.file_id}")

@dp.message(F.video)
async def send_foto(message: Message):
    video = message.video
    await message.answer_video(video=video.file_id, caption=f"File id: {video.duration}")



@dp.message(Command("get_photo"))
async def get_photo_command(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        FileStates.waiting_photo
    )

    await message.answer(
        "📷 Отправь мне фотографию."
    )


@dp.message(FileStates.waiting_photo)
async def receive_photo(
    message: Message,
    state: FSMContext
):

    if not message.photo:

        await message.answer(
            "❌ Отправь именно фотографию."
        )

        return

    photo = message.photo[-1]

    await database.save_photo(
        pool,
        message.from_user.id,
        photo.file_id
    )

    await state.clear()

    await message.answer(
        "✅ Фото сохранено!"
    )


@dp.message(Command("send_photo"))
async def send_photo(message: Message):

    photo = await database.get_photo(
        pool,
        message.from_user.id
    )

    if not photo:

        await message.answer(
            "❌ У тебя нет сохранённого фото."
        )

        return
    photo_group = MediaGroupBuilder(caption="hi")
    for ph in photo:
        photo_group.add_photo(media=ph["file_id"])

    await message.answer_media_group(media=photo_group.build())


@dp.message(Command("get_audio"))
async def get_audio_command(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        FileStates.waiting_audio
    )

    await message.answer(
        "🎵 Отправь мне аудио."
    )


@dp.message(FileStates.waiting_audio)
async def receive_audio(
    message: Message,
    state: FSMContext
):

    if not message.audio:

        await message.answer(
            "❌ Отправь именно аудио."
        )

        return

    audio = message.audio

    await database.save_audio(
        pool,
        message.from_user.id,
        audio.file_id,
        audio.file_name
    )

    await state.clear()

    await message.answer(
        "✅ Аудио сохранено!"
    )


@dp.message(Command("send_audio"))
async def send_audio(message: Message):

    audio = await database.get_audio(
        pool,
        message.from_user.id
    )

    if not audio:

        await message.answer(
            "❌ У тебя нет сохранённого аудио."
        )

        return

    await message.answer_audio(
        audio=audio["file_id"],
        caption=audio["file_name"]
    )


@dp.message(Command("files"))
async def files(message: Message):

    files = await database.get_all_files(
        pool,
        message.from_user.id
    )

    if not files:

        await message.answer(
            "📁 У тебя нет файлов."
        )

        return

    text = "📁 Твои файлы:\n\n"

    for file in files:

        if file["file_type"] == "photo":

            text += (
                f"📷 Фото — ID: {file['id']}\n"
            )

        elif file["file_type"] == "audio":

            text += (
                f"🎵 {file['file_name']} "
                f"— ID: {file['id']}\n"
            )

    await message.answer(text)


async def main():

    global pool

    pool = await database.create_db()

    print("Bot started!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
