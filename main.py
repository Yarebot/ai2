import telebot
from telebot import types

# --- НАСТРОЙКИ ---
TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Вставь сюда токен от BotFather
ADMIN_ID = 123456789            # Вставь сюда СВОЙ цифровой ID (не юзернейм!)

bot = telebot.TeleBot(TOKEN)

# --- ДАННЫЕ ОПРОСА ---
# Структура: вопрос и варианты ответов
SURVEY_DATA = [
    # Раздел 1
    {
        "section": "Раздел 1. О вас",
        "question": "1. Ваш пол:",
        "options": ["Мужской", "Женский"]
    },
    {
        "section": "Раздел 1. О вас",
        "question": "2. Ваш возраст:",
        "options": ["До 14 лет", "14–17 лет", "18–24 года", "25–34 года", "35–44 года", "45–54 года", "55+"]
    },
    # Раздел 2
    {
        "section": "Раздел 2. Интернет сегодня",
        "question": "3. Как изменился интернет в РФ за последний год?",
        "options": ["Стал лучше", "Без изменений", "Стал немного хуже", "Стал значительно хуже", "Затрудняюсь"]
    },
    {
        "section": "Раздел 2. Интернет сегодня",
        "question": "4. Как часто вы используете VPN/Proxy?",
        "options": ["Постоянно", "Часто (ежедневно)", "Редко", "Никогда / Не умею"]
    },
    # Раздел 3
    {
        "section": "Раздел 3. Будущее Рунета",
        "question": "5. Вероятный сценарий развития на 5 лет:",
        "options": ["Полная изоляция (Интранет)", "«Китайский вариант»", "Суверенный, но открытый", "Либерализация", "Другое"]
    },
    {
        "section": "Раздел 3. Будущее Рунета",
        "question": "6. Главная цель «суверенного интернета»:",
        "options": ["Защита от киберугроз", "Политическая цензура", "Поддержка IT-компаний", "Техническая необходимость"]
    },
    # Раздел 4
    {
        "section": "Раздел 4. Импортозамещение",
        "question": "7. Готовы ли отказаться от YouTube/Google в пользу наших аналогов? (1-нет, 5-да)",
        "options": ["1 (Не готов)", "2", "3", "4", "5 (Полностью готов)"]
    },
    {
        "section": "Раздел 4. Импортозамещение",
        "question": "8. Как ограничение глобальной сети повлияет на вас?",
        "options": ["Станет невозможной работа/учеба", "Серьезные трудности", "Незначительно", "Не повлияет"]
    },
    {
        "section": "Раздел 4. Импортозамещение",
        "question": "9. Отношение к гос. браузеру и сертификатам:",
        "options": ["Положительно", "Нейтрально", "Отрицательно", "Мне всё равно"]
    },
    # Раздел 5
    {
        "section": "Раздел 5. Итоги",
        "question": "10. Поможет ли изоляция развитию IT в РФ?",
        "options": ["Да, даст импульс", "Нет, будет застой", "Усилит отток кадров", "Сложно сказать"]
    },
    {
        "section": "Раздел 5. Итоги",
        "question": "11. Что вызывает наибольшее беспокойство?",
        "options": ["Рост цен", "Отсутствие объективной инфо", "Потеря контента", "Скорость соединения", "Утечки данных", "Ничего не беспокоит"]
    }
]

# Хранилище ответов: {chat_id: [ответ_0, ответ_1, ...]}
user_answers = {}

# --- ЛОГИКА ---

@bot.message_handler(commands=['start'])
def start_survey(message):
    # Очищаем старые ответы пользователя
    user_answers[message.chat.id] = []
    
    text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "🌐 **Тема опроса:** Будущее интернета в России: изоляция или развитие.\n"
        "Опрос анонимный, займет 1 минуту."
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 Начать опрос", callback_data="start"))
    
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# Обработчик кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    
    # Если нажали старт
    if call.data == "start":
        user_answers[chat_id] = [] # Сброс
        send_question(chat_id, call.message.message_id, 0)
        return

    # Если нажали вариант ответа (формат 'ans_номерВопроса_номерОтвета')
    if call.data.startswith("ans_"):
        parts = call.data.split('_')
        q_index = int(parts[1])
        ans_index = int(parts[2])
        
        # Сохраняем ответ (текст ответа)
        selected_option = SURVEY_DATA[q_index]['options'][ans_index]
        # Проверяем, не отвечал ли пользователь уже на этот вопрос (защита от дабл-клика)
        if len(user_answers.get(chat_id, [])) == q_index:
             user_answers[chat_id].append(selected_option)
        
        # Следующий вопрос
        next_q = q_index + 1
        
        if next_q < len(SURVEY_DATA):
            send_question(chat_id, call.message.message_id, next_q)
        else:
            finish_survey(chat_id, call.message.message_id, call.from_user)

# Функция отправки/обновления вопроса
def send_question(chat_id, message_id, index):
    data = SURVEY_DATA[index]
    
    text = f"📋 *{data['section']}*\n\n**{data['question']}**"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    # Генерируем кнопки
    for i, option in enumerate(data['options']):
        markup.add(types.InlineKeyboardButton(option, callback_data=f"ans_{index}_{i}"))
    
    bot.edit_message_text(
        chat_id=chat_id, 
        message_id=message_id, 
        text=text, 
        reply_markup=markup, 
        parse_mode="Markdown"
    )

# Финал опроса + Отправка отчета админу
def finish_survey(chat_id, message_id, user_info):
    answers = user_answers.get(chat_id, [])
    
    # 1. Показываем пользователю благодарность
    final_text = (
        "✅ **Спасибо! Ваши ответы приняты.**\n\n"
        "Мы учтем ваше мнение при анализе будущего Рунета."
    )
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=final_text, reply_markup=None, parse_mode="Markdown")
    
    # 2. Формируем отчет для Админа
    username = f"@{user_info.username}" if user_info.username else "Нет юзернейма"
    user_link = f"[{user_info.first_name}](tg://user?id={user_info.id})"
    
    report = f"📊 **НОВЫЙ ОТВЕТ НА ОПРОС**\n"
    report += f"👤 Пользователь: {user_link} ({username})\n"
    report += "-" * 20 + "\n"
    
    for i, ans in enumerate(answers):
        q_text = SURVEY_DATA[i]['question']
        report += f"❓ {i+1}. {q_text}\n💡 **{ans}**\n\n"
        
    # 3. Отправляем отчет админу
    try:
        bot.send_message(ADMIN_ID, report, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка отправки админу: {e}")

# Запуск
if __name__ == '__main__':
    print("Бот опроса запущен...")
    bot.infinity_polling()


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
