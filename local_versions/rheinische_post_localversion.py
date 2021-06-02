from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re

def login(driver):
    # open login-page
    driver.get("https://rp-online.de/sso/login")

    # access content
    content = driver.page_source
    soup = BeautifulSoup(content, 'xml')

    # find username and password input
    username = driver.find_element_by_name('username')
    # wooow: die ändern die ID täglich!!!

    password = driver.find_element_by_name('password')

    # einloggen
    username.send_keys("mayer@dezim-institut.de")
    password.send_keys("ImgesIIrp")

    # submit
    driver.find_element_by_class_name('park-button').click()

    # accept cookies
    driver.find_element_by_id('onetrust-accept-btn-handler').click()

    # eilmeldungen und Lesetipps blockieren
    driver.find_element_by_class_name('cleverpush-confirm-btn-deny').click()


def get_fulltext(driver):
    # open start-rss-page
    driver.get('https://rp-online.de/feed.rss')

    # access content
    content = driver.page_source
    soup = BeautifulSoup(content, 'xml')

    # access all the links
    items = soup.findAll('item')
    articles = []

    for article in items:

        title = article.find('title').text
        link = article.find('link').text

        categor = []
        cats = article.findAll('category')
        for category in cats:
            categor.append(category.text)
        categories = ' '.join(categor)

        published = article.find('pubDate').string.strip()

        link = article.find('link').text
        # print(link)

        paywall_wrap = article.find('content_tier')
        if paywall_wrap.text == 'locked':
            paywalled = 1
        else:
            paywalled = 0
        #print(paywalled)

        # follow link
        try:
            driver.get(link)
        except:
            pass
        newcontent = driver.page_source
        soup = BeautifulSoup(newcontent, "html.parser")

        teaserwrapper = soup.find('div', {'class': 'park-article__body'})
        teaser = teaserwrapper.find('p', {'class': 'park-article__intro'}).text

        articls = soup.findAll('div', {'class': 'park-article-content'})
        fulltext = []
        for par in articls:
            try:
                paragraph = par.find('p', recursive=False).text
                fulltext.append(paragraph)
            except:
                pass
        joined_text = ' '.join(fulltext)
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
        print(article)
        articles.append(article)


if __name__ == '__main__':
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    login(driver)
    get_fulltext(driver)