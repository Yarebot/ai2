pip install aiogram google-generativeai aiohttp pillow
import asyncio
import logging
import sys
import aiohttp
from io import BytesIO

# Библиотеки Telegram (aiogram 3.x)
from aiogram import Bot, Dispatcher, Router, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatAction
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Библиотеки для AI и работы с картинками
import google.generativeai as genai
from PIL import Image

# --- КОНФИГУРАЦИЯ ---
# ⚠️ ВАЖНО: В реальном проекте храни ключи в файле .env
BOT_TOKEN = "8350320156:AAH4Ryko_kYDpR272jlIIjT5VF_i6k8T7Ig"
GEMINI_API_KEY = "AIzaSyDaVtOnQtBNBcS7CkWFxVDcEMY0o4Duf_Y"
NANO_BANANA_TOKEN = "AIzaSyDaVtOnQtBNBcS7CkWFxVDcEMY0o4Duf_Y"

# URL API (Нужно заменить на реальные, когда будут известны)
NANO_BANANA_URL_IMAGE = "https://api.nano-banana.com/v1/image" 
NANO_BANANA_URL_VIDEO = "https://api.nano-banana.com/v1/video"

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model_gemini = genai.GenerativeModel('gemini-1.5-flash')

# Роутер
router = Router()

# --- МАШИНА СОСТОЯНИЙ (FSM) ---
class BotStates(StatesGroup):
    chat_gemini = State()    # Режим простого общения
    generate_image = State() # Режим генерации картинок
    generate_video = State() # Режим генерации видео

# --- КЛАВИАТУРЫ ---
def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Чат с AI", callback_data="mode_text")],
        [
            InlineKeyboardButton(text="🎨 Нарисовать", callback_data="mode_image"),
            InlineKeyboardButton(text="🎬 Снять видео", callback_data="mode_video")
        ],
        [
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help"),
            InlineKeyboardButton(text="👤 О боте", callback_data="about")
        ]
    ])

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_home")]
    ])

# --- БАЗОВЫЕ КОМАНДЫ ---

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    text = (
        f"👋 Привет, <b>{html.quote(message.from_user.first_name)}</b>!\n\n"
        f"Я — <b>Nano Banana Bot</b> 🍌🤖.\n"
        f"Я умею общаться, видеть фото и генерировать контент.\n\n"
        f"👇 <i>Выбери действие в меню:</i>"
    )
    await message.answer(text, reply_markup=main_menu_kb())

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "🆘 <b>СПРАВКА</b>\n\n"
        "1. <b>Чат:</b> Пиши текстом, я отвечу (Gemini Flash).\n"
        "2. <b>Зрение:</b> Просто пришли мне фото в любой момент, и я опишу его.\n"
        "3. <b>Генерация:</b> Выбери режим в меню и пиши промпт.\n\n"
        "Команды:\n"
        "/start - Перезапуск бота"
    )
    await message.answer(text, reply_markup=back_kb())

# --- НАВИГАЦИЯ ПО МЕНЮ ---

@router.callback_query(F.data == "back_home")
async def go_home(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🏠 <b>Главное меню</b>", reply_markup=main_menu_kb())

@router.callback_query(F.data == "help")
async def cb_help(callback: CallbackQuery):
    await callback.message.edit_text(
        "🆘 <b>Инструкция</b>\nВыбери режим и следуй указаниям.\nЯ понимаю русский язык.",
        reply_markup=back_kb()
    )

@router.callback_query(F.data == "about")
async def cb_about(callback: CallbackQuery):
    await callback.message.edit_text(
        "👤 <b>О боте</b>\nВерсия: 2.0\nДвижок: aiogram + Gemini\nТокен: Nano Banana",
        reply_markup=back_kb()
    )

# --- ФУНКЦИЯ: ЗРЕНИЕ (РАБОТАЕТ ВСЕГДА) ---
@router.message(F.photo)
async def handle_photo_vision(message: Message, bot: Bot):
    # Эта функция срабатывает, если юзер прислал фото (независимо от режима)
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_PHOTO)
    
    # Скачиваем фото
    photo_file = await bot.download(message.photo[-1])
    image = Image.open(photo_file)
    
    # Если есть подпись к фото, используем её как вопрос
    prompt = message.caption if message.caption else "Что изображено на этом фото? Опиши подробно."
    
    wait_msg = await message.reply("👀 <i>Анализирую изображение...</i>")
    
    try:
        response = model_gemini.generate_content([prompt, image])
        await wait_msg.delete()
        await message.reply(response.text, parse_mode="Markdown")
    except Exception as e:
        await wait_msg.edit_text(f"⚠️ Ошибка зрения: {e}")

# --- РЕЖИМ 1: ТЕКСТОВЫЙ ЧАТ ---

@router.callback_query(F.data == "mode_text")
async def start_text(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.chat_gemini)
    await callback.message.edit_text(
        "💬 <b>Режим чата</b>\nПиши любой вопрос или тему:",
        reply_markup=back_kb()
    )

@router.message(BotStates.chat_gemini)
async def process_text_gemini(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    try:
        response = model_gemini.generate_content(message.text)
        await message.answer(response.text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

# --- РЕЖИМ 2: ГЕНЕРАЦИЯ ФОТО (NANO BANANA) ---

@router.callback_query(F.data == "mode_image")
async def start_image(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.generate_image)
    await callback.message.edit_text(
        "🎨 <b>Генерация Фото</b>\nОпиши, что нарисовать (на английском точнее):",
        reply_markup=back_kb()
    )

@router.message(BotStates.generate_image)
async def process_image_gen(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_PHOTO)
    wait_msg = await message.answer(f"🍌 Использую Nano Banana ({message.text})...")
    
    # СИМУЛЯЦИЯ ЗАПРОСА (Так как нет реального URL)
    try:
        # Здесь должен быть код:
        # async with aiohttp.ClientSession() as session:
        #     resp = await session.post(NANO_BANANA_URL_IMAGE, json={"prompt": message.text}, headers={"Authorization": NANO_BANANA_TOKEN})
        #     result = await resp.json()
        
        await asyncio.sleep(2) # Имитация работы
        
        # Заглушка, так как URL фейковый. В реальности тут был бы URL картинки.
        await wait_msg.edit_text(
            "⚠️ <b>Статус API:</b>\n"
            "Сервер Nano Banana не ответил (неверный URL).\n"
            "Но логика бота работает! Вставьте верный URL в переменную `NANO_BANANA_URL_IMAGE`.",
            reply_markup=back_kb()
        )
    except Exception as e:
        await wait_msg.edit_text(f"Ошибка API: {e}")

# --- РЕЖИМ 3: ГЕНЕРАЦИЯ ВИДЕО ---

@router.callback_query(F.data == "mode_video")
async def start_video(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.generate_video)
    await callback.message.edit_text(
        "🎬 <b>Генерация Видео</b>\nОпиши сцену для видео:",
        reply_markup=back_kb()
    )

@router.message(BotStates.generate_video)
async def process_video_gen(message: Message):
    await message.answer("🛠 Генерация видео временно недоступна (ожидание API Nano Banana).", reply_markup=back_kb())

# --- ЗАПУСК ---

async def main():
    # Включаем логирование, чтобы видеть ошибки в консоли
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    
    # Удаляем старые обновления (чтобы бот не отвечал на старые сообщения при запуске)
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("🚀 Nano Banana Bot запущен! Нажми /start в Telegram.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
