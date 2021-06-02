import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
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

    driver.get('https://www.faz.net/aktuell/')

    # access iframe to accept cookies
    time.sleep(5)
    frame = driver.find_element_by_xpath("//*[@id='sp_message_iframe_488268']")
    driver.switch_to.frame(frame)

    # accept cookies
    wait = WebDriverWait(driver, 10, poll_frequency=10,
                         ignored_exceptions=[NoSuchElementException, ElementNotVisibleException,
                                             ElementNotSelectableException])
    accept = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='ZUSTIMMEN']")))

    # accept= driver.find_element_by_xpath("//button[text()='ZUSTIMMEN']")
    accept.click()
    # return to normal content

    driver.switch_to.default_content()
    driver.get("https://abo.faz.net/login")

    # locate login-input
    time.sleep(5)
    login = driver.find_element_by_id('login-form-email')
    user = "mayer@dezim-institut.de"
    # einloggen
    login.send_keys(user)

    # access password-field marked as not interactable
    pw = driver.find_element_by_id('login-form-password')
    pw.send_keys("ImgesIIfaz2021")

    # submit
    submit = driver.find_element_by_class_name('btn-white-with-border')
    submit.click()

    # open feed-page
    driver.get("https://www.faz.net/rss/aktuell/")
    # access content
    content = driver.page_source
    soup = BeautifulSoup(content, 'lxml')

    # access all the links
    articles = []
    items = soup.findAll('item')
    for item in items:
        time.sleep(5)
        title = item.find('title').text

        link = item.find('guid').text

        teaserwrapper = item.find('description').text
        r = re.compile('<p>(.+?)</p>')
        teaserlist = r.findall(teaserwrapper)
        for tease in teaserlist:
            teaser = tease

        published = item.find('pubdate').string.strip()

        # follow link
        try:
            driver.get(link)
        except:
            pass

        # access content of article
        newcontent = driver.page_source
        soup = BeautifulSoup(newcontent, 'html.parser')

        # find category
        try:
            categorywrapper = soup.find('meta', {'name': 'keywords'})
            categories = (categorywrapper['content'])
        except TypeError:
            try:
                categorywrapper = soup.find('footer', {'class': 'single-entry-meta'})
                categories = (categorywrapper['content'])
            except:
                pass

        # extract fulltext for current article
        fulltext = []

        paragraphs = soup.findAll('p', {'class': 'atc-TextParagraph'})
        for paragraph in paragraphs:
            fulltext.append(paragraph.text)

        joined_text = ' '.join(fulltext)

        paywall_info = driver.find_element_by_tag_name("body").get_attribute('data-iqdselector')
        if paywall_info == 'artikel_paywall':
            paywalled = 1
        else:
            paywalled = 0

        art_id = "FAZ-" + published + joined_text[9:11]

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
    fileName = 'FAZ-' + current_time + '.json'

    uploadByteStream = bytes(json.dumps(articles).encode('UTF-8'))

    s3.put_object(Bucket=bucket, Key=fileName, Body=uploadByteStream)

    print('Put complete')
