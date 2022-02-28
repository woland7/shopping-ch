import re
import unicodedata

import unicodedata2
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd


def search(url):
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    driver.maximize_window()
    driver.get('https://prodotti.migros.ch/offerte/azione?region=gmti')
    scroll_number = 2
    for i in range(1, scroll_number):
        driver.execute_script("window.scrollTo(1,50000)")
        time.sleep(6)

    file = open('DS.html', 'w')
    file.write(driver.page_source)
    file.close()

    driver.close()

    data = open('DS.html', 'r')
    soup = BeautifulSoup(data, 'html.parser')
    smaller_soup = soup.find('div', class_="msrc-offer-list")
    aria_labels = smaller_soup.findAll('a', attrs={'aria-label': True})

    scontos = []
    percentuales = []

    for a in aria_labels:
        to_split = a['aria-label'].split("Offerta")[0]
        to_split = unicodedata2.normalize('NFKC', to_split)
        if 'invece di' in to_split and 'Percentuale' not in to_split:
            scontos.append(to_split)
        elif 'Percentuale' in to_split:
            percentuales.append(to_split)
    scontos_df = sconto_search(scontos)
    percentuales_df = percentuale_search(percentuales)
    print(pd.concat([scontos_df, percentuales_df]).to_markdown())


def sconto_search(scontos):
    discounts = {
        "name": [],
        "discount": [],
        "discounted": [],
        "initial": [],
        "comment": []
    }
    for sconto in scontos:
        regex_split_string = re.search('^.+?(?=\\d)', sconto).group(0)
        regex_to_split = re.split('^.+?(?=\\d)', sconto)
        regex_split = regex_to_split[1].split(" ")
        discounts['name'].append(regex_split_string)
        discounts['discount'].append(regex_split[0])
        discounts['discounted'].append("{},{}".format(regex_split[1], regex_split[3]))
        discounts['initial'].append("{},{}".format(regex_split[7], regex_split[9]))
        discounts['comment'].append("".join(regex_split[11:-1]))
    df = pd.DataFrame(discounts)
    return df

def percentuale_search(percentuales):
    discounts = {
        "name": [],
        "discount": [],
        "discounted": [],
        "initial": [],
        "comment": []
    }
    for percentuale in percentuales:
        regex_split_string = re.search('^.+?(?=\\d)', percentuale).group(0)
        regex_split_discount = re.search('\\d+(?=\\sP)', percentuale).group(0)
        discounts['name'].append(regex_split_string)
        discounts['discount'].append(regex_split_discount+"%")
        discounts['discounted'].append("")
        discounts['initial'].append("")
        discounts['comment'].append("")
    df = pd.DataFrame(discounts)
    return df

def others_search():
    pass


search('')
