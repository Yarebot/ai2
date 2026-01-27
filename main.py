import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
# Вставьте сюда ваш токен от BotFather
BOT_TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"

# Вставьте сюда ВАШ цифровой ID (получить у @userinfobot)
# Бот будет присылать ответы именно сюда.
ADMIN_ID = 123456789 

# --- ЛОГИРОВАНИЕ ---
logging.basicConfig(level=logging.INFO)

# --- СОСТОЯНИЯ (FSM) ---
class Survey(StatesGroup):
    gender = State()
    age = State()
    internet_change = State()
    vpn_usage = State()
    future_scenario = State()
    sovereign_goal = State()
    substitution_ready = State()
    isolation_impact = State()
    gov_browser = State()
    it_development = State()
    concerns = State()

# --- ИНИЦИАЛИЗАЦИЯ ---
router = Router()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def make_keyboard(items: list[str], adjust: int = 1):
    """Создает клавиатуру из списка строк"""
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(text=item, callback_data=item[:30]) # callback_data ограничен 64 байтами
    builder.adjust(adjust)
    return builder.as_markup()

# --- ХЕНДЛЕРЫ (ОБРАБОТЧИКИ) ---

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Этот бот поможет нам собрать статистику по развитию Рунета. "
        "Опрос полностью анонимный.\n\n"
        "📊 <b>Раздел 1: О вас</b>", 
        parse_mode="HTML"
    )
    
    await message.answer(
        "1. Ваш пол:",
        reply_markup=make_keyboard(["Мужской", "Женский"], 2)
    )
    await state.set_state(Survey.gender)

# 1 -> 2
@router.callback_query(Survey.gender)
async def process_gender(callback: CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data) # Сохраняем ответ (берем из текста кнопки для простоты)
    # Текст кнопки может быть обрезан в callback_data, поэтому лучше брать label, 
    # но для простого примера берем data, так как ключи уникальны.
    # В идеале нужно мапить callback_data на полный ответ. 
    # Здесь для упрощения мы сохраним то, что пришло в callback (первые 30 символов).
    # Для красоты возьмем полный текст из сообщения, на которое нажали (сложнее), 
    # или просто передадим список вариантов заново.
    
    # Чтобы сохранить полный текст ответа, сделаем хитрее:
    full_answer = [b.text for row in callback.message.reply_markup.inline_keyboard for b in row if b.callback_data == callback.data][0]
    await state.update_data(gender=full_answer)

    await callback.answer()
    await callback.message.edit_text(f"✅ Пол: {full_answer}")

    await callback.message.answer(
        "2. Ваш возраст:",
        reply_markup=make_keyboard([
            "до 14 лет", "14–17 лет", "18–24 года", 
            "25–34 года", "35–44 года", "45–54 года", 
            "55 лет и старше"
        ], 2)
    )
    await state.set_state(Survey.age)

# 2 -> 3
@router.callback_query(Survey.age)
async def process_age(callback: CallbackQuery, state: FSMContext):
    full_answer = [b.text for row in callback.message.reply_markup.inline_keyboard for b in row if b.callback_data == callback.data][0]
    await state.update_data(age=full_answer)
    await callback.answer()
    await callback.message.edit_text(f"✅ Возраст: {full_answer}")

    await callback.message.answer("📊 <b>Раздел 2: Оценка текущей ситуации</b>", parse_mode="HTML")
    await callback.message.answer(
        "3. Как вы оцениваете изменения в работе интернета в России за последний год?",
        reply_markup=make_keyboard([
            "Стало значительно лучше",
            "Ничего не изменилось",
            "Стало немного хуже",
            "Стало значительно хуже",
            "Затрудняюсь ответить"
        ], 1)
    )
    await state.set_state(Survey.internet_change)

# 3 -> 4
@router.callback_query(Survey.internet_change)
async def process_internet_change(callback: CallbackQuery, state: FSMContext):
    full_answer = [b.text for row in callback.message.reply_markup.inline_keyboard for b in row if b.callback_data == callback.data][0]
    await state.update_data(internet_change=full_answer)
    await callback.answer()
    await callback.message.edit_text(f"✅ Оценка: {full_answer}")

    await callback.message.answer(
        "4. Как часто вы используете средства обхода блокировок (VPN и др.)?",
        reply_markup=make_keyboard([
            "Постоянно",
            "Часто",
            "Редко",
            "Никогда / Не умею"
        ], 1)
    )
    await state.set_state(Survey.vpn_usage)

# 4 -> 5
@router.callback_query(Survey.vpn_usage)
async def process_vpn(callback: CallbackQuery, state: FSMContext):
    full_answer = [b.text for row in callback.message.reply_markup.inline_keyboard for b in row if b.callback_data == callback.data][0]
    await state.update_data(vpn_usage=full_answer)
    await callback.answer()
    await callback.message.edit_text(f"✅ VPN: {full_answer}")

    await callback.message.answer("📊 <b>Раздел 3: Сценарии будущего</b>", parse_mode="HTML")
    await callback.message.answer(
        "5. Какой сценарий развития Рунета в ближайшие 5 лет кажется вам наиболее вероятным?",
        reply_markup=make_keyboard([
            "Полная изоляция (интранет)",
            "«Китайский вариант»",
            "Суверенный, но открытый",
            "Либерализация",
            "Другое"
        ], 1)
    )
    await state.set_state(Survey.future_scenario)

# 5 -> 6
@router.callback_query(Survey.future_scenario)
async def process_scenario(callback: CallbackQuery, state: FSMContext):
    full_answer = [b.text for row in callback.message.reply_markup.inline_keyboard for b in row if b.callback_data == callback.data][0]
    await state.update_data(future_scenario=full_answer)
    await callback.answer()
    await callback.message.edit_text(f"✅ Сценарий: {full_answer}")

    await callback.message.answer(
        "6. В чем, по вашему мнению, главная цель закона о «суверенном интернете»?",
        reply_markup=make_keyboard([
            "Защита от киберугроз",
            "Цензура и контроль",
            "Поддержка IT-компаний",
            "Техническая необходимость"
        ], 1)
    )
    await state.set_state(Survey.sovereign_goal)

# 6 -> 7
@router.callback_query(Survey.sovereign_goal)
async def process_goal(callback: CallbackQuery, state: FSMContext):
    full_answer = [b.text for row in callback.message.reply_markup.inline_keyboard for b in row if b.callback_data == callback.data][0]
    await state.update_data(sovereign_goal=full_answer)
    await callback.answer()
    await callback.message.edit_text(f"✅ Цель: {full_answer}")

    await callback.message.answer("📊 <b>Раздел 4: Импортозамещение и сервисы</b>", parse_mode="HTML")
    await callback.message.answer(
        "7. Готовы ли вы отказаться от зарубежных платформ в пользу российских?\n(1 - Не готов, 5 - Готов)",
        reply_markup=make_keyboard(["1", "2", "3", "4", "5"], 5)
    )
    await state.set_state(Survey.substitution_ready)

# 7 -> 8
@router.callback_query(Survey.substitution_ready)
async def process_substitution(callback: CallbackQuery, state: FSMContext):
    await state.update_data(substitution_ready=callback.data)
    await callback.answer()
    await callback.message.edit_text(f"✅ Готовность: {callback.data}")

    await callback.message.answer(
        "8. Если доступ к глобальному интернету перекроют, как это повлияет на вашу работу/учебу?",
        reply_markup=make_keyboard([
            "Станет невозможной",
            "Серьезные трудности",
            "Повлияет незначительно",
            "Никак не повлияет"
        ], 1)
    )
    await state.set_state(Survey.isolation_impact)

# 8 -> 9
@router.callback_query(Survey.isolation_impact)
async def process_impact(callback: CallbackQuery, state: FSMContext):
    full_answer = [b.text for row in callback.message.reply_markup.inline_keyboard for b in row if b.callback_data == callback.data][0]
    await state.update_data(isolation_impact=full_answer)
    await callback.answer()
    await callback.message.edit_text(f"✅ Влияние: {full_answer}")

    await callback.message.answer(
        "9. Ваше отношение к созданию единого гос. браузера и сертификатов шифрования?",
        reply_markup=make_keyboard([
            "Положительно",
            "Нейтрально",
            "Отрицательно",
            "Мне все равно"
        ], 1)
    )
    await state.set_state(Survey.gov_browser)

# 9 -> 10
@router.callback_query(Survey.gov_browser)
async def process_browser(callback: CallbackQuery, state: FSMContext):
    full_answer = [b.text for row in callback.message.reply_markup.inline_keyboard for b in row if b.callback_data == callback.data][0]
    await state.update_data(gov_browser=full_answer)
    await callback.answer()
    await callback.message.edit_text(f"✅ Отношение: {full_answer}")

    await callback.message.answer("📊 <b>Раздел 5: Итоги</b>", parse_mode="HTML")
    await callback.message.answer(
        "10. Поможет ли изоляция развитию российских IT-технологий?",
        reply_markup=make_keyboard([
            "Да, даст толчок",
            "Нет, приведет к застою",
            "Приведет к оттоку кадров",
            "Сложно сказать"
        ], 1)
    )
    await state.set_state(Survey.it_development)

# 10 -> 11
@router.callback_query(Survey.it_development)
async def process_dev(callback: CallbackQuery, state: FSMContext):
    full_answer = [b.text for row in callback.message.reply_markup.inline_keyboard for b in row if b.callback_data == callback.data][0]
    await state.update_data(it_development=full_answer)
    await callback.answer()
    await callback.message.edit_text(f"✅ Эффект: {full_answer}")

    # Вопрос 11. Для простоты реализации в Telegram делаем выбор самого главного фактора
    # (Множественный выбор значительно усложняет UX и код для такого примера)
    await callback.message.answer(
        "11. Что вызывает у вас НАИБОЛЬШЕЕ беспокойство?",
        reply_markup=make_keyboard([
            "Рост цен на интернет",
            "Отсутствие информации",
            "Потеря контента (игры/видео)",
            "Снижение скорости",
            "Утечки данных",
            "Ничего не беспокоит"
        ], 1)
    )
    await state.set_state(Survey.concerns)

# Финиш
@router.callback_query(Survey.concerns)
async def process_finish(callback: CallbackQuery, state: FSMContext, bot: Bot):
    full_answer = [b.text for row in callback.message.reply_markup.inline_keyboard for b in row if b.callback_data == callback.data][0]
    await state.update_data(concerns=full_answer)
    
    # Получаем все данные
    data = await state.get_data()
    user = callback.from_user
    username = f"@{user.username}" if user.username else "Скрыт"
    
    # Формируем отчет для админа
    report = (
        f"📝 <b>НОВЫЙ ОТВЕТ НА ОПРОС</b>\n"
        f"👤 Пользователь: {user.full_name} ({username}, ID: {user.id})\n\n"
        f"1. Пол: {data.get('gender')}\n"
        f"2. Возраст: {data.get('age')}\n"
        f"3. Изменения: {data.get('internet_change')}\n"
        f"4. VPN: {data.get('vpn_usage')}\n"
        f"5. Сценарий: {data.get('future_scenario')}\n"
        f"6. Цель суверенитета: {data.get('sovereign_goal')}\n"
        f"7. Отказ от зарубежного: {data.get('substitution_ready')}/5\n"
        f"8. Влияние на работу: {data.get('isolation_impact')}\n"
        f"9. Гос. браузер: {data.get('gov_browser')}\n"
        f"10. Развитие IT: {data.get('it_development')}\n"
        f"11. Беспокойство: {data.get('concerns')}"
    )

    # Отправляем пользователю
    await callback.answer()
    await callback.message.edit_text(f"✅ Беспокойство: {full_answer}")
    await callback.message.answer("🎉 <b>Спасибо! Опрос завершен.</b> Ваши ответы записаны.", parse_mode="HTML")
    
    # Отправляем админу
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=report, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Не удалось отправить отчет админу: {e}")

    await state.clear()

# --- ЗАПУСК ---
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
