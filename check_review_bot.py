import requests
import telebot
from dotenv import load_dotenv
import os
import time


def get_task_status(access_token, params):
    headers = {
        "Authorization": access_token
    }
    
    response = requests.get(
        'https://dvmn.org/api/long_polling/',
        params=params,
        headers=headers,
        timeout=60
    )
    
    response.raise_for_status()
    
    result_of_lesson = response.json()
    
    if result_of_lesson.get('timestamp_to_request'):
        params['timestamp'] = result_of_lesson.get('timestamp_to_request')
    
    if result_of_lesson.get('status') == 'found':
        lesson_title = result_of_lesson.get('lesson_title', 'Неизвестный урок')
        lesson_url = result_of_lesson.get('lesson_url', 'Ссылки нету')
                
        if result_of_lesson.get('is_negative'):
            is_fall = 'К сожалению, в работе нашлись ошибки'
        else:
            is_fall = 'Преподавателю всё понравилось, можно приступать к следующему уроку!'
                
        message = f"У вас проверили работу «{lesson_title}».\n{is_fall}\nСсылка: {lesson_url}"
        return message
    else:
        return None


def bot_send_message(token, chat_id, message):
    bot = telebot.TeleBot(token)
    bot.send_message(chat_id, message)
    

def main():
    load_dotenv()
    
    access_token = os.environ['DVMN_ACCESS_TOKEN']
    token = os.environ['TG_TOKEN']
    chat_id = os.environ['TG_CHAT_ID']
    
    params = {}  
    
    while True:
        try:
            answer_about_task = get_task_status(access_token, params)
            if answer_about_task:
                bot_send_message(token, chat_id, answer_about_task)
                
        except requests.exceptions.ReadTimeout:
            time.sleep(60)
            
        except ConnectionError:
            time.sleep(60)


if __name__ == "__main__":
    main()
