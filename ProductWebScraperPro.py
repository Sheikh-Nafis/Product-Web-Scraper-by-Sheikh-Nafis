from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing HTML content
import requests  # Import requests for making HTTP requests
import pandas as pd  # Import pandas for data manipulation and storage
import time  # Import time for adding delays between requests

# Base URL of the website's category without the page number
base_url = 'https://www.example.com/category/'

# Headers to mimic a browser request to avoid being blocked by the server
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Lists to store extracted product details
product_names = []  # To store product names
original_prices = []  # To store original prices (before discount)
current_prices = []  # To store current prices (after discount or final price)
product_links = []  # To store product URLs
product_images = []  # To store URLs of product images

# Start with the first page
page_number = 1

# Infinite loop to go through each page until no more pages are found
while True:
    # Construct the URL for the current page
    if page_number == 1:
        url = base_url  # Use base URL for the first page
    else:
        url = f'{base_url}page/{page_number}/'  # Append page number for subsequent pages

    # Fetch the HTML content of the current page
    try:
        response = requests.get(url, headers=headers)  # Make an HTTP GET request
        # Check if the server returned a 404 (page not found) error
        if response.status_code == 404:
            print(f"Page {page_number} does not exist. Stopping scraping.")
            break  # Stop the loop if a 404 error is encountered

        response.raise_for_status()  # Raise an error if the request failed
        
    except requests.exceptions.HTTPError as e: # Catch and handle HTTP errors (status codes 4xx and 5xx)
        print(f"HTTP error occurred on page {page_number}: {e}")
        break  # Stop the loop on HTTP errors
    except Exception as e: # Catch and handle HTTP errors (status codes 4xx and 5xx)
        print(f"An error occurred on page {page_number}: {e}")
        break  # Stop the loop on any other errors

    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'lxml')

    # Find the main container that holds all the products
    product_container = soup.find('div', class_="products wd-products wd-grid-g grid-columns-5")
    if not product_container:
        print(f"No product container found on page {page_number}. Assuming no more products.")
        break  # Stop the loop if no product container is found

    # Find all individual product elements within the container
    products = product_container.find_all('div', class_='product')
    if not products:
        print(f"No products found on page {page_number}. Stopping scraping.")
        break  # Stop the loop if no products are found

    print(f"Found {len(products)} products on page {page_number}")

    # Extract details for each product
    for product in products:
        # Extract product title (name)
        product_title = product.find('h3', class_="wd-entities-title").text.strip()
        
        # Find the price container that holds pricing information
        price_container = product.find('span', class_='price')
        original_price = None  # Initialize original price
        current_price = None  # Initialize current price
        
        # Extract original and current prices
        original_price_tag = price_container.find('del')  # Find the <del> tag for original price
        if original_price_tag:
            # Get original price if available
            original_price = original_price_tag.find('span', class_='woocommerce-Price-amount amount').text.strip()
        
        current_price_tag = price_container.find('ins')  # Find the <ins> tag for current price
        if current_price_tag:
            # Get current price if available
            current_price = current_price_tag.find('span', class_='woocommerce-Price-amount amount').text.strip()
        else:
            # If there's no <ins> tag, use the first available price as the current price
            current_price = price_container.find('span', class_='woocommerce-Price-amount amount').text.strip()
        
        # Extract product webpage link
        webpage_link = product.find('h3', class_="wd-entities-title").a['href']
        # Extract product image link
        image_tag = product.div.a.img
        image_link = image_tag.get('data-lazy-src') or image_tag.get('src')

        # Append extracted details to corresponding lists
        product_names.append(product_title)
        original_prices.append(original_price)
        current_prices.append(current_price)
        product_links.append(webpage_link)
        product_images.append(image_link)

    # Delay between requests to avoid overloading the server and potentially getting blocked
    time.sleep(5)  # Adjust the delay as needed

    # Increment the page number to go to the next page
    page_number += 1

# Create a DataFrame from the lists to organize the data
df = pd.DataFrame({
    'Product Name': product_names,
    'Original Price': original_prices,
    'Current Price': current_prices,
    'Product Link': product_links,
    'Product Image': product_images
})

# Write the DataFrame to an Excel file for later use
df.to_excel('saved/products.xlsx', index=False)

print('All product data saved to products.xlsx')