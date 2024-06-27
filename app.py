from flask import Flask, render_template, request, redirect, url_for
import math
import os
import random
import base64
import requests
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from dateutil.parser import parse
import parsedatetime as pdt

app = Flask(__name__)

HEADERS = {"accept-encoding": "gzip", "user-agent": "okhttp/4.9.2"}
AUTH_KEY = None
calendar = pdt.Calendar()

def fetch_authkey() -> str:
    url = "https://api-1.online/post/"
    params = {"action": "get_encrypted_api_key", "type": "user"}
    json = {"api": "111"}
    rq = requests.post(url, params=params, headers=HEADERS, json=json)
    return rq.json()["api_key"]

def decrypt_key(encrypted_str: str) -> str:
    decode = base64.b64decode(encrypted_str)
    iv = decode[:16]
    encrypted_data = decode[16:]
    cipher = AES.new("9e8986a75ffa32aa187b7f34394c70ea".encode(), AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted_data.decode()

def fetch_countries() -> dict:
    url = "https://api-1.online/get/"
    params = {"action": "country"}
    return requests.post(url, params=params, headers=HEADERS).json()["records"]

def fetch_numbers(country: str, page: int) -> dict:
    global AUTH_KEY
    if AUTH_KEY is None:
        AUTH_KEY = decrypt_key(fetch_authkey())
        print(f"Fetched and decrypted AUTH_KEY: {AUTH_KEY}")
    
    url = "https://api-1.online/post/"
    params = {"action": "GetFreeNumbers", "type": "user"}
    headers = HEADERS.copy()
    headers["authorization"] = "Bearer " + AUTH_KEY
    json = {"country_name": country, "limit": 10, "page": page}
    
    response = requests.post(url, params=params, headers=headers, json=json)
    response_json = response.json()
    print(f"Fetching numbers for {country}, page {page}: {response_json}")
    
    if "error" in response_json:
        raise ValueError(f"API Error: {response_json['error']['message']}")
    
    if "Available_numbers" not in response_json:
        raise KeyError(f"Key 'Available_numbers' not found in response: {response_json}")
    
    return response_json

def fetch_all_numbers(country: str) -> list:
    all_numbers = []
    page = 1
    while True:
        try:
            numbers_data = fetch_numbers(country, page)
            numbers = get_recent_numbers(numbers_data.get("Available_numbers", []))
            all_numbers.extend(numbers)
            total_pages = numbers_data.get("Total_Pages", 1)
            if page >= total_pages or len(all_numbers) > 149:
                break
            page += 1
        except (ValueError, KeyError) as e:
            print(f"Error fetching numbers for {country}: {e}")
            break
    return all_numbers

def fetch_sms(number: str) -> dict:
    global AUTH_KEY
    if AUTH_KEY is None:
        AUTH_KEY = decrypt_key(fetch_authkey())
    url = "https://api-1.online/post/getFreeMessages"
    json = {"no": number, "page": "1"}
    headers = HEADERS.copy()
    headers["authorization"] = "Bearer " + AUTH_KEY
    response = requests.post(url, headers=headers, json=json)
    response_json = response.json()
    print(f"Fetching SMS for {number}: {response_json}")
    
    if "error" in response_json:
        raise ValueError(f"API Error: {response_json['error']['message']}")
    
    if "messages" not in response_json:
        raise KeyError(f"Key 'messages' not found in response: {response_json}")
    
    return response_json["messages"]

def get_recent_numbers(numbers):
    one_month_ago = datetime.now() - timedelta(days=30)
    recent_numbers = []

    for num in numbers:
        try:
            # Try to parse the time as a datetime object
            if 'ago' in num['time']:
                number_time = calendar.parseDT(num['time'])[0]
            else:
                number_time = parse(num['time'])
                
            if number_time > one_month_ago:
                recent_numbers.append(num)
        except (ValueError, TypeError):
            # Skip if the date format is invalid
            continue

    print(f"Recent numbers: {recent_numbers}")
    return recent_numbers

@app.route('/')
def index():
    global AUTH_KEY
    if not AUTH_KEY:
        AUTH_KEY = decrypt_key(fetch_authkey())

    countries = fetch_countries()
    available_countries = []

    for country in countries:
        try:
            country_name = country["Country_Name"]
            numbers_data = fetch_numbers(country_name, 1)
            available_numbers = get_recent_numbers(numbers_data.get("Available_numbers", []))
            if available_numbers:
                available_countries.append(country_name)
        except (ValueError, KeyError) as e:
            print(f"Error fetching numbers for {country_name}: {e}")
    
    random_countries = random.sample(available_countries, min(len(available_countries), 15))
    return render_template('index.html', countries=random_countries)

@app.route('/countries')
def countries():
    countries = fetch_countries()
    return render_template('countries.html', countries=countries)

@app.route('/numbers/<country>')
def numbers(country):
    page = 1
    numbers = []

    try:
        numbers_data = fetch_numbers(country, page)
        numbers.extend(get_recent_numbers(numbers_data.get("Available_numbers", [])))
        total_pages = numbers_data.get("Total_Pages", 1)

        for i in range(2, total_pages + 1):
            numbers_data = fetch_numbers(country, i)
            numbers.extend(get_recent_numbers(numbers_data.get("Available_numbers", [])))
            if len(numbers) > 149:
                break

    except (ValueError, KeyError) as e:
        print(f"Error fetching numbers for {country}: {e}")
        return f"Error fetching numbers for {country}: {e}", 500
    
    print(f"All fetched numbers for {country}: {numbers}")
    return render_template('numbers.html', country=country, numbers=numbers)

@app.route('/messages/<number>')
def messages(number):
    page = request.args.get('page', 1, type=int)
    per_page = 15
    try:
        messages = fetch_sms(number)
    except (ValueError, KeyError) as e:
        print(f"Error fetching messages for {number}: {e}")
        return f"Error fetching messages for {number}: {e}", 500
    
    total_messages = len(messages)
    messages = messages[(page-1)*per_page : page*per_page]
    
    country = number[:5]  # Extract country code, assuming first 5 characters are the country code
    all_numbers = fetch_all_numbers(country)
    random_number = random.choice(all_numbers) if all_numbers else None
    return render_template(
        'messages.html', 
        number=number, 
        messages=messages, 
        random_number=random_number,
        page=page,
        per_page=per_page,
        total_messages=total_messages
    )

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

if __name__ == '__main__':
    app.run(debug=True)
