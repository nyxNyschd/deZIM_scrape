import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os
import re
import datetime
import boto3

s3 = boto3.client('s3')


def lambda_handler(event, context):
    bucket = 'newspapersdump'

    options = Options()
    options.binary_location = '/opt/bin/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome('/opt/bin/chromedriver', chrome_options=options)

    # access page
    driver.get("https://www.spiegel.de")

    # access content
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    print('## FINDING LOGIN-ICON')

    # find login-icon
    try:
        url = soup.find('a', {'title': 'Jetzt anmelden'})['href']
    except TypeError:
        pass

    # open login-page
    driver.get(url)

    # locate login-field
    login = driver.find_element_by_id('loginname')
    pw = driver.find_element_by_id('password')

    # einloggen
    login.send_keys("")
    pw.send_keys("")

    submit = driver.find_element_by_id('submit')
    submit.click()

    print('## LOGGED IN')

    # kurz warten
    time.sleep(2)

    # dann noch der Werbung zustimmen:
    accept = driver.find_element_by_id('sp_message_iframe_449643').click()

    print('## OPEN RSS-FEEDS')

    # open start-rss-page
    driver.get("https://www.spiegel.de/schlagzeilen/tops/index.rss")

    # access content
    content = driver.page_source
    soup = BeautifulSoup(content, 'xml')

    # access all the links
    articles = []
    items = soup.findAll('item')
    for item in items:
        try:
            title = item.find('title').text
            link = item.find('guid').text
            teaser = item.find('description').text

            cats = item.find_all('category')
            categories = []

            for category in cats:
                categories.append(category.text)

            published = item.find('pubDate').string.strip()
        except:
            pass

        print('## FOLLOWING LINK')
        # follow link
        try:
            driver.get(link)
        except:
            pass

        # access content of article
        newcontent = driver.page_source
        soup = BeautifulSoup(newcontent, 'html.parser')

        # extract fulltext for current article
        fulltext = []
        paragraph_wrapper = soup.find_all('div', {'class': 'RichText'})
        for pack in paragraph_wrapper:
            paragraphs = pack.findChildren("p", recursive=False)

            for p in paragraphs:
                fulltext.append(p.text)

        joined_text = ' '.join(fulltext)
        # print(joined_text)

        if soup.find('div',{'data-paycategory' : 'PAID'}):
            paywalled=1
        else:
            paywalled=0

        art_id = "SPi-" + published + joined_text[9:11]

        article = {
            'id': art_id,
            'title': title,
            'link': link,
            'teaser': teaser,
            'text': joined_text,
            'category': categories,
            'published': published,
            'paywall':paywalled
        }
        articles.append(article)

    current_time = str(datetime.datetime.now())
    fileName = 'SPi-' + current_time + '.json'

    uploadByteStream = bytes(json.dumps(articles).encode('UTF-8'))

    s3.put_object(Bucket=bucket, Key=fileName, Body=uploadByteStream)

    print('Put complete')

if __name__ == '__main__':
    lambda_handler(None, None)













