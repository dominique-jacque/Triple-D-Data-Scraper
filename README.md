# Triple-D-Data-Scraper
Triple D Data Scraper is a Python-based web scraping project that extracts restaurant data from the Diners, Drive-Ins, and Dives website. The project retrieves restaurant names, addresses, phone numbers, websites, and episode information for various states. The scraped data is saved as a CSV file and uploaded to an AWS S3 bucket for storage.

## Features
- Scrapes restaurant data for all 50 U.S. states.
- Handles pagination to capture all available records.
- Uses multithreading for efficient scraping.
- Saves data as a CSV file.
- Uploads the CSV file to an AWS S3 bucket.

## Tech Stack
- Python
- Requests (for HTTP requests)
- BeautifulSoup (for web scraping)
- Pandas (for data processing)
- Boto3 (for AWS S3 integration)
- ThreadPoolExecutor (for concurrent execution)

## Next Steps
Futurer improvements include integrating more AWS services to improve automation, security, and scalability. 
- AWS Lambda: Automate scraping via serverless execution.
- Amazon EventBridge: Schedule automated scraping.
- DynamoDB: Store structured data for fast queries.
- AWS Step Functions: Manage multi-step workflows.
- Amazon SNS: Notify users when data updates.
- Amazon Athena: Enable SQL queries on scraped data.
- API Gateway: Provide an API for querying restaurant data.
