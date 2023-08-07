import telebot
import soundfile as sf
import speech_recognition as spr
import os
from libs.config import TOKEN

bot = telebot.TeleBot(TOKEN)

def recognize_text_from_wav(file_path):
    recognizer = spr.Recognizer()

    with spr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)

    try:
        recognized_text = recognizer.recognize_google(audio_data, language='uk-UA')
        return recognized_text
    except spr.UnknownValueError:
        return 'Не розпізнано текст'
    except spr.RequestError as e:
        return f'Помилка сервісу розпізнавання: {e}'

@bot.message_handler(commands=['start'])
def start(message):
    cht = message.chat.id
    bot.send_message(cht, f'Вітаю, {message.from_user.username}!\nЯ перетворюю голосові повідомлення у текст\nПросто перешли сюди аудіо')

@bot.message_handler(content_types=['voice'])
def audio(message):
    cht = message.chat.id

    fileId = message.voice.file_id

    fileInfo = bot.get_file(fileId)
    filePath = fileInfo.file_path

    downloadedFile = bot.download_file(filePath)

    with open(f'{fileId}.ogg', 'wb') as new_file:
        new_file.write(downloadedFile)

    with open(f'{message.voice.file_id}.ogg', 'rb') as f:
        output_file = 'output.wav'

        data, sample_rate = sf.read(f)
        sf.write(output_file, data, sample_rate)

    recognized_text = recognize_text_from_wav(output_file)

    bot.send_message(cht, recognized_text.lower())

    os.remove(f'{fileId}.ogg')
    os.remove('output.wav')

bot.polling()