# imports from needed libraries
# ___________________________________________________________________
import os
import logging
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
import telebot
import requests
import json


# __________________________________________________________________


# helper
# __________________________________________________________________
def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


# __________________________________________________________________


# server needed constants & creating server and db
# __________________________________________________________________
TOKEN = '1395616602:AAEitL36CEX_epUhcJeBFhqE_oc8ZU2NAek'
# webhook_url = 'https://maximtestheroku-29.herokuapp.com/' + TOKEN
webhook_url = 'https://f18e5d4b907e.ngrok.io/' + TOKEN
server_url = 'https://f18e5d4b907e.ngrok.io/'
server = Flask(__name__)
server.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgres://ynrrjmbbwpkdse:eb7f211b285eb95d562cacaf3f885ec31edbc6ae43e3b42ddc8764e5234714bb@ec2-34-238-26-109.compute-1.amazonaws.com:5432/dbsd0628b94q4s'
# server.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)
# __________________________________________________________________


# models needed imports & creating bot
# __________________________________________________________________
from youtubeAPI import getVideoInfoByPrompt, getUrlByVideoId
import db_data
import Task as t
import markups

task = t.Task()
bot = telebot.TeleBot(TOKEN)


# __________________________________________________________________


# bot's handlers and first interaction with client
# __________________________________________________________________
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    response = requests.get("{}/adduser".format(webhook_url),
                            params={"id": message.chat.id, "name": message.chat.id, "email": 'bla-bla-bla'})

    # write_json(response.json(), filename='user.json')
    bot.send_message(message.chat.id, 'Я добавил Вас в базу данных')

    if not task.isRunning:
        chat_id = message.chat.id
        msg = bot.send_message(
            chat_id, 'Привет)\nСколько видео по теме ты хочешь искать?', reply_markup=markups.maxres_markup)
        bot.register_next_step_handler(msg, ask_max_results)


def ask_max_results(message):
    chat_id = message.chat.id
    text = message.text
    if text.isdigit():
        task.maxResult = int(text)
        msg = bot.send_message(
            chat_id, f'Отлично. Будем искать {task.maxResult} лучших видео по теме:')
        bot.register_next_step_handler(msg, ask_source)
    else:
        msg = bot.send_message(
            chat_id, 'Введите, пожалуйста, натуральное число')
        bot.register_next_step_handler(msg, ask_max_results)
        return


def ask_source(message):
    chat_id = message.chat.id
    text = message.text.lower()
    response = requests.get("{}/youtube/video/urlsbyprompt".format(webhook_url),
                            params={"prompt": text, "maxResult": task.maxResult})
    video_urls = json.loads(response.text)
    write_json(response.json(), filename='video.json')
    for url in video_urls:
        bot.send_message(chat_id, url)


# __________________________________________________________________


# server web hooks
# __________________________________________________________________
@server.route('/' + TOKEN + '/adduser', methods=['POST', 'GET'])
def add_user():
    user_id, name, email = request.args['id'], request.args['name'], request.args['email']
    u = db_data.User(id=user_id, nickname=name, email=email)
    print("user created", u)

    # if not exist
    db.session.add(u)
    db.session.commit()
    return "<h1>user added</h1>", 200


@server.route('/deleteuser')
def delete_user():
    u = db_data.User.query.get(request.args['id'])
    db.session.delete(u)
    db.session.commit()
    return "<h1>user deleted</h1>", 200


@server.route('/addvideo')
def add_video():
    video_id, video_url = request.args['id'], request.args['video_url']
    v = db_data.Video(id=video_id, video_url=video_url)
    print("video added", v)
    db.session.add(v)
    db.session.commit()
    return "video created"


@server.route('/' + TOKEN + '/youtube/video/urlsbyprompt', methods=['POST', 'GET'])
def get_urls_by_prompt():
    prompt, maxResult = request.args['prompt'], request.args['maxResult']
    videosInfo = getVideoInfoByPrompt(prompt, maxResult)
    logging.info(f"videosInfo={str(videosInfo)}")
    result = map(lambda video: getUrlByVideoId(video.Id), videosInfo)
    print(result)
    return jsonify(list(result))


# For Bot 
@server.route("/" + TOKEN, methods=["POST"])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "bot got new update", 200


@server.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        print("webhook's url was: {}\n".format(bot.get_webhook_info().url))
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print("now webhook's url is: {}\n".format(bot.get_webhook_info().url))
        return "<h1>webhook was changed</h1>", 200
    r = request.get_json()
    write_json(r)
    return jsonify(r)


# __________________________________________________________________


if __name__ == '__main__':
    server.run(host='127.0.0.1', port=5000)

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
