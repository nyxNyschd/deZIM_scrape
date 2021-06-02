# deZIM_scrape
As part of a project accompanying voters' decisions around the national elections in Germany, I am scraping several newspapers,
dumping the articles into an S3 bucket.
The folder "local_versions" contains the scraping-scripts I built locally with Jupyter Notebook and Python
The folder "lambda_versions" contains the scripts I built on/with AWS Lambda, including the dump to S3. In order to make 
the functions work on AWS, they need Lambda layers I created with the .zip-files. 
