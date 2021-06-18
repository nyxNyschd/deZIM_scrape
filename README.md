# deZIM_scrape
This is a Python project, scraping newspapers articles and taking screenshots of the newspapers with AWS lambda and S3, Pyppeteer and asyncio, Selenium and Beautiful Soup. 
This project is part of a study accompanying voters' decisions around the national elections in Germany.


The folder "**pyppeteer_w_screenshot**" contains: login, taking the html-content and a screenshot of all the pages with **pyppeteer**. scraping with **bs4**, 
returning a dataframe

The folder "**local_versions**" contains scraping newspaper contents with **Selenium** and **BS4**.

The folder **"lambda_versions"** contains the **AWS Lambda functions**, including the **dump to S3**. 

folder **lambda-layers:**
.zip-files to build the layers :In order to make your imports work on AWS, 
you need Lambda layers containing the .zip-files in an uploadable path. 
