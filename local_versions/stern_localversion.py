
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import re

def get_stern_fulltexts(driver):
    content = driver.page_source
    soup = BeautifulSoup(content, 'xml')

    articles = []
    posts = soup.findAll('item')

    for post in posts:
        title = post.find('title').text

        urlwrap = post.find('link').text
        token = urlwrap.split("?");
        link = token[0]

        teaser_raw = post.find('description').text
        teaser = re.sub(r"^.*/\xa0.*", " ", teaser_raw)

        cats = []
        categories = post.findAll('category')
        for cat in categories:
            caty = cat.text
            # print(caty)
            cats.append(caty)
            category = ' '.join(cats)
        # print(category)

        published = post.find('pubDate').string.strip()
        # follow link

        try:
            driver.get(link)
        except:
            text = post.find('content:encoded').text
            r = re.compile('<p>(.+?)</p>')
            paragraphs = r.findall(text)
            for paragraph in paragraphs:
                text = paragraph
                joined_text = re.sub(r"^.*/\xa0.*", " ", text)

        # access content of article
        newcontent = driver.page_source
        soup = BeautifulSoup(newcontent)

        try:
            # enter iframe
            frame = driver.find_element_by_id('sp_message_iframe_479928')
            driver.switch_to.frame(frame)

            # datenschutz-zustimmung
            driver.find_element_by_xpath("//button[@title='Zustimmen']").click()

            # back to content
            driver.switch_to.default_content()
        except:
            pass

        fulltext = []
        article = soup.find('article', {'class': 'article__main'}).find('div', {'class': 'article__body'})
        paragraphs = article.findAll('p', {'class': 'text-element'})
        for paragraph in paragraphs:
            try:
                p = paragraph.text
                fulltext.append(p)
            except:
                pass
            try:
                p = paragraph.find('span').text
                fulltext.append(p)
            except:
                pass
        newtext = ' '.join(fulltext)
        better_text = re.sub(
            r"^.*/\xa0.*",
            " ", newtext)
        joined_text = re.sub(
            r"^.*/\n*",
            "", better_text)

        art_id = "stern-" + published + joined_text[9:11]
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
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    get_stern_fulltexts(driver)