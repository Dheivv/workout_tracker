import os
import sys
import smtplib
from email.message import EmailMessage
from tkinter import *
from tkinter import messagebox
from pyperclip import copy
import dotenv
import requests
import math
from time import time as t
from datetime import datetime as dt

config_file_path = f'{os.getcwd()}\\workout_tracker\\config.env'
gif_file_path = f'{os.getcwd()}\\yeah-budy-ronnie-coleman.gif'

try:
    find_config_file = dotenv.find_dotenv(filename=config_file_path, raise_error_if_not_found=True)

except:
    messagebox.showerror(
        title='Error (FileNotFound)', 
        message=f"No config file found at '{config_file_path}'"
    )
    sys.exit(0)

dotenv.load_dotenv(dotenv_path=config_file_path)
    
APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')
EXERCISES_ENDPOINT = os.getenv('EXERCISES_ENDPOINT')
SHEET_ENDPOINT = os.getenv('SHEET_ENDPOINT')
GOOGLE_SPREADSHEET = os.getenv('GOOGLE_SPREADSHEET')
EMAIL = os.getenv('EMAIL')
PYTHON_APP_PASSWORD = os.getenv('PYTHON_APP_PASSWORD')
NAME = os.getenv('NAME')
WEIGHT = os.getenv('WEIGHT')
HEIGHT = os.getenv('HEIGHT')
AGE = os.getenv('AGE')
TOKEN = os.getenv('TOKEN')

max_tries = 3
n_retries = 0
shutdown_duration = 300
n_clicks = 0
remember_me = False

# ---------------------------- BACKEND SETUP ------------------------------- #

def animateImg(ind):
    
    canvas = Canvas(width=498, height=280)
     
    if ind == frameCount:
        ind = 0
        
    frame = frames[ind]
    ind += 1
        
    canvas.create_image(249, 140, image=frame)
    canvas.grid(column=0, row=1, columnspan=3)
    window.after(100, animateImg, ind)

def turnOnOffRememberMe():
    
    global remember_me, n_clicks
    
    n_clicks += 1
    
    if n_clicks % 2 == 0:
        remember_me_btn.config(fg='black')
        remember_me = False
        # print(remember_me)
        return remember_me
    
    else:
        remember_me_btn.config(fg='red')
        remember_me = True
        # print(remember_me)
        return remember_me

def verifyUser():
    
    global shutdown_duration
    
    EXIT_TIME = os.getenv('EXIT_TIME')
    # print(EXIT_TIME)
    
    if EXIT_TIME: 
        current_time = t()
        
        if current_time <= (float(EXIT_TIME) + shutdown_duration):
            n_minutes = math.floor((shutdown_duration - (current_time - float(EXIT_TIME))) / 60)
            n_seconds = round(shutdown_duration - (current_time - float(EXIT_TIME))) % 60
            
            if n_minutes > 0:
                messagebox.showerror(
                    title='Error', 
                    message='This program is blocked because a user exceeded the max number of retries during authentication'
                    + ', ' + f'try again in {n_minutes} minutes' + ' and ' + f'{n_seconds} seconds.'
                )
            
            else:
                messagebox.showerror(
                    title='Error', 
                    message='This program is blocked because a user exceeded the max number of retries during authentication'
                    + ', ' + f'try again in {n_seconds} seconds.'
                )
                
            return sys.exit(0)

def sendToken():
    
    username = name_entry.get()
    
    if username == EMAIL:
        msg = f'Here is the token you requested: {TOKEN}'
        
        email = EmailMessage()
        email.set_content(msg)
        email['Subject'] = 'Auth Token'
        email['From'] = EMAIL
        email['To'] = EMAIL
        
        try:
            connection = smtplib.SMTP('smtp.gmail.com')
            connection.starttls()
            connection.login(EMAIL, PYTHON_APP_PASSWORD)
            connection.send_message(email)
            
        except Exception as err:
            return messagebox.showerror(title='Error', message=f'Uh oh, something went wrong! ({err})')
        
        return messagebox.showinfo(
            title='Request completed', 
            message=f'Token sent to {EMAIL} successfully, check your inbox.'
        )
    
    else:
        verifyEntries()

def verifyEntries():
    
    global n_retries, max_tries, shutdown_duration
    
    token = token_entry.get()
    
    if len(token) == 0:
        return messagebox.showinfo(title='Missing token', message='Token field cannot be empty!')
        
    if token != TOKEN and len(token) > 0:
        n_retries += 1
            
        if n_retries >= max_tries:
            exit_time = t()
            shutdown_minutes = round(shutdown_duration / 60)
                
            with open(config_file_path, 'r') as file:
                data = file.readlines()
                data[len(data) - 1] = f'EXIT_TIME={exit_time}'
                
            with open(config_file_path, 'w') as file:
                file.writelines(data)
            
            messagebox.showerror(
                title='Error', 
                message=f'Max number of retries exceeded, try again in {shutdown_minutes} minutes'
            )       
            return sys.exit(0)
        
        return messagebox.showwarning(
            title='Warning', 
            message=f'Invalid token, please try again (retries left before shutdown: {max_tries - n_retries}).'
        )
        
    username = name_entry.get()
    query = query_entry.get()
    weight_kg = weight_entry.get()
    height_cm = height_entry.get()
    age = age_entry.get()
    
    entries_inputs = [username, query, weight_kg, height_cm, age]
    
    for item in entries_inputs:
        if len(item) == 0:
            return messagebox.showinfo(
                title='Missing field(s)', 
                message='One or more required fields are empty!')
    
    rememberMe(username, weight_kg, height_cm, age)

def rememberMe(name, weight, height, age):
    
    with open(config_file_path, 'r') as file:
        data = file.readlines()
        
        if remember_me:
            # print('saving info')
            data[len(data) - 5] = f'NAME={name}\n'
            data[len(data) - 4] = f'WEIGHT={weight}\n'
            data[len(data) - 3] = f'HEIGHT={height}\n'
            data[len(data) - 2] = f'AGE={age}\n'
        
        else:
            data[len(data) - 5] = 'NAME=\n'
            data[len(data) - 4] = 'WEIGHT=\n'
            data[len(data) - 3] = 'HEIGHT=\n'
            data[len(data) - 2] = 'AGE=\n'
                
        with open(config_file_path, 'w') as file:
            file.writelines(data)
    
    postData(name, weight, height, age)

def postData(name, weight, height, age):
    
    query = query_entry.get()
    
    options = {
        'query': query,
        'weight_kg': weight,
        'height_cm': height,
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
        
    except Exception as err:
        return messagebox.showerror(title='Error', message=f'Uh oh, something went wrong! ({err})')
            
    else:
        exercises = res.json()['exercises']

        calories_list = [str(round(exercise['nf_calories'])) for exercise in exercises]
        duration_list = [str(round(exercise['duration_min'])) for exercise in exercises]
        exercises_list = [exercise['name'] for exercise in exercises]

        # print(calories_list)
        # print(duration_list)
        # print(exercises_list)
        
        token = token_entry.get()
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
                    'name': name
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
            
            try:
                res = requests.post(url=SHEET_ENDPOINT, json=data, headers=auth)
                res.raise_for_status()
                
            except Exception as err:
                return messagebox.showerror(title='Error', message=f'Uh oh, something went wrong! ({err})')
    
            else:
                copy(f'{GOOGLE_SPREADSHEET}')
                return messagebox.showinfo(
                    title='Request completed', 
                    message=f'Success! Check results at: {GOOGLE_SPREADSHEET} (link copied to clipboard).'
                )

# ---------------------------- USER INTERFACE ------------------------------- #

# Window Setup
window = Tk()
window.title('Workout Tracker')
window.config(padx=50, pady=50)

# User Verification
window.after(0, verifyUser)

# Animated Image
frameCount = 52

try:
    frames = [PhotoImage(
        file=gif_file_path, 
        format=f'gif -index {i}') for i in range(frameCount)
    ]
    
except:
    messagebox.showerror(
        title='Error', 
        message=f'No image file found at {gif_file_path}'
    )
    sys.exit(0)
    
window.after(0, animateImg, 0)

# Labels
header_label = Label(text='Workout Tracker Program', font=('Aerial', 35), fg='red', pady=30)
header_label.grid(column=0, row=0, columnspan=3)

div_label = Label(text='')
div_label.grid(column=0, row=2, pady=6)

token_label = Label(text='Authenticate yourself:')
token_label.grid(column=0, row=3)

name_label = Label(text='Your name / username:')
name_label.grid(column=0, row=4)

query_label = Label(text='Tell me which exercises you did (e.g.: ran 4km):')
query_label.grid(column=0, row=5)

weight_label = Label(text='Your weight in kgs (e.g.: 70):')
weight_label.grid(column=0, row=6)

height_label = Label(text='Your height in cms (e.g.: 180):')
height_label.grid(column=0, row=7)

age_label = Label(text='Your age (e.g.: 25):')
age_label.grid(column=0, row=8)

# Entries
token_entry = Entry(width=35)
token_entry.grid(column=1, row=3, columnspan=2)
token_entry.focus()

name_entry = Entry(width=35)
name_entry.grid(column=1, row=4, columnspan=2)
if NAME and len(NAME) > 0:
    name_entry.insert(0, NAME)

query_entry = Entry(width=35)
query_entry.grid(column=1, row=5, columnspan=2)
# query_entry.insert(0, 'ran 4km and swam for 30 minutes')

weight_entry = Entry(width=35)
weight_entry.grid(column=1, row=6, columnspan=2)
if WEIGHT and len(WEIGHT) > 0:
    weight_entry.insert(0, WEIGHT)

height_entry = Entry(width=35)
height_entry.grid(column=1, row=7, columnspan=2)
if HEIGHT and len(HEIGHT) > 0:
    height_entry.insert(0, HEIGHT)

age_entry = Entry(width=35)
age_entry.grid(column=1, row=8, columnspan=2)
if AGE and len(AGE) > 0:
    age_entry.insert(0, AGE)

# Buttons
remember_me_btn = Checkbutton(
    text='Remember me',
    activeforeground='red', 
    command=turnOnOffRememberMe
)
remember_me_btn.grid(column=0, row=9)

post_btn = Button(
    text='Confirm', 
    activeforeground='red', 
    width=30, 
    command=sendToken
)
post_btn.grid(column=1, row=9, columnspan=2)

window.mainloop()

