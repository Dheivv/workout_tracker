import os
import sys
import dotenv
import requests
import math
from time import sleep, time as t
from datetime import datetime as dt

def postData():
    dotenv.load_dotenv(dotenv_path=f'{os.getcwd()}/config.env')
    
    EXIT_TIME = os.getenv('EXIT_TIME')
    # print(EXIT_TIME)
    shutdown_duration = 300
    
    if EXIT_TIME:
        current_time = t()
        if current_time <= (float(EXIT_TIME) + shutdown_duration):
            print(
                'This program is blocked because a user exceeded the max number of retries during authentication'
                + ', ' + f'retry in {math.floor((shutdown_duration - (current_time - float(EXIT_TIME))) / 60)} minutes'
                + ' and ' + f'{round(shutdown_duration - (current_time - float(EXIT_TIME))) % 60} seconds'
                )
            sleep(5)
            sys.exit(0)
    
    APP_ID = os.getenv('APP_ID')
    APP_KEY = os.getenv('APP_KEY')
    EXERCISES_ENDPOINT = os.getenv('EXERCISES_ENDPOINT')
    SHEET_ENDPOINT = os.getenv('SHEET_ENDPOINT')
    GOOGLE_SPREADSHEET = os.getenv('GOOGLE_SPREADSHEET')
    TOKEN = os.getenv('TOKEN')
    
    username = input('Tell me your name / username: ')
    
    max_tries = 5
    n_retries = 0
    is_authenticated = False
    
    while is_authenticated == False:
        token = input('Please authenticate yourself: ')
        
        if token == TOKEN:
            is_authenticated = True
            
        else:
            n_retries += 1
            
            if n_retries >= max_tries:
                exit_time = t()
                
                with open(f'{os.getcwd()}/config.env', 'r') as file:
                    data = file.readlines()
                    data[len(data) - 1] = f'EXIT_TIME={exit_time}'
                
                with open(f'{os.getcwd()}/config.env', 'w') as file:
                    file.writelines(data)
                    
                print(f'Max number of retries exceeded, try again in {round(shutdown_duration / 60)} minutes')
                sleep(5)
                sys.exit(0)
                
            print(f'\nInvalid token, please try again (retries left before shutdown: {max_tries - n_retries})')
    
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
        
    try:
        res = requests.post(url=EXERCISES_ENDPOINT, json=options, headers=headers)
        res.raise_for_status()
        
    except:
        print('Uh oh, something went wrong!')
            
    else:
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
                    'calories(j)': calories,
                    'name': username
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

            print('Processing request, please be patient...')
                
            try:
                res = requests.post(url=SHEET_ENDPOINT, json=data, headers=auth)
                res.raise_for_status()
                
            except:
                print('Uh oh, something went wrong!')
    
            else:
                print(f'Success! Check results at: {GOOGLE_SPREADSHEET}')

postData()

