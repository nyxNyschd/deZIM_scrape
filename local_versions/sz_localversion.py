from selenium import webdriver
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import json
import re
import time


def login(driver):
    # open startpage
    driver.get("https:sueddeutsche.de")

    # access iframe to accept cookies
    # erst warten!
    time.sleep(5)
    frame = driver.find_element_by_xpath("//*[@id='sp_message_iframe_452113']")
    driver.switch_to.frame(frame)

    # accept cookies
    accept = driver.find_element_by_xpath('/html/body/div/div[2]/div[3]/div/div/button[1]')
    accept.click()

    # leave iframe, click login-button
    driver.switch_to.default_content()
    login = driver.find_element_by_id('login-toggle').click()

    # locate login-input
    login = driver.find_element_by_id('login_login-form')
    # password=driver.find_element_by_id('id_password')

    # einloggen
    user = ""
    login.send_keys(user)

    # access password-field marked as not interactable
    pw = driver.execute_script("document.getElementById('password_login-form').value=''")

    # achtung, ich muss erst NEBEN den frame klicken:
    # dann kann ich erst submit klicken!
    driver.find_element_by_id('login-header').click()

    # submit
    submit = driver.find_element_by_id('authentication-button').click()

    # falls dann nochmal accept-box kommt
    try:
        frame_members = driver.find_element_by_xpath("//*[@id='sp_message_iframe_452112']")
        driver.switch_to.frame(frame_members)
        # accept "weniger werbung für digital abo"
        accept = driver.find_element_by_xpath("//button[@title='Akzeptieren']")
        accept.click()
    except:
        pass

def get_sz_fulltexts(driver):
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
        for teaser in teaserlist:
            teaser = teaser

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
        soup = BeautifulSoup(newcontent)

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

        if soup.find('div', {'data-paycategory': 'PAID'}):
            paywalled = 1
        else:
            paywalled = 0
        print(paywalled)

        art_id = "SZ-" + published + joined_text[9:11]
        # print(art_id)

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
    # print(articles)

if __name__ == '__main__':
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    login(driver)
    get_sz_fulltexts(driver)
