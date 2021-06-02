from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
import re

driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")

def login(driver):
    # open start-page
    driver.get("https://www.faz.net/aktuell/")

    # access content
    content = driver.page_source
    soup = BeautifulSoup(content)

    # access iframe to accept cookies
    frame = driver.find_element_by_xpath("//*[@id='sp_message_iframe_488268']")
    driver.switch_to.frame(frame)

    # accept cookies
    accept = driver.find_element_by_xpath("//button[text()='ZUSTIMMEN']").click()

    # return to normal content
    driver.switch_to.default_content()

    # open login-page --> der direkte Weg :)
    driver.get("https://abo.faz.net/login")

    # find user-inputfield
    login = driver.find_element_by_id('login-form-email')

    # find pw-inputfield
    pw = driver.find_element_by_id('login-form-password')

    # einloggen
    login.send_keys("mayer@dezim-institut.de")
    pw.send_keys("ImgesIIfaz2021")

    submit = driver.find_element_by_class_name('btn-white-with-border')
    submit.click()


def faz_get_fulltext(driver):
    try:
        # open feed-page
        driver.get("https://www.faz.net/rss/aktuell/")

        # access content
        content = driver.page_source
        soup = BeautifulSoup(content, 'lxml')  # aha: ohne lxml ging nix mehr

        # access all the links
        items = soup.findAll('item')

        for item in items:
            time.sleep(5)
            articles = []

            for article in items:

                title = article.find('title').text
                link = article.find('guid').text
                published = article.find('pubdate').string.strip()
                teaserwrapper = article.find('description').text
                r = re.compile('<p>(.+?)</p>')
                teaserlist = r.findall(teaserwrapper)
                for teaser in teaserlist:
                    teaser = teaser

                    # category gibts nicht  --> keywords von hauptseite

                # follow link
                try:
                    driver.get(link)
                except:
                    pass

                # access content of article
                newcontent = driver.page_source
                soup = BeautifulSoup(newcontent)

                # get categories
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

                if soup.find("data-iqdselector" == "article_paywall"):
                    paywalled = 1

                else:
                    paywalled = 0

                art_id = "FAZ-" + published + joined_text[9:11]

                article = {
                    'art_id':art_id,
                    'title': title,
                    'link': link,
                    'teaser': teaser,
                    'text': joined_text,
                    'category': categories,
                    'published': published,
                    'paywall': paywalled
                }

        articles.append(article)

# print(articles)

    except Exception as e:
        print('Scraping current article failed. See exception: ')
        print(e)
        pass

if __name__ == '__main__':
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    login(driver)
    faz_get_fulltext(driver)