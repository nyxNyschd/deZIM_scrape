from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
import json

def login(driver):

    # access content
    content = driver.page_source
    soup = BeautifulSoup(content)

    # find login-icon
    url = soup.find('a', {'class': 'headline__login-link'})['href']

    # open login-page
    driver.get(url)

    # locate login-field
    login = driver.find_element_by_id('login_email')
    pw = driver.find_element_by_id('login_pass')

    # einloggen
    login.send_keys("")
    pw.send_keys("")

    submit = driver.find_element_by_class_name('submit-button')
    submit.click()

    # enter iframe
    # frame = driver.find_element_by_id('sp_message_iframe_494009')
    # WAIT!! until element da!!!
    wait = WebDriverWait(driver, 10, poll_frequency=10,
                         ignored_exceptions=[NoSuchElementException, ElementNotVisibleException,
                                             ElementNotSelectableException, TimeoutException])
    wait.until(EC.presence_of_element_located((By.XPATH, "//iframe[@title='SP Consent Message']")))
    frame = driver.find_element_by_xpath("//iframe[@title='SP Consent Message']")

    driver.switch_to.frame(frame)

    # werbung akzeptieren
    try:
        accept = driver.find_element_by_xpath("//button[@title='EINVERSTANDEN']")
        accept.click()
    except:
        pass

    # leave iframe
    driver.switch_to.default_content()


def get_zeit_fulltexts(driver):
    # access content
    content = driver.page_source
    soup = BeautifulSoup(content)

    #find article-links
    content = driver.page_source
    soup = BeautifulSoup(content)

    links = []
    main = soup.find('main', {'id': 'main'})
    wrappers = main.findAll('div', {'class': 'cp-region--standard'})
    for wrapper in wrappers:

        head_links = wrapper.findAll('a', {'class': 'zon-teaser-classic__combined-link'})
        for link in head_links:
            link = link['href']
            links.append(link)
            # print(link)

        standard_links = soup.findAll('a', {'class': 'zon-teaser-standard__combined-link'})
        for link in standard_links:
            link = link['href']
            if link != "https://sudoku.zeit.de/":
                links.append(link)
                # print(links)
    articles = []
    # try:
    for link in links:
        driver.get(link)

        newcontent = driver.page_source
        soup = BeautifulSoup(newcontent)

        try:
            main = soup.find('main', {'id': 'main'})
            titlewrapper = main.find('h1', {'class': 'article-heading'})
            title = titlewrapper.find('span', {'class': 'article-heading__title'}).text

            categories = []
            categorywrapper = soup.find('meta', {'name': 'keywords'})
            categories = (categorywrapper['content'])
            # print(categories)

            date = soup.find('meta', {'name': 'date'})
            published = (date['content'])

            teaser = soup.find('meta', {'name': 'description'})['content']

            fulltext = []
            paragraphs = soup.findChildren('p', {'class': 'paragraph'})
            for paragraph in paragraphs:
                fulltext.append(paragraph.text)
            joined_text = ' '.join(fulltext)
            # print(joined_text)

            categories = []
            categorywrapper = soup.find('meta', {'name': 'keywords'})
            categories = (categorywrapper['content'])
            # print(categories)

            date = soup.find('meta', {'name': 'date'})
            published = (date['content'])

            teaser = soup.find('meta', {'name': 'description'})['content']

            fulltext = []
            paragraphs = soup.findChildren('p', {'class': 'paragraph'})
            for paragraph in paragraphs:
                fulltext.append(paragraph.text)
            joined_text = ' '.join(fulltext)

            art_id = "Zeit-" + published + joined_text[9:11]
            # print(art_id)

            article = {
                'id': art_id,
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
        # print(articles)
        articles_json = json.dumps(articles)

    return articles_json


if __name__ == '__main__':
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    driver.get('https://www.zeit.de/')
    login(driver)
    get_zeit_fulltexts(driver)