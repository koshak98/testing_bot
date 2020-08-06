from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import telebot
import requests
import Task as t
import parser
import markups


TOKEN = '1395616602:AAEitL36CEX_epUhcJeBFhqE_oc8ZU2NAek'
webhook_url = 'https://maximtestheroku-29.herokuapp.com/' + TOKEN
# webhook_url = 'https://d014fd4d3690.ngrok.io' + TOKEN
server = Flask(__name__)
server.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ynrrjmbbwpkdse:eb7f211b285eb95d562cacaf3f885ec31edbc6ae43e3b42ddc8764e5234714bb@ec2-34-238-26-109.compute-1.amazonaws.com:5432/dbsd0628b94q4s'

db = SQLAlchemy(server)

task = t.Task()
bot = telebot.AsyncTeleBot(task.TOKEN)


from db_data import Video
from db_data import User


@server.route('/adduser')
def webhook():
    user_id, name, email = request.args['id'], request.args['name'], request.args['email']
    u = User(id=user_id, nickname=name, email=email)
    print("user created", u)
    db.session.add(u)
    db.session.commit()
    return "user created"

@server.route('/deleteuser')
def delete():
    u = User.query.get(request.args['id'])
    db.session.delete(u)
    db.session.commit()
    return "user deleted"

@server.route('/addvideo')
def webhookvideo():
    video_id, video_url = request.args['id'], request.args['video_url']
    v = Video(id=video_id, video_url=video_url)
    print("video added", v)
    db.session.add(v)
    db.session.commit()


# For Bot 
@server.route("/" + TOKEN, methods=["POST"])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "bot got new update", 200


@server.route("/")
def web_hook():
    print("webhook's url was: {}\n".format(bot.get_webhook_info().url))
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    print("now webhook's url is: {}\n".format(bot.get_webhook_info().url))
    return "webhook was changed", 200

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


if __name__ == '__main__':
    server.run(host='127.0.0.1', port=80)
    












# import telebot
# import os
# from flask import Flask, request


# bot = telebot.TeleBot("593642481:AAEuoLHI.....")

# server = Flask(__name__)


# @bot.message_handler(commands=['start'])
# def handle_text(message):
#     user_markup = telebot.types.ReplyKeyboardMarkup(True,False)
#     user_markup.row('/start','/info')
#     start_text = str('Привет, '+message.from_user.first_name+'!\nЯ бот на Heroku.')
#     bot.send_message(chat_id=1154965888, text=start_text, parse_mode='Markdown')


# @server.route('/' + tokenBot.TOKEN, methods=['POST'])
# def getMessage():
#     bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
#     return "!", 200

# @server.route("/")
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url='https://test-new-new.herokuapp.com/' + tokenBot.TOKEN)
#     return "!", 200

