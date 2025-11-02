
import telebot
from telebot import types
import paramiko
import psycopg2
import sshtunnel
from sentence_transformers import SentenceTransformer, util
import torch
import os
import logging
import configparser

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Чтение конфигурационного файла
config = configparser.ConfigParser()
config.read('config.ini')

# Параметры SSH
ssh_host = config['SSH']['host']
ssh_user = config['SSH']['user']
ssh_pkey = config['SSH']['pkey']
ssh_port = int(config['SSH']['port'])

# Параметры PostgreSQL
db_host = config['PostgreSQL']['host']
db_name = config['PostgreSQL']['database']
db_user = config['PostgreSQL']['user']
db_password = config['PostgreSQL']['password']
db_port = int(config['PostgreSQL']['port'])

# Параметры Bot
BOT_TOKEN = config['Bot']['token']
VIDEO_PATH = config['Bot']['video_path']

bot = telebot.TeleBot(BOT_TOKEN)

# --- Данные о темах и категориях ---
themes_and_categories = {
    "Programming": ["books", "source", "cheatsheet", "python", "php", "html", "css", "js", "cpplus", "c", "assembler",
                    "wordpress", "api"],
    "Network": ["source", "tools", "cheatsheet", "commands"],
    "Pentest / Software": ["books", "source", "tools", "cheatsheet"],
    "Linux / Windows / AD": ["source", "tools", "cheatsheet", "commands", "ad", "windows", "powershell", "linux"],
    "Databases": ["books", "source", "tools", "sql", "nosql", "mysql", "postgresql", "mongodb"],
    "Revers / Malware dev": ["books", "malware", "revers"],
    "Steganography / Cryptography": ["books", "source", "tools", "crack", "crypto", "steganography"],
    "Servers / Docker": ["books", "source", "cheatsheet", "docker", "servers", "nginx", "waf"],
    "OSINT / Phishing": ["books", "source", "tools"]
}

themes_and_categories_db = {
    "Programming": "programming",
    "Network": "network",
    "Pentest / Software": "pentestsoftware",
    "Linux / Windows / AD": "linuxwindowsad",
    "Databases": "databases",
    "Revers / Malware dev": "reversmalwaredev",
    "Steganography / Cryptography": "steganographycryptography",
    "Servers / Docker": "serversdocker",
    "OSINT / Phishing": "osintphishing"
}

# ---  Глобальные переменные для хранения данных поиска ---
search_theme = None
search_categories = []
search_description = None
current_state = 'theme_selection'  # Отслеживаем текущее состояние
message_id_to_edit = None # Добавляем для хранения ID сообщения, которое нужно редактировать
last_search_message_id = None # ID последнего сообщения поиска, которое может иметь кнопку.
start_help_message_id = None # ID сообщения после /start или /help
help_command_used = False # Добавлено: флаг, чтобы отслеживать использование команды /help
start_command_used = False # Добавлено: флаг, чтобы отслеживать использование команды /start

# --- Загрузка модели SentenceTransformer ---
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logging.info("Модель SentenceTransformer загружена.")
except Exception as e:
    logging.error(f"Ошибка при загрузке модели SentenceTransformer: {e}")
    model = None  # Устанавливаем в None, чтобы бот не упал, если модель не загрузилась

def search_with_embeddings(theme, categories, user_description):
    table_name = themes_and_categories_db[theme]
    try:
        with sshtunnel.SSHTunnelForwarder(
                (ssh_host, ssh_port),
                ssh_username=ssh_user,
                ssh_pkey=ssh_pkey,
                remote_bind_address=(db_host, db_port)
        ) as tunnel:
            logging.info(f"Туннель SSH установлен на порту {tunnel.local_bind_port}")
            with psycopg2.connect(
                host="localhost",
                database=db_name,
                user=db_user,
                password=db_password,
                port=tunnel.local_bind_port
            ) as conn:
                with conn.cursor() as cur:
                    # 1. Получите данные из базы данных
                    query = f"SELECT post_id, post_keywords, post_text, post_url FROM {table_name}"
                    cur.execute(query)
                    results = cur.fetchall()

                    # 2. Сгенерируйте embeddings для описаний в базе данных
                    db_descriptions = [row[2] for row in results]
                    db_embeddings = model.encode(db_descriptions, convert_to_tensor=True)

                    # 3. Сгенерируйте embedding для запроса пользователя
                    query_embedding = model.encode(user_description, convert_to_tensor=True)

                    # 4. Вычислите косинусное сходство
                    cosine_scores = util.pytorch_cos_sim(query_embedding, db_embeddings)[0]

                    # 5. Отсортируйте результаты по сходству
                    results_with_scores = list(zip(results, cosine_scores.tolist()))
                    results_with_scores.sort(key=lambda x: x[1], reverse=True)

                    # 6. Отфильтруйте результаты по категориям и верните лучшие
                    filtered_results = []
                    for (row, score) in results_with_scores:
                        keywords = row[1]
                        if all(category in keywords for category in categories): # проверяем вхождение всех категорий
                            filtered_results.append((row, score))

                    return filtered_results[:5] #  Возвращаем топ-5 результатов

    except Exception as e:
        logging.error(f"Error during search: {e}")
        return []

# --- Обработчик команды /start ---
@bot.message_handler(commands=['start'])
def start(message):
    global start_help_message_id, help_command_used, start_command_used
    reset_search(message)  # Сбрасываем поиск при использовании команды /start
    help_command_used = False  # Сбрасываем флаг использования /help
    start_command_used = True # Устанавливаем флаг использования /start

    markup = types.InlineKeyboardMarkup(row_width=1)
    item_search = types.InlineKeyboardButton("Осуществить поиск 🔎", callback_data='start_search')
    markup.add(item_search)

    sent_message = bot.send_message(message.chat.id,
                     "Здравствуйте! Чтобы найти нужный пост, нажмите кнопку под сообщением и следуйте инструкциям 👾🪬\n\n"
                     "ℹ️ Если у Вас возникнут сложности с использованием бота, то подробное руководство Вы найдете в Меню в разделе \"Помощь\"",
                     reply_markup=markup)

    start_help_message_id = sent_message.message_id

    # Устанавливаем меню команд
    set_commands(bot)


# --- Обработчик команды /help ---
@bot.message_handler(commands=['help'])
def help_command(message):
    global start_help_message_id, help_command_used
    reset_search(message)  # Сбрасываем поиск при использовании команды /help
    help_command_used = True  # Устанавливаем флаг использования /help

    # Отправляем сообщение с инструкциями
    help_text = (
        "*1)* Нажмите \"Осуществить поиск 🔎\"\n"
        "*2)* Затем выберите тему, по которой бот будет искать пост\n"
        "*3)* Выберите одну или несколько категорий (тегов под постами) — бот будет искать только те посты, в которых есть хотя бы одна из выбранных категорий\n"
        "- Если вы случайно выбрали ненужную категорию, просто нажмите на нее второй раз, чтобы отменить выбор\n"
        "*4)* Наиболее детально опишите пост, который необходимо найти. Постарайтесь вспомнить какую-то информацию и написать её боту\n\n"
        "Если остались вопросы, пишите @infSecAdmin"
    )

    # Создаем inline-кнопку
    markup = types.InlineKeyboardMarkup(row_width=1)
    item_search = types.InlineKeyboardButton("Осуществить поиск 🔎", callback_data='start_search')
    markup.add(item_search)

    # Отправляем видео вместе с текстом и кнопкой
    try:
        video = open(VIDEO_PATH, 'rb')
        sent_message = bot.send_video(message.chat.id, video, caption=help_text, parse_mode="Markdown", reply_markup=markup)
    except FileNotFoundError:
        sent_message = bot.send_message(message.chat.id, "Видео с инструкцией не найдено.\n\n" + help_text, parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        logging.error(f"Ошибка при отправке видео: {e}")
        sent_message = bot.send_message(message.chat.id, "Произошла ошибка при отправке видео.\n\n" + help_text, parse_mode="Markdown", reply_markup=markup)

    start_help_message_id = sent_message.message_id

# --- Обработчик команды /search ---
@bot.message_handler(commands=['search'])
def search_command(message):
    global help_command_used, start_command_used
    reset_search(message) # Сбрасываем поиск при использовании команды /search
    help_command_used = False  # Сбрасываем флаг использования /help
    start_command_used = False # Сбрасываем флаг использования /start
    ask_theme(message)

# --- Функция для сброса параметров поиска ---
def reset_search(message):
    global search_theme, search_categories, search_description, current_state, message_id_to_edit, last_search_message_id, start_help_message_id
    search_theme = None
    search_categories = []
    search_description = None
    current_state = 'theme_selection'

    # Удаляем предыдущее сообщение, если оно есть
    if message_id_to_edit:
        try:
            bot.delete_message(message.chat.id, message_id_to_edit)
        except telebot.apihelper.ApiTelegramException as e:
            logging.error(f"Error deleting message: {e}")
        message_id_to_edit = None

    # Удаляем кнопку "Осуществить новый поиск" с последнего сообщения поиска
    if last_search_message_id:
        try:
            bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=last_search_message_id, reply_markup=None)
            last_search_message_id = None # Сбрасываем ID
        except telebot.apihelper.ApiTelegramException as e:
            logging.error(f"Error deleting markup: {e}")

    # Удаляем кнопку "Осуществить поиск" с сообщения после /start или /help
    if start_help_message_id:
        try:
            bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=start_help_message_id, reply_markup=None)
            start_help_message_id = None
        except telebot.apihelper.ApiTelegramException as e:
            logging.error(f"Error deleting markup from /start or /help message: {e}")

# --- Функция для задания вопроса о теме поиска ---
def ask_theme(message):
    global message_id_to_edit

    markup = types.InlineKeyboardMarkup(row_width=2)
    for theme in themes_and_categories.keys():
        item = types.InlineKeyboardButton(theme, callback_data=f'theme:{theme}')
        markup.add(item)

    # Если сообщение уже было отправлено (редактируем существующее)
    if message_id_to_edit:
        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message_id_to_edit,
                                  text="По какой теме хотите осуществить запрос?", reply_markup=markup)
            bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message_id_to_edit, reply_markup=markup)
            return  # Важно: выходим из функции, чтобы не отправлять новое сообщение
        except telebot.apihelper.ApiTelegramException as e:
            logging.error(f"Error editing message: {e}")

    # Если это первый раз (отправляем новое сообщение и сохраняем его ID)
    sent_message = bot.send_message(message.chat.id, "По какой теме хотите осуществить запрос?", reply_markup=markup)
    message_id_to_edit = sent_message.message_id


# --- Функция для задания вопроса о категориях поиска ---
def ask_categories(message, theme):
    global current_state, message_id_to_edit

    current_state = 'category_selection'
    markup = types.InlineKeyboardMarkup(row_width=2)
    for category in themes_and_categories[theme]:
        item = types.InlineKeyboardButton(category, callback_data=f'category:{category}')
        if category in search_categories:
            item.text = f"✅ {category}"  # Показываем выбранные категории
        markup.add(item)

    # Добавляем кнопки "Назад" и "Далее"
    item_back = types.InlineKeyboardButton("⬅️ Назад", callback_data='back_to_theme')
    item_next = types.InlineKeyboardButton("➡️ Далее", callback_data='next_categories')
    markup.add(item_back, item_next)

    # Редактируем сообщение, используя сохраненный ID
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message_id_to_edit,
                              text=f"Выберите категории для темы {theme} и нажмите Далее:")
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message_id_to_edit, reply_markup=markup)
    except telebot.apihelper.ApiTelegramException as e:
        logging.error(f"Error editing message: {e}")

# --- Функция для запроса описания ---
def ask_description_ai(message):
    global current_state, message_id_to_edit

    current_state = 'description_input'

    markup = types.InlineKeyboardMarkup(row_width=1)
    item_back = types.InlineKeyboardButton("⬅️ Назад", callback_data='back_to_categories')
    markup.add(item_back)

    # Редактируем сообщение, используя сохраненный ID
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message_id_to_edit,
                              text="Введите описание для поиска (можно часть текста):")
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message_id_to_edit, reply_markup=markup)
    except telebot.apihelper.ApiTelegramException as e:
        logging.error(f"Error editing message: {e}")


# --- Функция для обработки введенного описания ---
@bot.message_handler(func=lambda message: current_state == 'description_input', content_types=['text'])
def process_description_ai(message):
    global search_description, message_id_to_edit
    search_description = message.text

    # Удаляем сообщение "Введите описание для поиска" с кнопкой "Назад"
    if message_id_to_edit:
        try:
            bot.delete_message(message.chat.id, message_id_to_edit)
        except telebot.apihelper.ApiTelegramException as e:
            logging.error(f"Error deleting message: {e}")
        message_id_to_edit = None  # Сбрасываем ID, так как сообщение удалено

    perform_search_ai(message) # вызываем поиск с ИИ

def send_no_results_message(message, theme, categories, description):
    global last_search_message_id

    # Формируем сообщение о запросе
    category_text = "Категория" if len(categories) == 1 else "Категории"
    categories_str = ", ".join(categories)  # Соединяем категории через запятую
    request_info = f"Ваш запрос:\n- Тема: {theme}\n- {category_text}: {categories_str}\n- Описание: {description}\n\n"
    message_text = request_info + "К сожалению, я не нашел такого поста 😔\nПоменяйте тему, добавьте больше категорий или измените описание 💡"

    # Добавляем кнопку "Осуществить новый поиск"
    markup = types.InlineKeyboardMarkup(row_width=1)
    item_search = types.InlineKeyboardButton("Осуществить новый поиск 🔎", callback_data='start_search')
    markup.add(item_search)

    # Отправляем сообщение и сохраняем ID
    sent_message = bot.send_message(message.chat.id, message_text, reply_markup=markup)
    last_search_message_id = sent_message.message_id

# --- Функция для выполнения поиска с ИИ ---
def perform_search_ai(message):
    global search_theme, search_categories, search_description, current_state, message_id_to_edit, last_search_message_id, start_help_message_id, help_command_used, start_command_used

    if model is None:
        bot.send_message(message.chat.id, "К сожалению, функция поиска с использованием ИИ временно недоступна.")
        return

    # Удаляем кнопку "Осуществить новый поиск" с последнего сообщения поиска (если оно было)
    if last_search_message_id:
        try:
            bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=last_search_message_id, reply_markup=None)
        except telebot.apihelper.ApiTelegramException as e:
            logging.error(f"Error deleting markup: {e}")

    # Удаляем кнопку "Осуществить поиск" с сообщения после /start или /help
    if start_help_message_id and (help_command_used or start_command_used): # Проверяем, что команда /help или /start была использована
        try:
            bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=start_help_message_id, reply_markup=None)
            start_help_message_id = None
        except telebot.apihelper.ApiTelegramException as e:
            logging.error(f"Error deleting markup from /start or /help message: {e}")

    # Отправляем сообщение "Осуществляю поиск..."
    searching_message = bot.send_message(message.chat.id, "Осуществляю поиск...")

    results = search_with_embeddings(search_theme, search_categories, search_description)

    # Удаляем сообщение "Осуществляю поиск..."
    bot.delete_message(message.chat.id, searching_message.message_id)

    # Формируем сообщение о запросе
    category_text = "Категория" if len(search_categories) == 1 else "Категории"
    categories_str = ", ".join(search_categories)  # Соединяем категории через запятую
    request_info = f"Ваш запрос:\n- Тема: {search_theme}\n- {category_text}: {categories_str}\n- Описание: {search_description}\n\n"

    # Сбрасываем параметры поиска после выполнения
    theme = search_theme
    categories = search_categories
    description = search_description

    search_theme = None
    search_categories = []
    search_description = None
    current_state = 'theme_selection'
    # Важно! Не сбрасываем message_id_to_edit, потому что на него может ссылаться сообщение с результатом поиска!

    if results:
        # Формируем список ссылок с процентами сходства
        links = []
        for (row, score) in results:
            if score * 100 >= 20:  # Проверяем, что сходство >= 20%
                link = row[3]  # Получаем URL поста из результатов
                similarity = int(score * 100)  # Преобразуем в целое число процентов
                links.append(f"{link} — Сходство: {similarity}%")

        if len(links) == 1:  # Если только одна ссылка
            message_text = request_info + "Найден следующий пост:\n" + "\n".join(links)
        else:
            message_text = request_info + "Найдены следующие посты:\n" + "\n".join(links)

        # Добавляем кнопку "Осуществить новый поиск"
        markup = types.InlineKeyboardMarkup(row_width=1)
        item_search = types.InlineKeyboardButton("Осуществить новый поиск 🔎", callback_data='start_search')
        markup.add(item_search)

        # Отправляем сообщение и сохраняем ID
        sent_message = bot.send_message(message.chat.id, message_text, reply_markup=markup)
        last_search_message_id = sent_message.message_id

    else:
        # Если вообще ничего не найдено
        send_no_results_message(message, theme, categories, description)


# --- Обработчик InlineKeyboardButton ---
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global search_theme, search_categories, current_state, message_id_to_edit, last_search_message_id, start_help_message_id, help_command_used, start_command_used

    if call.data == 'start_search':
        bot.answer_callback_query(call.id)
        search_theme = None
        search_categories = []
        current_state = 'theme_selection'

        # Удаляем все лишние кнопки поиска
        if last_search_message_id:
            try:
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=last_search_message_id, reply_markup=None)
                last_search_message_id = None
            except telebot.apihelper.ApiTelegramException as e:
                logging.error(f"Error deleting markup: {e}")

        # Удаляем кнопку "Осуществить поиск" с сообщения после /start или /help
        if start_help_message_id and (help_command_used or start_command_used):
            try:
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=start_help_message_id, reply_markup=None)
                start_help_message_id = None
            except telebot.apihelper.ApiTelegramException as e:
                logging.error(f"Error deleting markup from /start or /help message: {e}")

        if message_id_to_edit: # Удаляем предыдущее сообщение, если оно есть
           try:
               bot.delete_message(call.message.chat.id, message_id_to_edit)
           except telebot.apihelper.ApiTelegramException as e:
               logging.error(f"Error deleting message: {e}")
           message_id_to_edit = None
        ask_theme(call.message)

    elif call.data.startswith('theme:'):
        bot.answer_callback_query(call.id)
        search_theme = call.data.split(':')[1]
        search_categories = [] # Сбрасываем категории при выборе новой темы
        ask_categories(call.message, search_theme)

    elif call.data.startswith('category:'):
        category = call.data.split(':')[1]
        if category not in search_categories:
            search_categories.append(category)
            bot.answer_callback_query(call.id, f"Категория '{category}' добавлена")
        else:
            search_categories.remove(category)
            bot.answer_callback_query(call.id, f"Категория '{category}' удалена")

        # редактируем сообщение с кнопками, чтобы пользователь видел, что выбрано
        markup = types.InlineKeyboardMarkup(row_width=2)
        for cat in themes_and_categories[search_theme]:
            item = types.InlineKeyboardButton(cat, callback_data=f'category:{cat}')
            if cat in search_categories:
                item.text = f"✅ {cat}"
            markup.add(item)

        # Добавляем кнопки "Назад" и "Далее"
        item_back = types.InlineKeyboardButton("⬅️ Назад", callback_data='back_to_theme')
        item_next = types.InlineKeyboardButton("➡️ Далее", callback_data='next_categories')
        markup.add(item_back, item_next)

        try:
            bot.edit_message_reply_markup(call.message.chat.id, message_id_to_edit, reply_markup=markup)
        except telebot.apihelper.ApiTelegramException as e:
            logging.error(f"Error editing message: {e}")

    elif call.data == 'next_categories':
        if search_theme and len(search_categories) > 0:
            ask_description_ai(call.message)  # Заменили вызов ask_description на ask_description_ai
        else:
            bot.answer_callback_query(call.id, "Пожалуйста, выберите хотя бы одну категорию.")
            # (Опционально) Можно вернуть к выбору категорий или как-то выделить ошибку.

    elif call.data == 'back_to_theme':
        search_categories = []  # Сбрасываем выбранные категории
        # Вместо вызова ask_theme вызываем его "внутренности" и редактируем сообщение
        markup = types.InlineKeyboardMarkup(row_width=2)
        for theme in themes_and_categories.keys():
            item = types.InlineKeyboardButton(theme, callback_data=f'theme:{theme}')
            markup.add(item)

        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=message_id_to_edit,
                                  text="По какой теме хотите осуществить запрос?", reply_markup=markup)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id_to_edit, reply_markup=markup)
        except telebot.apihelper.ApiTelegramException as e:
            logging.error(f"Error editing message: {e}")

        current_state = 'theme_selection'

    elif call.data == 'back_to_categories':
        # Обновляем клавиатуру категорий с учетом выбранных
        markup = types.InlineKeyboardMarkup(row_width=2)
        for category in themes_and_categories[search_theme]:
            item = types.InlineKeyboardButton(category, callback_data=f'category:{category}')
            if category in search_categories:
                item.text = f"✅ {cat}"  # Показываем выбранные категории
            markup.add(item)

        # Добавляем кнопки "Назад" и "Далее"
        item_back = types.InlineKeyboardButton("⬅️ Назад", callback_data='back_to_theme')
        item_next = types.InlineKeyboardButton("➡️ Далее", callback_data='next_categories')
        markup.add(item_back, item_next)

        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=message_id_to_edit,
                                  text=f"Выберите категории для темы '{search_theme}':")
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id_to_edit, reply_markup=markup)
        except telebot.apihelper.ApiTelegramException as e:
            logging.error(f"Error editing message: {e}")
        current_state = 'category_selection'

    else:
        bot.answer_callback_query(call.id, "Неизвестный запрос")


# --- Функция для установки меню команд ---
def set_commands(bot):
    commands = [
        telebot.types.BotCommand("start", "Перезапуск бота 📖"),
        telebot.types.BotCommand("search", "Осуществить поиск 🔎"),
        telebot.types.BotCommand("help", "Помощь 📖")
    ]
    bot.set_my_commands(commands)


# Запускаем бота
if __name__ == "__main__":
    bot.infinity_polling()
