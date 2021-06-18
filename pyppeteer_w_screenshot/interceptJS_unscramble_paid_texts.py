import asyncio
import time
from pyppeteer import launch
from pyppeteer.network_manager import NetworkManager, Response, Request
from pyppeteer.errors import TimeoutError
from bs4 import BeautifulSoup
import pandas as pd

async def interceptResponse(response):
    url = 'https://www.waz.de/'

    if not response.ok:
        print('request %s failed' % url)
        return
    elif "text/html" in response.headers.get("content-type", ""):
            # Print some info about the responses
            print("URL:", response.url)
            print("Method:", response.request.method)
            print("Response headers:", response.headers)
            print("Request Headers:", response.request.headers)
            print("Response status:", response.status)
            # Print the content of the response
            content= await response.text()
            print("Content: ", content)
            # NOTE: Use await response.json() if you want to get the JSON directly
            return content


async def login(url, browser, page):
    await page.goto(url, {'waitUntil': 'domcontentloaded'})
    time.sleep(10)
    if not await page.J('.cmpboxbtnyes'):
        time.sleep(10)
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
    time.sleep(10)
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


async def get_locked_content(url, browser, page):
    await login(url, browser, page)

    # follow links, get entire html of the page, then parse it with beautiful soup from there
    links = []
    linkwrappers = await page.querySelectorAll('.teaser__link')
    for wrap in linkwrappers:
        links.append(await page.evaluate('(wrap) => wrap.href', wrap))

    articles = []
    for link in links:
      #  try:
        await page.goto(link)

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
        try:
            # hand html to BeautifuSoup
            soup = BeautifulSoup(html, 'html.parser')
            paywall_info = soup.find('meta', {'property': 'article:content_tier'})
            is_paywall = (paywall_info['content'])
            if is_paywall == 'locked':
               # paywalled = 1
                print('Its paywalled: intercepting response')
                page.on('response',  lambda response: asyncio.ensure_future(interceptResponse(response)))
                await page.goto(link)

            else:
               # paywalled = 0
                print('Free content: good to go')
                #return soup  --> call method to scrape with beautiful soup
            #except:
            #    pass

        except:
            pass



async def run():
    url = 'https://www.waz.de/'
    browser = await launch(headless=False, devtools=True, args=['--no-sandbox'])
    page = await browser.newPage()
   # page.on('response',
     #      lambda response: asyncio.ensure_future(interceptResponse(response)))
    await page.goto(url)

    await get_locked_content(url, browser, page)
    await browser.close()
    return

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    #future = asyncio.ensure_future(run())
    loop.run_until_complete(run())



