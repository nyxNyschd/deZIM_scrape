from selenium import webdriver
from bs4 import BeautifulSoup
import json

def login():
    #access content
    content = driver.page_source
    soup = BeautifulSoup(content)

    # accept cookies
    try:
        accept = driver.find_element_by_class_name('cmpboxbtnyes')
        accept.click()
    except:
        pass

    try:
        close_welcome_crap = driver.find_element_by_class_name("cleverpush-confirm-btn-deny']").click()
    except:
        pass

    # open login-dropdown
    driver.find_element_by_class_name('header-top-button--login').click()

    # enter iframe
    frame = driver.find_element_by_id('offer_f4e52180a8a5fa58f9f9-0')
    driver.switch_to.frame(frame)

    #enter login-container
    userwrapper = driver.find_element_by_class_name("input-container")
    username = userwrapper.find_element_by_xpath(".//input")
    username.click()

    #login
    username.send_keys("")
    password = driver.find_element_by_id('password')
    password.send_keys("")
    submit = userwrapper.find_element_by_xpath("//input[@type='submit']").click()

    driver.switch_to.default_content()

def get_nrz_fulltexts(driver):
    content = driver.page_source
    soup = BeautifulSoup(content)
    # get links
    try:
        close_welcome_crap = driver.find_element_by_class_name('cleverpush-confirm-btn-deny').click()
    except:
        pass
    links = []
    linx = driver.find_elements_by_class_name('teaser__link')
    for link in linx:
        link = link.get_attribute('href')
        links.append(link)

    for link in links:
        driver.get(link)
        try:
            close_welcome_crap = driver.find_element_by_class_name('cleverpush-confirm-btn-deny').click()
        except:
            pass
        try:
            driver.find_element_by_xpath("//button[@aria-label='Close']").click()
        except:
            pass

        head = soup.find('head')
        title = head.find('title').text

        teaserwrap = soup.find('meta', {'name': 'description'})
        teaser = (teaserwrap['content'])

        categories = []
        categorywrapper = soup.find('meta', {'name': 'keywords'})
        categories = (categorywrapper['content'])

        time = soup.find('meta', {'name': 'DC.date.issued'})
        published = (time['content'])

        #articlewrapper = soup.find('main', {'class':'main'}).find('article', {'class':'article--type-news'})


    #toDO fulltexts, paywalled --> am besten direkt mit pyppeteer versuchen

if __name__ == '__main__':
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    driver.get("https://www.nrz.de/")
    login(driver)
    get_nrz_fulltexts(driver)