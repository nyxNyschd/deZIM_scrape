
from selenium import webdriver
from bs4 import BeautifulSoup
import json
from selenium.webdriver.common.by import By

def login(driver):
    # openpage
    driver.get("https://www.waz.de/")

    content = driver.page_source
    soup = BeautifulSoup(content)
    try:
        accept = driver.find_element_by_class_name('cmpboxbtnyes').click()
    except:
        pass

    # open login-dropdown
    driver.find_element_by_class_name('header-top-button--login').click()

    # enter iframe
    frame = driver.find_element_by_id('offer_72271bc88fe7a326d330-0')
    driver.switch_to.frame(frame)

    #access login-form
    userwrapper = driver.find_element_by_class_name("input-container")
    username = userwrapper.find_element_by_xpath(".//input")
    username.click()

    #login
    username.send_keys("")
    password = driver.find_element_by_id('password')
    password.send_keys("")
    submit = userwrapper.find_element_by_xpath("//input[@type='submit']").click()

    # exit iframe
    driver.switch_to.default_content()

    # turn off notifications if they ask again
    try:
        deny = driver.find_element_by_class_name('cleverpush-confirm-btn-deny').click()
    except:
        pass

def get_waz_fulltexts(driver):
    driver.get("https://www.waz.de/")
    try:
        close_welcome_crap = driver.find_element_by_xpath("//button[@aria-label='Close']").click()
    except:
        pass

    # turn off notifications
    try:
        deny = driver.find_element_by_class_name('cleverpush-confirm-btn-deny').click()
    except:
        pass

    links = driver.find_elements_by_class_name('teaser__link')
    for link in links:
        link = link.get_attribute('href')
        # follow link
        driver.get(link)

        newcontent = driver.page_source
        soup = BeautifulSoup(newcontent)

        try:
            close_welcome_crap = driver.find_element_by_xpath("//button[@aria-label='Close']").click()
        except:
            pass
        # turn off notifications
        try:
            deny = driver.find_element_by_class_name('cleverpush-confirm-btn-deny').click()
        except:
            pass
        title = soup.find('title').text

        teaserwrap = soup.find('meta', {'name': 'description'})
        teaser = (teaserwrap['content'])

        categories = []
        categorywrapper = soup.find('meta', {'name': 'keywords'})
        categories = (categorywrapper['content'])

        articlewrapper = soup.find('main', {'class': 'main'}).find('article', {'class': 'article--type-news'})

        published = articlewrapper.find('div', {'class': 'author'}).find('time', {'class': 'author__time'}).text

        fulltext = []
        art = articlewrapper.find('div', {'class': 'article__body'})
        paragraphs = art.findChildren('p', {'class': 'article__paragraph'})
        for paragraph in paragraphs:
            try:
                paragraph = paragraph.text
                # print(paragraph)
                fulltext.append(paragraph)
            except:
                continue
        joined_text = ' '.join(fulltext)

        is_paywall = driver.find_elements_by_xpath("//meta[@content='locked']")

        if len(is_paywall) > 0:
            paywalled = 1
        else:
            paywalled = 0

        #published = published

        art_id = "WAZ-" + published + joined_text[9:11]
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

if __name__ == '__main__':
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    login(driver)
    get_waz_fulltexts(driver)