from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

import json
import re
import time


def login(driver):
    # open startpage
    driver.get("https:sueddeutsche.de")
    driver.delete_all_cookies()

    # access iframe to accept cookies
    # erst warten!
    time.sleep(5)
    frame = driver.find_element_by_xpath("//*[@id='sp_message_iframe_511728']")
    driver.switch_to.frame(frame)

    # accept cookies
    accept = driver.find_element_by_xpath('/html/body/div/div[2]/div[3]/div/div/button[1]')
    accept.click()

    # leave iframe, click login-button
    driver.switch_to.default_content()
    driver.set_window_size(1920, 1080)
    login = driver.find_element_by_id('login-toggle').click()
    print('login-toggle clicked')
    time.sleep(5)
   # login = driver.get('https://id.sueddeutsche.de/login')

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
    time.sleep(10)

    try:
        wait = WebDriverWait(driver, 10, poll_frequency=10,
                             ignored_exceptions=[NoSuchElementException, ElementNotVisibleException,
                                                 ElementNotSelectableException])
        wait.until(EC.presence_of_element_located((By.XPATH, "//body[class='no-touch']")))

        failed= driver.find_element_by_xpath('//body[class="no-touch"]')

        if failed:
            print('login failed!')
            logoutwrap= driver.find_element_by_class_name('profile')
            logoutform = logoutwrap.find_element_by_xpath("./child::form")
            logout = logoutform.find_element_by_xpath("./child::button")
            logout.click()
            login(driver)
        else:
            print("logged in")
    except:
        pass
    # falls dann nochmal accept-box kommt
    try:
        frame_members = driver.find_element_by_xpath("//*[@id='sp_message_iframe_511728']")
        driver.switch_to.frame(frame_members)
        # accept "weniger werbung für digital abo"
        accept = driver.find_element_by_xpath("//button")
        accept.click()
    except:
        pass

def get_sz_fulltexts(driver):
    login(driver)
    # open feed-page
    driver.get("https://rss.sueddeutsche.de/rss/Topthemen")
    time.sleep(10)
    driver.get("https://rss.sueddeutsche.de/rss/Topthemen")
    print("opened feeds")
    # access content
    content = driver.page_source
    soup = BeautifulSoup(content, 'xml')
    # access all the links
    articles = []
    items = soup.findAll('item')
    print('found items')

    for item in items:
        title = item.find('title').text
        link = item.find('link').text
        #print(link)

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
        driver.get(link)

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

        #case ticker
        try:
            tickerwraps = soup.find('ul', {'class': 'tikjs-event-list'}).findChildren('li', recursive=False)
            for ticker in tickerwraps:
                fulltext.append(ticker.text)
        except:
            pass

        # normal article
        articlewrap= soup.find('div',{'data-testid': 'article-body'})
        paragraphs = articlewrap.find_all('p', {'class': 'css-13wylk3'})
        for paragraph in paragraphs:
            fulltext.append(paragraph.text)
            #print(paragraph.text)

        joined_text = ' '.join(fulltext)
        #print(fulltext)

        if soup.find('div', {'data-paycategory': 'PAID'}):
            paywalled = 1
        else:
            paywalled = 0
        #print(paywalled)

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
        print(article)
        articles.append(article)
        time.sleep(5)
    driver.find_element_by_class_name('loggedin').click()
    time.sleep(5)
    logoutwrap = driver.find_element_by_class_name('profile')
    logoutform = logoutwrap.find_element_by_xpath("./child::form")
    logout = logoutform.find_element_by_xpath("./child::button")
    logout.click()
        #driver.find_element_by_xpath('//button[text()="Logout"]').click()
    # print(articles)

if __name__ == '__main__':
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", options=options)
    get_sz_fulltexts(driver)
    driver.delete_all_cookies()
    driver.quit()

