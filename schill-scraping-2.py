import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Main page URL
main_url = 'https://www.northwestern.edu/leadership-notes/'  # Replace with the actual URL
response = requests.get(main_url)

# Create a directory to store the text files
output_dir = 'scraped_articles'
os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

if response.status_code == 200:
    print("Main page retrieved successfully.")
    
    # Parse the main page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find and collect all the links (adjust the selector as needed)
    links = soup.find_all('a', href=True)
    urls_to_scrape = []

    # Construct full URLs from links and store them
    for link in links:
        href = link.get('href')
        # Make sure the href is not None and check if it starts with a year (as opposed to another NU page like admissions)
        if href and href.startswith('2'):
                # Check if main_url ends with a slash; if it doesn't, add one
            if not main_url.endswith('/'):
                main_url += '/'
            
            full_url = f"{main_url}{href}"  # Create full URL 
            urls_to_scrape.append(full_url)
            
    else:
        print("This link is not a leadership message")


    # Date to filter posts (October 7, 2023)
    target_date = datetime(2023, 10, 7)

    # Step 2: Scrape each linked page
    for url in urls_to_scrape:
        #test_url = urls_to_scrape[5] # Access the first URL
        #print(f"Scraping {test_url}...")
        #print(f"Scraping {url}...")
        page_response = requests.get(url)
        
        if page_response.status_code == 200:
            page_soup = BeautifulSoup(page_response.content, 'html.parser')
            #   Find the div with the content
            main_content = page_soup.find('div', id='news-story')

            if main_content:

                # Extract the date from the article (adjust the tag and class to match where the date is stored)
                date_tag = page_soup.find('div', class_='story-date')  # Adjust selector
                title_text = page_soup.find('h2').get_text() if page_soup.find('h2') else ''

                
                if date_tag:
                    # Get the date text and parse it
                    date_string = date_tag.get_text(strip=True)
                    try:
                        post_date = datetime.strptime(date_string, '%B %d, %Y')  # Adjust format
                        print(f"Found post titled {title_text}, from {post_date}")

                        # Filter based on the target date
                        if post_date > target_date:
                            # print(f"Post from {post_date} is after {target_date}. Scraping content...")

                            # Extract text from the post (adjust selector as needed)
                            paragraphs = page_soup.find_all('p')
                            for paragraph in paragraphs:
                                print(paragraph.get_text())
                                article_text = "\n".join(paragraph.get_text() for paragraph in paragraphs)

                        
                            # Create a filename based on the title or URL
                            filename = f"{output_dir}/{title_text.replace('/', '-')}.txt"  # Replace slashes to avoid path issues

                            # Write the text to a file
                            with open(filename, 'w', encoding='utf-8') as file:
                                file.write(article_text)

                            print(f"Saved article to {filename}")
                        else:
                            print(f"Post from {post_date} is before the target date. Not scraping.")
                    except ValueError:
                        print(f"Could not parse date: {date_string}")
                else:
                    print("No date found in this post.")
            else:
                print(f"Failed to retrieve {url}")
    else:
        print("Failed to retrieve the main page.")
