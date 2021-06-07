from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
import re

def login(driver):
    # open start-page
    driver.get("https://www.bild.de")

    # access content
    content = driver.page_source
    soup = BeautifulSoup(content)

    # access iframe to accept cookies
    frame = driver.find_element_by_xpath("//*[@id='sp_message_iframe_440195']")
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

    submit = driver.find_element_by_id('login-form-submit')
    submit.click()

    # kurz warten
    time.sleep(2)


def get_bild_contents(driver):
    # open start-rss-page
    driver.get("https://www.bild.de/rss-feeds/rss-16725492,feed=news.bild.html")

    # access content
    content = driver.page_source
    soup = BeautifulSoup(content, 'xml')

    # access all the links
    articles = []
    items = soup.findAll('item')

    for item in items:
        title = item.find('title').text
        link = item.find('guid').text

        # teaser=item.find('description') #ist besser auf der Hauptseite, Darstellung hier messy
        cats = item.find_all('category')
        categories = []
        for category in cats:
            categories.append(category.text)
        published = item.find('pubDate').text

        paywall = re.compile('([\*]+).\w*.\w*.([\*]+)')
        is_paywalled = paywall.findall(title)

        if len(is_paywalled) > 0:
            paywalled = True
            title = re.sub(r'([\*]+).\w*.\w*.([\*]+)', "", title)
        else:
            paywalled = False
        print(title)
        print(paywalled)

        # follow link
        try:
            driver.get(link)
        except:
            pass

        newcontent = driver.page_source
        soup = BeautifulSoup(newcontent, "lxml")

        # find teaser
        try:
            teaserwrapper = soup.find('div', {'class': 'article-body'}).find('p', recursive=False)
            teaser = teaserwrapper.find('b', recursive=False).text
        except:
            pass

        # get fulltext
        try:
            articles = soup.find('div', {'class': 'article-body'})

            paragraphs = articles.find_all('p')

            fulltext = []
            for p in paragraphs:
                if p.text and not p.has_attr("class"):
                    paragraph = p.text
                    fulltext.append(paragraph)
                    print(p.text)
                else:
                    paragraphs = p.findChildren('p', recursive=False)
                    for p in paragraphs:
                        fulltext.append(p.text)

            joined_text = ' '.join(fulltext)

            article = {
                'title': title,
                'link': link,
                'teaser': teaser,
                'text': joined_text,
                'category': categories,
                'published': published
            }
            # print(article)
            articles.append(article)
        except:
            pass
    return articles

if __name__ == '__main__':
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    login(driver)
    get_bild_contents(driver)