# Function to collect the master URLs
def scrape_urls(base_url, num_pages):
    ''' This function takes a URL (string) and a number as arguments.
    It scrapes the consecutive pages (defined by the num_pages arg.)
    of the base_url and retrieves specific HTML elements (containing the course link)
    of each page before finally returning them as a list.
    '''
    
    import requests
    from bs4 import BeautifulSoup
    
    courses_url = []   # Create a list to save the extracted page URLs
    index = 1   # 
    
    # Handling the page number incrementation within a for loop 
    for page_num in range(1, num_pages + 1):
        if page_num == 1:   # The first page doesn't end in '/?PG={page_num}', so we handle it with an if statement.
            url = f"{base_url}/"
        else:
            url = f"{base_url}/?PG={page_num}"   # Using f-string to capture addresses of the first 400 pages

        # Sending a GET request to the URL passed to the function
        response = requests.get(url)

        # Checking whether the HTTP response is successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')   # Parse the URL to make it ready for data extraction

            # After messing around with the HTML structure of the website, pass the proper HTML tag (which contains course links) to find_all method 
            course_elements = soup.find_all('a', {'class': 'courseLink'})

            # Iterate over the page elements grabbed in the previous step
            for course_element in course_elements:
                
                # Extract the course URL from the 'href' attribute of each element
                course_url = 'https://www.findamasters.com' + course_element['href']
                print(course_url)
                courses_url.append(course_url)   # Save the URL in the courses_url list
                
                # Calculating the subfolder index
                subfolder_index = (index - 1) // links_per_folder + 1
    
                # Calling create_folders function. Please refer to the function docstring for further details.
                folder_path = create_folders(parent_folder, subfolder_prefix, subfolder_index)
    
                # Calling download_html function. Please refer to the function docstring for further details.
                download_html(course_url, folder_path)

                index = index + 1

            print(f"Scraped page {page_num}")   # Print the page scraped

            time.sleep(3)  # Adding a 3-second delay (by trial & error) between requests so that IP is not blocked

        # If the server's response was not successful (2xx), then return the response with a fail to fetch message along with the corresponding page URL
        else:
            print(f"Failed to fetch page {page_num}. Status code: {response.status_code}")

    return courses_url