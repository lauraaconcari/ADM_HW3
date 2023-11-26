def extract_msc_page(msc_page_url):
    ''' This function takes a URL as input and extracts several
    contents from the corresponding HTML elements.
    '''

    import requests
    from bs4 import BeautifulSoup

    contents = {}   # Defining a dictionary to save the extracted contents (as dictionary values) with the corresponding tag (as dictionary key).

    # Opening the HTML file and parse it with BeautifulSoup
    with open(msc_page_url, "r", encoding="utf-8") as file:
        html_content = file.read()
        
    soup = BeautifulSoup(html_content, "html.parser")

    # Extracting course Name
    name_span = soup.find("h1", {'class': "text-white course-header__course-title"})
    contents['courseName'] = name_span.get_text(strip=True) if name_span else ''   # If the information is missing, return an empty string

    # Extracting course University & Faculty names
    ins_dept_span = soup.find("span", {'class': "course-header__inst-dept-name"})
    contents['universityName'] = ins_dept_span.a.get_text(strip=True) if ins_dept_span else ''   # If the information is missing, return an empty string
    contents['facultyName'] = ins_dept_span.find('a', {'class': 'course-header__department'}).get_text(strip=True) if ins_dept_span else ''   # If the information is missing, return an empty string

    # Extracting study type, Full or Part Time
    study_type_span = soup.find("span", {'class': "key-info__content key-info__study-type py-2 pr-md-3 text-nowrap d-block d-md-inline-block"})
    contents['isItFullTime'] = study_type_span.find("a").get_text(strip=True) if study_type_span else ''   # If the information is missing, return an empty string

    # Extracting course Short Description
    contents['description'] = soup.find("div", id="Snippet").get_text(strip=True) if soup.find("div", id="Snippet") else ''   # If the information is missing, return an empty string

    # Extracting course Start Date
    start_span = soup.find("span", {'class': "key-info__content key-info__start-date py-2 pr-md-3 text-nowrap d-block d-md-inline-block"})
    contents['startDate'] = start_span.get_text(strip=True) if start_span else ''   # If the information is missing, return an empty string

    # Extracting course Fees
    fee_span = soup.find("div", {'class': 'course-sections course-sections__fees tight col-xs-24'})
    contents['fees'] = fee_span.find('p').get_text(strip=True) if fee_span else ''   # If the information is missing, return an empty string

    # Extracting course Modality
    modality_span = soup.find("span", {'class': "key-info__content key-info__qualification py-2 pr-md-3 text-nowrap d-block d-md-inline-block"})
    contents['modality'] = modality_span.find("a").get_text(strip=True) if modality_span else ''   # If the information is missing, return an empty string

    # Extracting course Duration
    duration_span = soup.find("span", {'class': "key-info__content key-info__duration py-2 pr-md-3 d-block d-md-inline-block"})
    contents['duration'] = duration_span.get_text(strip=True) if duration_span else ''   # If the information is missing, return an empty string

    # Extracting City where the course is held
    city_span = soup.find("a", {'class': "card-badge text-wrap text-left badge badge-gray-200 p-2 m-1 font-weight-light course-data course-data__city"})
    contents['city'] = city_span.get_text(strip=True) if city_span else ''   # If the information is missing, return an empty string

    # Extracting Country where the course is held
    country_span = soup.find("a", {'class': "card-badge text-wrap text-left badge badge-gray-200 p-2 m-1 font-weight-light course-data course-data__country"})
    contents['country'] = country_span.get_text(strip=True) if country_span else ''   # If the information is missing, return an empty string

    # Extracting course Presence or online modality
    admin_span = soup.find("a", {'class': "card-badge text-wrap text-left badge badge-gray-200 p-2 m-1 font-weight-light course-data course-data__on-campus"})
    contents['administration'] = admin_span.get_text(strip=True) if admin_span else ''   # If the information is missing, return an empty string

    # Extracting Link to the course page
    contents['url'] = soup.find('link', rel='canonical')['href']
    
    return contents
