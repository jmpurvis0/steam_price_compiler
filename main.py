import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time

url = 'https://store.steampowered.com/search/?supportedlang=english&hidef2p=1&filter=topsellers&ndl=1'

def totalresults(url):
    r = requests.get(url)
    data = dict(r.json())
    totalresults = data['total_count']
    return int(totalresults)

def get_data(url):
    r = requests.get(url)
    data = dict(r.json())
    return data['results_html']

def parse(data):
    gameslist = []
    soup = BeautifulSoup(data, 'html.parser')
    games = soup.find_all('a')
    for game in games:
        title = game.find('span', {'class': 'title'}).text
        orig_price = game.find('div', {'class': 'discount_original_price'})
        disc_price = game.find('div', {'class': 'discount_final_price'})
        link = game["href"]

        # if game is free, don't record prices
        if orig_price == None and disc_price == None:
            continue

        disc_price = float(disc_price.text.strip().split('$')[1])

        if orig_price == None:
            orig_price = disc_price
        else:
            orig_price = float(orig_price.text.strip().split('$')[1])

        raw_sale = round(orig_price - disc_price, 2)
        percent_sale = int((raw_sale / orig_price) * 100)

        print(title, orig_price, disc_price, raw_sale, percent_sale, link)

        mygame ={
            'title': title,
            'orig_price': orig_price,
            'disc_price': disc_price,
            'raw_sale': raw_sale,
            'percent_sale': percent_sale,
            'game_link': link
        }
        gameslist.append(mygame)
    return gameslist

def output(results):
    gamesdf = pd.concat([pd.DataFrame(g) for g in results])
    gamesdf.to_csv('gamesprices.csv', index=False)
    print('Fin. Saved to CSV')
    print(gamesdf.head())
    return

results = []
for x in range(0, 5000, 100):
    data = get_data(f'https://store.steampowered.com/search/results/?query&start={x}&count=50&dynamic_data=&sort_by=_ASC&supportedlang=english&snr=1_7_7_7000_7&filter=topsellers&infinite=1')
    results.append(parse(data))
    print('Results Scraped: ', x + 100)
    time.sleep(1.5)

output(results) 




