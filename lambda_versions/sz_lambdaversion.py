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

    driver.get('https:sueddeutsche.de')

    # access iframe to accept cookies
    time.sleep(5)
    frame = driver.find_element_by_xpath("//*[@id='sp_message_iframe_452113']")
    driver.switch_to.frame(frame)

    # accept cookies
    accept = driver.find_element_by_xpath('/html/body/div/div[2]/div[3]/div/div/button[1]')
    accept.click()

    driver.get('https://id.sueddeutsche.de/login')

    # locate login-input
    login = driver.find_element_by_id('login_login-form')
    user = "mayer@dezim-institut.de"
    # einloggen
    login.send_keys(user)

    # access password-field marked as not interactable
    pw = driver.execute_script("document.getElementById('password_login-form').value='ImgesIIsz2021'")

    # achtung, ich muss erst NEBEN den frame klicken:
    # dann kann ich erst submit klicken!
    driver.find_element_by_id('login-header').click()

    # submit
    submit = driver.find_element_by_id('authentication-button').click()

    # falls dann nochmal accept-box kommt
    try:
        frame_members = driver.find_element_by_xpath("//*[@id='sp_message_iframe_452112']")
        driver.switch_to.frame(frame_members)

        accept = driver.find_element_by_xpath("//button[@title='Akzeptieren']")
        accept.click()
    except:
        pass

    # open feed-page
    driver.get("https://rss.sueddeutsche.de/rss/Topthemen")
    # access content
    content = driver.page_source
    soup = BeautifulSoup(content, 'xml')

    # access all the links
    articles = []
    items = soup.findAll('item')
    for item in items:
        title = item.find('title').text

        link = item.find('link').text

        teaserwrapper = item.find('description').text

        r = re.compile('<p>(.+?)</p>')
        teaserlist = r.findall(teaserwrapper)

        for tease in teaserlist:
            teaser = tease

        cats = item.find_all('category')
        categories = []

        for category in cats:
            categories.append(category.text)

        published = item.find('pubDate').text

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

        # case newsblog
        try:
            newslist = soup.find('div', {'class': 'css-19lujvc'}).find('ul', recursive=False)
            news = newslist.findChildren('p', recursive=False)
            for p in news:
                fulltext.append(p.text)
        except:
            pass

        # normal article
        paragraphs = soup.find_all('p', {'class': 'css-13wylk3'})

        for paragraph in paragraphs:
            fulltext.append(paragraph.text)

        joined_text = ' '.join(fulltext)
        # print(joined_text)

        if soup.find('div', {'data-paycategory': 'PAID'}):
            paywalled = 1
        else:
            paywalled = 0

        art_id = "SZ-" + published + joined_text[9:11]

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
        articles.append(article)

    current_time = str(datetime.datetime.now())
    fileName = 'SZ-' + current_time + '.json'

    uploadByteStream = bytes(json.dumps(articles).encode('UTF-8'))

    s3.put_object(Bucket=bucket, Key=fileName, Body=uploadByteStream)

    print('Put complete')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    lambda_handler(None, None)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
