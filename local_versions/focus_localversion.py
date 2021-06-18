from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import re
import lxml

options = Options()
#options.add_argument('--headless')
options.add_argument('--no-sandbox')

def get_focus_fulltexts():
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", options=options)
    # open feed-page
    driver.get("https://rss.focus.de/fol/XML/rss_folnews.xml")
    content = driver.page_source
    soup = BeautifulSoup(content, 'lxml')

    articles = soup.findAll('item')
    for post in articles:
        teaser_raw = post.find('description').text
        teaser = re.sub(r"^[ \n(\t)*]+", "", teaser_raw)
        category = post.find('category').text
        published = post.find('pubdate').string.strip()
        title = post.find('title').text
        link = post.find('link').text

        # follow link
        driver.get(link)

        newcontent = driver.page_source
        soupy = BeautifulSoup(newcontent, 'html.parser')

        # accept cookies:
        try:
            # enter iframe
            frame = driver.find_element_by_id('sp_message_iframe_448514')
            driver.switch_to.frame(frame)

            # datenschutz-zustimmung
            driver.find_element_by_xpath("//button[@title='Akzeptieren']").click()

            # back to content
            driver.switch_to.default_content()
        except:
            pass

            # extract fulltext for current link
        fulltext = []
        sect = soupy.find_all('div', {'class': 'textBlock'})
        for s in sect:
            children = s.findChildren("p", recursive=False)
            for child in children:
                fulltext.append(child.text)

        text = ' '.join(fulltext)
        joined_text = re.sub(
            r"^.*/\xa0.*",
            " ", text)
        # print(joined_text)
        art_id = "focus-" + published + joined_text[9:11]
        # print(art_id)

        article = {
            'id': art_id,
            'title': title,
            'link': link,
            'teaser': teaser,
            'text': joined_text,
            'category': category,
            'published': published
        }
        articles.append(article)
    return articles


if __name__ == '__main__':

    get_focus_fulltexts()