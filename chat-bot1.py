import requests


def get_task_status():
    headers = {
        "Authorization": "Token 610fe58bce00b15b146d66d09c85243779d282c8"
    }
    
    params = {
        'timestamp': 1555493856
    }

    while True:
        try:
            response = requests.get('https://dvmn.org/api/long_polling/', params=params, headers=headers, timeout=5)
            response.raise_for_status()
                        
            data = response.json()
            print(data)
        except requests.exceptions.ReadTimeout:
            print('Ждем ответ от сервера')


get_task_status()