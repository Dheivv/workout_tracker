import requests
import os
from datetime import datetime as dt
import dotenv

dotenv.load_dotenv(dotenv_path='C:/Users/mcato/100 Days Of Code/Day 38/workout_tracker/config.env')

APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')
EXERCISES_ENDPOINT = os.getenv('EXERCISES_ENDPOINT')
SHEET_ENDPOINT = os.getenv('SHEET_ENDPOINT')
# TOKEN = os.getenv('TOKEN')

token = input('Please authenticate yourself: ')
query = input('Tell me which exercises you did: ')
weight_kg = input('Your weight in kgs (e.g.: 70): ')
height_cm = input('Your height in cms (e.g.: 180): ')
age = input('Your age (e.g.: 25): ')

options = {
    'query': query,
    'weight_kg': weight_kg,
    'height_cm': height_cm,
    'age': age,
}

headers = {
    'Content-Type': 'application/json',
    'x-app-id': APP_ID,
    'x-app-key': APP_KEY,
}

res = requests.post(url=EXERCISES_ENDPOINT, json=options, headers=headers)
res.raise_for_status

exercises = res.json()['exercises']

calories_list = [str(round(exercise['nf_calories'])) for exercise in exercises]
duration_list = [str(round(exercise['duration_min'])) for exercise in exercises]
exercises_list = [exercise['name'] for exercise in exercises]

# print(calories_list)
# print(duration_list)
# print(exercises_list)

date = str(dt.now()).split(' ')[0]
time = str(dt.now()).split(' ')[1].split(':')[0] + ':' + str(dt.now()).split(' ')[1].split(':')[1]

for calories, duration, exercise in zip(calories_list, duration_list, exercises_list):

    data = {
        'foglio1': {
            'date': date,
            'time': time,
            'exercise': exercise,
            'duration(min.)': duration,
            'calories(j)': calories
        }
    }

    auth = {
        'Authorization': f'Bearer {token}'
    }

    # print(date)
    # print(time)
    # print(exercise)
    # print(duration)
    # print(calories)

    res = requests.post(url=SHEET_ENDPOINT, json=data, headers=auth)
    res.raise_for_status()


