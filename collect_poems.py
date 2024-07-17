import requests
from bs4 import BeautifulSoup
import time

# Function to get the HTML content of the page
def get_html_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the content. Error: {e}")
        return None

# Function to extract poem links from a page
def extract_poem_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    poem_links = []
    
    # Find all links to the poems
    for record_div in soup.find_all('div', class_='record col-12'):
        poem_link_tag = record_div.find('a', class_='float-right')
        if poem_link_tag:
            poem_url = poem_link_tag.get('href')
            if poem_url:
                poem_links.append(poem_url)

    return poem_links

# Function to extract poem data from individual poem page
def extract_poem_data(poem_url):
    poem_html_content = get_html_content(poem_url)
    if not poem_html_content:
        return None

    soup = BeautifulSoup(poem_html_content, 'html.parser')
    
    title_tag = soup.find('h2', class_='h3')
    poem_title = title_tag.text.strip() if title_tag else 'No title'
    
    poem_content_div = soup.find('div', id='poem_content')
    poem_lines = [line.text.strip() for line in poem_content_div.find_all('h3')] if poem_content_div else []
    
    # Combine every two lines into one, separated by a hyphen
    combined_lines = []
    for i in range(0, len(poem_lines), 2):
        if i + 1 < len(poem_lines):
            combined_lines.append(f"{poem_lines[i]} - {poem_lines[i+1]}")
        else:
            combined_lines.append(poem_lines[i])
    
    poem_content = '\n'.join(combined_lines)
    
    return {'title': poem_title, 'content': poem_content}

# Function to save a single poem to a text file
def save_poem_to_file(poem, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f"{poem['content']}")
        file.write('$' + '\n')

# Main function to scrape the data
def main():
    base_url = 'https://www.aldiwan.net'
    main_page_url_template = f'{base_url}/Type-%D8%B9%D9%85%D9%88%D8%AF%D9%8A%D9%87?page={{}}'
    
    for page_num in range(2779, 3642): 
        print(f"Processing page {page_num}...")
        main_page_url = main_page_url_template.format(page_num)
        html_content = get_html_content(main_page_url)
        
        if html_content:
            poem_links = extract_poem_links(html_content)
            
            # Process all poems on the current page
            for poem_link in poem_links:
                poem_url = f'{base_url}{poem_link}' if poem_link.startswith('/') else f'{base_url}/{poem_link}'
                poem_data = extract_poem_data(poem_url)
                
                if poem_data:
                    # Save each poem to a text file immediately
                    save_poem_to_file(poem_data, 'all_poems.txt')
        
        # To avoid overwhelming the server, let's add a delay between requests
        time.sleep(1)

if __name__ == "__main__":
    main()
