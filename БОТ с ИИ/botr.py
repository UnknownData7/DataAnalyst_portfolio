import telebot
from telebot import types

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота, полученный от BotFather

bot = telebot.TeleBot(BOT_TOKEN)

# --- Данные о темах и категориях ---
themes_and_categories = {
    "Programming": ["books", "source", "cheatsheet", "python", "php", "html", "css", "js", "cPPlus", "c", "assembler", "wordpress", "api"],
    "Network": ["source", "tools", "cheatsheet", "commands"],
    "Pentest / Software": ["books", "source", "tools", "cheatsheet"],
    "Linux / Windows / AD": ["source", "tools", "cheatsheet", "commands", "ad", "windows", "powershell", "linux"],
    "Databases": ["books", "source", "tools", "sql", "nosql", "mysql", "postgresql", "mongodb"],
    "Revers / Malware dev": ["books", "malware", "revers"],
    "Steganography / Cryptography": ["books", "source", "tools", "crack", "crypto", "steganography"],
    "Servers / Docker": ["books", "source", "cheatsheet", "docker", "servers", "nginx", "waf"],
    "OSINT / Phishing": ["books", "source", "tools"]
}

# ---  Глобальные переменные для хранения данных поиска ---
search_theme = None
search_categories = []
search_description = None


# --- Обработчик команды /start ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    item_search = types.InlineKeyboardButton("Осуществить поиск 🔎", callback_data='start_search')
    markup.add(item_search)

    bot.send_message(message.chat.id,
                     "Здравствуйте! Чтобы найти нужный пост, нажмите кнопку под сообщением и следуйте инструкциям 👾🪬\n\n"
                     "ℹ️ Если у Вас возникнут сложности с использованием бота, то подробное руководство Вы найдете в Меню в разделе \"Помощь\"",
                     reply_markup=markup)

    # Устанавливаем меню команд
    set_commands(bot)


# --- Обработчик команды /help ---
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "Доступные команды:\n"
                                      "/start - Перезапуск бота\n"
                                      "/search - Осуществить поиск\n"
                                      "/help - Помощь")

# --- Обработчик команды /search ---
@bot.message_handler(commands=['search'])
def search_command(message):
    global search_theme, search_categories, search_description
    search_theme = None
    search_categories = []
    search_description = None
    ask_theme(message)


# --- Функция для задания вопроса о теме поиска ---
def ask_theme(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for theme in themes_and_categories.keys():
        item = types.InlineKeyboardButton(theme, callback_data=f'theme:{theme}')
        markup.add(item)

    bot.send_message(message.chat.id, "По какой теме хотите осуществить запрос?", reply_markup=markup)


# --- Функция для задания вопроса о категориях поиска ---
def ask_categories(message, theme):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for category in themes_and_categories[theme]:
        item = types.InlineKeyboardButton(category, callback_data=f'category:{category}')
        markup.add(item)

    item_next = types.InlineKeyboardButton("Далее", callback_data='next_categories')  # Кнопка "Далее"
    markup.add(item_next)  # Добавляем кнопку "Далее"

    bot.send_message(message.chat.id, f"По каким категориям производить запрос для темы '{theme}'?", reply_markup=markup)


# --- Функция для задания вопроса об описании поиска ---
def ask_description(message):
    bot.send_message(message.chat.id, "Опишите своими словами, что вы хотите найти:")
    bot.register_next_step_handler(message, process_description)  # Регистрируем следующий шаг


# --- Функция для обработки описания поиска ---
def process_description(message):
    global search_description
    search_description = message.text
    # Здесь можно добавить логику для сохранения или обработки введенной информации.

    categories_str = ", ".join(search_categories)
    response_text = "Спасибо! Ваш запрос получен, осуществляю поиск...\n"
    response_text += f"- Тема: {search_theme}\n"
    response_text += f"- Категории: {categories_str}\n"
    response_text += f"- Описание: {search_description}"

    bot.send_message(message.chat.id, response_text)

    # Сброс переменных для следующего поиска (опционально)
    # search_theme = None
    # search_categories = []
    # search_description = None


# --- Обработчик Inline Keyboard Callback Query ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global search_theme, search_categories

    if call.data == 'start_search':
        search_command(call.message)  # Вызываем команду /search
        bot.answer_callback_query(call.id, "Начинаем поиск...")

    elif call.data.startswith('theme:'):
        search_theme = call.data[6:]  # Обрезаем 'theme:'
        bot.answer_callback_query(call.id, f"Вы выбрали тему: {search_theme}")
        ask_categories(call.message, search_theme)  # Передаем выбранную тему функции ask_categories

    elif call.data.startswith('category:'):
        category = call.data[9:]  # Обрезаем 'category:'
        if category not in search_categories:
            search_categories.append(category)
            bot.answer_callback_query(call.id, f"Категория '{category}' добавлена")
        else:
            search_categories.remove(category)  # если уже есть в списке - удаляем
            bot.answer_callback_query(call.id, f"Категория '{category}' удалена")

        # редактируем сообщение с кнопками, чтобы пользователь видел, что выбрано
        markup = types.InlineKeyboardMarkup(row_width=2)
        for cat in themes_and_categories[search_theme]:
            item = types.InlineKeyboardButton(cat, callback_data=f'category:{cat}')
            if cat in search_categories:
                item.text = f"✅ {cat}"
            markup.add(item)
        item_next = types.InlineKeyboardButton("Далее", callback_data='next_categories')  # Кнопка "Далее"
        markup.add(item_next)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)



    elif call.data == 'next_categories':
        if search_theme and len(search_categories) > 0:  # Проверяем, выбрана ли тема и есть ли категории
            ask_description(call.message)  # Переходим к вопросу об описании
        else:
            bot.answer_callback_query(call.id,
                                      "Пожалуйста, выберите хотя бы одну категорию.")  # Сообщение, если не выбраны категории
            # (Опционально) Можно вернуть к выбору категорий или как-то выделить ошибку.


# --- Функция для установки меню команд ---
def set_commands(bot_instance):
    commands = [
        telebot.types.BotCommand("start", "Перезапуск бота"),
        telebot.types.BotCommand("search", "Осуществить поиск"),
        telebot.types.BotCommand("help", "Помощь")
    ]
    bot_instance.set_my_commands(commands)


# --- Запуск бота ---
if name == 'main':
    # Устанавливаем меню команд при запуске бота
    set_commands(bot)
    bot.polling(none_stop=True)