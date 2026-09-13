import requests
import telebot
from dotenv import load_dotenv
import os
import time
import logging


class MyLogsHandler(logging.Handler):
    
    def __init__(self, token, chat_id, level=logging.NOTSET):
        super().__init__(level=level)
        self.token = token
        self.chat_id = chat_id
        self.bot = telebot.TeleBot(token)
    
    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.bot.send_message(self.chat_id, log_entry)
        except Exception:
            self.handleError(record)


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
    
    logger = logging.getLogger("review_logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(MyLogsHandler(token, chat_id))
    
    logger.info('Бот запущен')
    
    params = {}  
    
    while True:

        try:
            answer_about_task = get_task_status(access_token, params)
            if answer_about_task:
                logger.info('A new response sent to another server')
                bot_send_message(token, chat_id, answer_about_task)
                
        except requests.exceptions.ReadTimeout:
            continue
            
        except requests.exceptions.ConnectionError:
            logger.info('Ошибка соединения, бот ожидает 1 минуту')
            time.sleep(60)
            
        except Exception as e:
            logger.error(f'Бот упал с ошибкой: {e}', exc_info=True)
            time.sleep(60)


if __name__ == "__main__":
    main()
    
