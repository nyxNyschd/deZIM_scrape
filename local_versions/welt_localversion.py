import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time


def login(driver):

    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # enter iframe
    frame = driver.find_element_by_id('sp_message_iframe_440191')
    driver.switch_to.frame(frame)

    # accept cookies
    accept = driver.find_element_by_xpath("//button[@title='Alle akzeptieren']")
    accept.click()

    #go to login-page
    login = driver.get("https://lo.la.welt.de/login?target=https%3A%2F%2Fwww.welt.de%2F")

    # locate and activate login-field
    loginform = driver.find_element_by_id('login-form')

    activate_login = loginform.find_element_by_xpath("//div[@data-testid='username']").click()
    username = driver.find_element_by_xpath("//input[@name='username']")
    username.send_keys("mayer@dezim-institut.de")

    # locate and activate password-field
    activate_password = loginform.find_element_by_xpath("//div[@data-testid='password']").click()
    password = driver.find_element_by_xpath("//input[@name='password']")
    password.send_keys("ImgesIIbild")

    # login
    submit = driver.find_element_by_id('login-form-submit').click()


def get_welt_fulltexts(driver):

    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # get links
    links = []
    articlesections = soup.findAll('ul', {'class': 'c-grid'})

    for section in articlesections:
        article_items = section.findAll('article', {'class': 'o-teaser'})
        for arts in article_items:
            try:
                link = arts.find('a', {'data-content': 'Teaser.Link'})['href']
                substring = 'https://www.welt.de'
                if substring in link:
                    link = link
                    links.append(link)
                    print(link)
                elif link == 'http://https//jobs.welt.de/':
                    continue
                else:
                    link = substring + link
                    links.append(link)
                    print(link)
            except TypeError:
                pass

            # follow links
        articles = []
        for link in links:
            try:
                driver.get(link)

                newcontent = driver.page_source
                soup = BeautifulSoup(newcontent)

                # try:
                main = soup.find('main', {'class': 'c-page-container--has-detailed-content'})
                titlewrapper = main.find('h2', {'class': 'c-headline'})  # o-dreifaltigkeit__headline
                title = titlewrapper.text
                # print(title)

                categories = []
                categorywrapper = soup.find('meta', {'name': 'keywords'})
                categories = (categorywrapper['content'])
                # print(categories)

                date = soup.find('meta', {'name': 'date'})
                published = (date['content'])

                teaser = soup.find('meta', {'name': 'description'})['content']

                fulltext = []
                paragraphs = soup.find('div', {'class': 'c-article-text'})
                paragraphs = soup.findChildren('p')
                for paragraph in paragraphs:
                    try:
                        paragraph = paragraph.text
                        fulltext.append(paragraph)
                    except:
                        continue
                joined_text = ' '.join(fulltext)

                if soup.find('div',{'data-paycategory' : 'PAID'}):
                    paywalled=1
                else:
                    paywalled=0

                art_id= "SZ-"+published+joined_text[9:11]

                article = {
                 'id':art_id,
                 'title':title,
                 'link': link,
                 'teaser':teaser,
                 'text':joined_text,
                 'category':categories,
                 'published':published,
                 'paywall':paywalled
                 }
                articles.append(article)
            except:
                pass
    return articles

if __name__ == '__main__':
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    driver.get("https://www.welt.de/")
    login(driver)
    get_welt_fulltexts(driver)
