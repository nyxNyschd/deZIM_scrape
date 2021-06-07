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
    options.add_argument('--window-size=1920,1080')
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome('/opt/bin/chromedriver', chrome_options=options)

    # open login-page
    driver.get("https://rp-online.de/sso/login")
    # access content
    content = driver.page_source
    soup = BeautifulSoup(content, 'xml')

    # find username and password input
    username = driver.find_element_by_name('username')
    password = driver.find_element_by_name('password')

    # einloggen
    username.send_keys("")
    password.send_keys("")
    # submit
    driver.find_element_by_class_name('park-button').click()

    # accept cookies
    try:
        driver.find_element_by_id('onetrust-accept-btn-handler').click()
    except:
        pass

    # eilmeldungen und Lesetipps blockieren
    try:
        driver.find_element_by_class_name('cleverpush-confirm-btn-deny').click()
    except:
        pass

    # open feed-page
    driver.get('https://rp-online.de/feed.rss')

    # access content
    content = driver.page_source
    soup = BeautifulSoup(content, 'xml')

    # access all the links
    items = soup.findAll('item')
    articles = []
    for item in items:
        title = item.find('title').text

        paywall_wrap = item.find('content_tier')
        if paywall_wrap.text == 'locked':
            paywalled = 1
        else:
            paywalled = 0
        # print(paywalled)

        link = item.find('link').text
        # print(link)

        categor = []
        cats = item.findAll('category')
        for category in cats:
            categor.append(category.text)
        categories = ' '.join(categor)

        published = item.find('pubDate').string.strip()

        # follow link
        try:
            driver.get(link)
        except:
            pass

        newcontent = driver.page_source
        soup = BeautifulSoup(newcontent, "html.parser")

        teaserwrapper = soup.find('div', {'class': 'park-article__body'})
        teaser = teaserwrapper.find('p', {'class': 'park-article__intro'}).text

        # get fulltext
        posts = soup.findAll('div', {'class': 'park-article-content'})
        fulltext = []
        for art in posts:
            try:
                paragraph = art.find('p', recursive=False).text
                # print(paragraph)
                fulltext.append(paragraph)
            except:
                pass
        joined_text = ' '.join(fulltext)
        # print(joined_text)

        art_id = "RP-" + published + joined_text[9:11]

        article = {
            'id': art_id,
            'title': title,
            'link': link,
            'teaser': teaser,
            'text': joined_text,
            'category': categories,
            'published': published,
            'paywall': paywalled
        }
        # print(article)
        articles.append(article)

    current_time = str(datetime.datetime.now())
    fileName = 'RP-' + current_time + '.json'

    uploadByteStream = bytes(json.dumps(articles).encode('UTF-8'))

    s3.put_object(Bucket=bucket, Key=fileName, Body=uploadByteStream)

    print('Put complete')

    # return {
#     'statusCode': 200,
#     'body': json.dumps('Hello from Lambda!')
# }
if __name__ == '__main__':
    lambda_handler(None, None)