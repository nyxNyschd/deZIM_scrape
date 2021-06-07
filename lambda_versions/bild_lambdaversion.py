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
    options.add_argument('--disable-gpu')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--window-size=1280,1696')
    options.add_argument('--user-data-dir=/tmp/user-data')
    options.add_argument('--data-path=/tmp/data-path')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--enable-logging')
    options.add_argument('--log-level=0')
    options.add_argument('--v=99')
    options.add_argument("--start-maximized")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--homedir=/tmp')
    options.add_argument('--disk-cache-dir=/tmp/cache-dir')

    driver = webdriver.Chrome('/opt/bin/chromedriver', chrome_options=options)

    driver.get("https://www.bild.de")

    # access content
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # access iframe to accept cookies
    time.sleep(5)
    frame = driver.find_element_by_xpath("//iframe[@title='SP Consent Message']")
    driver.switch_to.frame(frame)

    # accept cookies
    accept = driver.find_element_by_xpath("//button[text()='Alle akzeptieren']").click()

    # find login-icon
    loginwrapper = soup.find('ul', {'class': 'utilities'}).find('li', {'class': 'community_loggedout'})

    try:
        url = loginwrapper.find('a', recursive=False)['href']
    except TypeError:
        pass

    # open login-page
    driver.get(url)

    # locate login-field
    username = driver.find_element_by_name('username')
    password = driver.find_element_by_name('password')

    # einloggen
    username.send_keys("")
    password.send_keys("")

    # submit
    submit = driver.find_element_by_id('login-form-submit')
    submit.click()

    # kurz warten
    time.sleep(2)

    # open start-rss-page
    driver.get("https://www.bild.de/rss-feeds/rss-16725492,feed=news.bild.html")

    # access content
    content = driver.page_source
    soup = BeautifulSoup(content, 'xml')

    # access all the links
    items = soup.findAll('item')
    articles = []

    for item in items:
        title = item.find('title').text
        paywall = re.compile('([\*]+).\w*.\w*.([\*]+)')
        is_paywalled = paywall.findall(title)

        if len(is_paywalled) > 0:
            paywalled = 1
            title = re.sub(r'([\*]+).\w*.\w*.([\*]+)', "", title)
        else:
            paywalled = 0

        link = item.find('guid').text

        # teaser=item.find('description') #ist besser auf der Hauptseite, Darstellung hier messy
        cats = item.find_all('category')
        categors = []
        for category in cats:
            categors.append(category.text)
        categories = ' '.join(categors)
        published = item.find('pubDate').text

        # follow link
        try:
            driver.get(link)
        except:
            pass

        # access content of article
        newcontent = driver.page_source
        soup = BeautifulSoup(newcontent, 'html.parser')

        # find teaser
        try:
            teaserwrapper = soup.find('div', {'class': 'article-body'}).find('p', recursive=False)
            teaser = teaserwrapper.find('b', recursive=False).text

            # getting fulltext
            posts = soup.find('div', {'class': 'article-body'})
            paragraphs = posts.find_all('p')
            fulltext = []
            for p in paragraphs:
                if p.text and not p.has_attr("class"):
                    paragraph = p.text
                    fulltext.append(paragraph)
                    # print(p.text)
                else:
                    paragraphs = p.findChildren('p', recursive=False)
                    for p in paragraphs:
                        fulltext.append(p.text)

            joined_text = ' '.join(fulltext)

            art_id = "Bild-" + published + joined_text[9:11]

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

        except:
            pass

    current_time = str(datetime.datetime.now())
    fileName = 'Bild-' + current_time + '.json'

    uploadByteStream = bytes(json.dumps(articles).encode('UTF-8'))

    s3.put_object(Bucket=bucket, Key=fileName, Body=uploadByteStream)

    # print('Put complete')

    # return {
    #    'statusCode': 200,
    #    'body': json.dumps('hellohelloooo')
# }

