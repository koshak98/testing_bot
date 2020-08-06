# imports



# token = '1363386793:AAEq5fcDZEQm0YIV-5Wrl4ku8yU_B_8EABM'  # @pixelray_bot

# handlers
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    if not task.isRunning:
        chat_id = message.chat.id
        print(message.chat.id)
        msg = bot.send_message(
            chat_id, 'Привет)\nСколько видео по теме ты хочешь искать?', reply_markup=markups.maxres_markup)
        bot.register_next_step_handler(msg.wait(), askMaxResults)


def askMaxResults(message):
    chat_id = message.chat.id
    text = message.text
    if text.isdigit():
        task.maxResult = int(text)
        msg = bot.send_message(
            chat_id, f'Отлично. Будем искать {task.maxResult} лучших видео по теме:')
        bot.register_next_step_handler(msg.wait(), askSource)
    else:
        msg = bot.send_message(
            chat_id, 'Введите, пожалуйста, натуральное число')
        bot.register_next_step_handler(msg.wait(), askMaxResults)
        return


def askSource(message):
    chat_id = message.chat.id
    text = message.text.lower()
    response = requests.get("http://web:8000/youtube/video/urlsbyprompt",
                            params={"prompt": text, "maxResult": task.maxResult})
    video_urls = json.loads(response.text)

    for url in video_urls:
        bot.send_message(chat_id, url)


def askAge(message):
    chat_id = message.chat.id
    text = message.text.lower()
    filters = task.filters[0]
    if text not in filters:
        msg = bot.send_message(
            chat_id, 'Такого временного промежутка нет. Введите порог корректно.')
        bot.register_next_step_handler(msg, askAge)
        return
    task.myFilter = task.filters_code_names[0][filters.index(text)]
    msg = bot.send_message(chat_id, 'Сколько страниц парсить?')
    bot.register_next_step_handler(msg.wait(), askAmount)


def askRating(message):
    chat_id = message.chat.id
    text = message.text.lower()
    filters = task.filters[1]
    if text not in filters:
        msg = bot.send_message(
            chat_id, 'Такого порога нет. Введите порог корректно.')
        bot.register_next_step_handler(msg, askRating)
        return
    task.myFilter = task.filters_code_names[1][filters.index(text)]
    msg = bot.send_message(chat_id, 'Сколько страниц парсить?')
    bot.register_next_step_handler(msg, askAmount)


def askAmount(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if not text.isdigit():
        msg = bot.send_message(
            chat_id, 'Количество страниц должно быть числом. Введите корректно.')
        bot.register_next_step_handler(msg, askAmount)
        return
    if int(text) < 1 or int(text) > 11:
        msg = bot.send_message(
            chat_id, 'Количество страниц должно быть > 0 и < 11. Введите корректно.')
        bot.register_next_step_handler(msg, askAmount)
        return
    task.isRunning = False
    output = ''
    if task.mySource == 'top':
        output = parser.getTitlesFromTop(int(text), task.myFilter)
    else:
        output = parser.getTitlesFromAll(int(text), task.myFilter)
    msg = bot.send_message(chat_id, output)
  

if __name__ == "__main__":
    main()
