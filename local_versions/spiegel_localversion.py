from selenium import webdriver
from bs4 import BeautifulSoup
import time


def login(driver):
    # open start-page
    driver.get("https://www.spiegel.de")

    # access content
    content = driver.page_source
    soup = BeautifulSoup(content)

    # find login-icon
    url = soup.find('a', {'title': 'Jetzt anmelden'})['href']

    # open login-page
    driver.get(url)

    # locate login-field
    login = driver.find_element_by_id('loginname')
    pw = driver.find_element_by_id('password')

    # einloggen
    login.send_keys("")
    pw.send_keys("")

    submit = driver.find_element_by_id('submit')
    submit.click()

    # kurz warten
    time.sleep(2)

    # dann noch der Werbung zustimmen:
    accept = driver.find_element_by_id('sp_message_iframe_449643').click()


def get_spiegel_fulltext(driver):
    try:
        # open start-rss-page
        driver.get("https://www.spiegel.de/schlagzeilen/tops/index.rss")

        # access content
        content = driver.page_source
        soup = BeautifulSoup(content)

        # access all the links
        items = soup.findAll('item')

        for item in items:
            time.sleep(5)
            articles = []

            for article in items:
                title = article.find('title').text

                link = article.find('guid').text
                teaser = article.find('description').text
                category = article.find('category').text
                published = article.find('pubdate').string.strip()

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

                paragraph_wrapper = soup.find_all('div', {'class': 'RichText'})

                for pack in paragraph_wrapper:
                    paragraphs = pack.findChildren("p", recursive=False)

                    for p in paragraphs:
                        fulltext.append(p.text)

                joined_text = ' '.join(fulltext)
                # print(joined_text)

                if soup.find('div', {'data-paycategory': 'PAID'}):
                    paywalled = 1
                else:
                    paywalled = 0

                art_id = "SPi-" + published + joined_text[9:11]

                article = {
                    'id': art_id,
                    'title': title,
                    'link': link,
                    'teaser': teaser,
                    'text': joined_text,
                    'category': category,
                    'published': published,
                    'paywall': paywalled
                }
               # print(article)
                articles.append(article)

    except Exception as e:
        print('Scraping current article failed. See exception: ')
        print(e)
        pass


if __name__ == '__main__':
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    login(driver)
    get_spiegel_fulltext(driver)