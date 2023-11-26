def download_html(url, folder_path):
    ''' This function takes a URL and a folder path as input arguments
    and saves its HTML content in the path provided.
    '''

    import os
    import requests
    from bs4 import BeautifulSoup

    # Using try-except block to handle possible errors
    try:
        # Retrieving the HTML content of the page using the get method
        response = requests.get(url)
        
        # Check for response status code (the most likely response we got here was: 429 Too Many Requests)
        if response.status_code == 429:
            print(f"Rate limited. Waiting for a while...")
            time.sleep(3)  # Wait for 3 seconds
            return download_html(url, folder_path)

        # Check for other possible errors
        response.raise_for_status()   # returns an HTTPError object if an error occurs
        
        # Extracting the page name from the URL to use as the filename
        
        # First approach: using string methods
        # file_name = url.split("/")[-2].replace('-',' ')
        # The problem with this approach is that there are courses with similar titles and only the first one will be saved.

        # Second approach: the entire URL as the page name after URL encoding using parse module from urllib library
        file_name = quote(url, safe='')   # setting safe parameter to an empty string to encode all characters 
        # This function represents special characters in the URL by replacing them with percent-encoded (%) values
        
        # Third approach: Replace the characters not allowed in Windows filenames
        # file_name = page_name.replace(":", "_").replace("/", "_").replace("?", "_").replace("&", "_")
        # At the end of the day there will be a link that fails this approach too! (After 1740 iterations!)
        
        # Fourth approach among many others W.R.T this course is using hashlib library which here returns a hexadecimal representation of a given URL
        # This approach makes sure to produce a valid and unique filename while avoiding potential issues regarding Windows filenames
        # file_name = hashlib.md5(url.encode('utf-8')).hexdigest()
        
        # Creating a file path W.R.T the path passed to function (parent folder)
        file_path = os.path.join(folder_path, f"{file_name}.html")
        
        # Saving the HTML with the file_name variable defined by 2nd (or 4th) approach
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)

        print(f"Downloaded: {url}")

    # For conventions, print any possible error raised which helps to debug more easily
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}. Error: {e}")