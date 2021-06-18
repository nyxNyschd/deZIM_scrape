import asyncio
import time
from pyppeteer import launch
from bs4 import BeautifulSoup
import pandas as pd
import datetime


async def take_screenshot(url, browser, page):
    await page.goto(url)
    await page.setViewport({'width': 800, 'height': 1000})
    if not await page.J('.cmpboxbtnyes'):
        current_time = str(datetime.datetime.now())
        screenshot = await page.screenshot({'path': './waz_'+current_time+'.jpg', 'type': 'jpeg', 'fullPage': True})
    else:
        await page.evaluate('''() =>
        {
           const accept_button = document.getElementsByClassName('cmpboxbtnyes')[0];
          accept_button.click();    
        }''')
        screenshot = await page.screenshot({'path': './waz.jpg', 'type': 'jpeg', 'fullPage': True})


async def login(url,browser,page):

    await page.goto(url, {'waitUntil' : 'domcontentloaded'})
    time.sleep(10)
    if not await page.J('.cmpboxbtnyes'):
        time.sleep(5)
        try:
            await page.evaluate('''() =>
            {
               const deny_notes = document.getElementsByClassName('cleverpush-confirm-btn-deny')[0];
              deny_notes.click();

            }''')
        except:
            pass

        # open login-dropdown
        await page.evaluate('''() =>
            {
               const drop_login = document.getElementsByClassName('header-top-button--login')[0];
              drop_login.click();
            }''')
    else:
        await page.evaluate('''() =>
            {
               const accept_button = document.getElementsByClassName('cmpboxbtnyes')[0];
              accept_button.click();

              const drop_login = document.getElementsByClassName('header-top-button--login')[0];
              drop_login.click();
            }''')

    # enter iframe
    time.sleep(5)
    login_frame = await page.waitForSelector('#offer_72271bc88fe7a326d330-0')

    frame_access = await login_frame.contentFrame()

    # login
    await frame_access.type('input', '')
    time.sleep(3)
    await frame_access.type('#password', '')

    # submit login
    time.sleep(5)
    await frame_access.evaluate('''() =>
        {
           const submit_button = document.querySelector('input.col-33:nth-child(3)').click();
        }''')
    time.sleep(5)

    # agree to cookies/block notifications
    try:
        await page.waitForSelector('.cleverpush-confirm-btn-deny')
        await page.evaluate('''() =>
        {
           const deny_notes = document.getElementsByClassName('cleverpush-confirm-btn-deny')[0];
          deny_notes.click();
    
        }''')
    except:
        pass

async def scrape_page(url,browser,page):
    await login(url,browser,page)

    # follow links, get entire html of the page, then parse it with beautiful soup from there
    links = []
    linkwrappers = await page.querySelectorAll('.teaser__link')
    for wrap in linkwrappers:
        links.append(await page.evaluate('(wrap) => wrap.href', wrap))

    articles = []
    for link in links:
        try:
            await page.goto(link)
            #print(link)

            # get html
            if not await page.J('.cmpboxbtnyes'):
                try:
                    await page.evaluate('''() =>
                    {
                       const deny_notes = document.getElementsByClassName('cleverpush-confirm-btn-deny')[0];
                      deny_notes.click();
    
                    }''')
                except:
                    pass
            else:
                await page.evaluate('''() =>
                {
                   const accept_button = document.getElementsByClassName('cmpboxbtnyes')[0];
                  accept_button.click();
    
                }''')

            html = await page.evaluate('() => document.documentElement.outerHTML')

            # hand html to BeautifuSoup
            soup = BeautifulSoup(html, 'html.parser')

            title = soup.find('h2', {'class': 'article__header__headline'}).text

            teaserwrap = soup.find('meta', {'name': 'description'})
            teaser = (teaserwrap['content'])

            categorywrapper = soup.find('meta', {'name': 'keywords'})
            categories = (categorywrapper['content'])

            publish_info = soup.find('meta', {'name': 'DC.date.issued'})
            published = (publish_info['content'])

            #scraping full-text
            fulltext = []
            articlewrapper = soup.find('main', {'class': 'main'}).find('article', {'class': 'article--type-news'})
            art = articlewrapper.find('div', {'class': 'article__body'})

            paragraphs = art.findChildren('p', {'class': 'article__paragraph'})
            for paragraph in paragraphs:
                try:
                    paragraph = paragraph.text
                    fulltext.append(paragraph)
                except:
                    continue
            joined_text = ' '.join(fulltext)
            #print('text__: '+joined_text)

            #get paywall-info
            paywall_info = soup.find('meta', {'property': 'article:content_tier'})
            is_paywall = (paywall_info['content'])
            if is_paywall == 'locked':
                paywalled = 1
            else:
                paywalled = 0

            art_id = "WAZ-" + published + joined_text[9:11]

            # assemble and append article
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

            articles.append(article)
        except:
            pass

        dataframe = pd.DataFrame(articles)
    return dataframe


async def run():
    url = 'https://www.waz.de/'
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await take_screenshot(url,browser,page)
    await scrape_page(url, browser, page)
    await browser.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run())
    loop.run_until_complete(future)
