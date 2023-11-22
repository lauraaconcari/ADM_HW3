# ADM_HW3 - Master's Degrees from all over!
Algorithmic Methods of Data Mining (Sc.M. in Data Science) Academic year 2023–2024. Homewok 3
---

## Team members
* Laura Concari 1890490
* Filippo Parlanti 2136988
* Laura Cesario 1852596
* Sohrab Seyyedi Parsa 2101087

## Contents
* __`main.ipynb`__: 
	> A Jupyter notebook which provides the solutions to all research questions.

    ### 1. Data collection

    In this response, we focus on implementing a data collection process to build a corpus of documents centered around master's degree programs. The approach involves breaking down the tasks into distinct modules, such as crawler.py for web scraping master's degree information, ```parser.py``` for extracting relevant details, and ```engine.py``` for orchestrating the entire process. 

    * **Get the list of master's degree courses**
    
        The initial phase entails navigating through master's degree courses, gathering detailed information, and subsequently retrieving the URLs associated with each course. Finally, the results are saved in a text file (.txt), with each line representing a unique URL, limited to the first 400 pages to yield 6000 unique URLs. Special attention is given to handling exceptions and creating code that is both readable and efficient.

    * **Crawl master's degree pages**

        In this section, the focus is on crawling the master's degree pages corresponding to the URLs obtained from the first 400 pages. The process involves:

        - Downloading the HTML content for each collected URL.
        - Immediately saving the HTML of each page in a file to prevent data loss in case the program stops for any reason.
        - Organizing the downloaded HTML pages into folders, with each folder containing the HTML of courses from a specific page in the master's program list.

    * **Parse downloaded pages** 

        At this stage, all HTML documents related to the master's degree programs have been acquired, and the next step is to extract specific information. The desired information for each course and their respective formats are:

            Course Name
            University 
            Faculty 
            Full or Part Time 
            Short Description 
            Start Date 
            Fees 
            Modality 
            Duration 
            City 
            Country 
            Presence or online modality 
            Link to the 

    ### 2. Search Engine
    * **Preprocessing the text**
        - Removing special characters and numbers
        - Removing stop words
        - Lemmatization
        - Stemming 
        - Any other necessary preprocessing steps

    * **Preprocessing the fees column** 

        This task involves converting the 'Fees' column into a numerical value that can be used in calculations and comparisons.

    * **Conjunctive query**

        Given a user-input query (e.g., "advanced knowledge"), the Search Engine performs a conjunctive query (AND operation). It returns a list of documents that contain all the words in the query. For each selected document, the output includes:

            courseName
            universityName
            description
            URL
    
    <a id="define-new-score"></a>
    ### 3. Define a new score!
    Build a novel scoring metric to rank MSc degrees based on user queries, considering multiple variables beyond the description field.
    
    ### 4. Visualizing the most relevant MSc degrees
    Create a map showcasing MSc degree courses based on the defined score in point 3. The map should provide insights into the location (city and country) of each course, along with a representation of associated fees.

    <a id="command-line-question"></a>
    ### 6. Command Line Question
    Answered the questions using **only** Linux command line tools and created a script named ```CommandLine.sh``` for execution.

    - Which country offers the most Master's Degrees? Which city?
    - How many colleges offer Part-Time education?
    - Print the percentage of courses in Engineering (the word "Engineer" is contained in the course's name).

    ### 7. Algorithmic Question 
    This algorithm tackles the problem of assisting Leonardo in determining if he can create a fictitious report of daily work hours that adheres to HR constraints. It takes input parameters such as the number of days worked (d), the total hours worked (sumHours), and the minimum and maximum hour constraints for each day. The algorithm sorts the constraints based on minimum hours and then distributes the remaining hours to meet the total required hours, ensuring compliance with both minimum and maximum constraints. If it's feasible to generate a report within the given constraints, the algorithm prints 'YES' followed by the daily hours; otherwise, it prints 'NO'. The algorithm provides a solution that respects HR limitations and contributes to the overall requested hours worked.


* __`CommandLine.sh`__: 
    > Script that performs several operations using Linux command line tools to concatenate all TSV files created in point 1 into a single file named ```merged_courses.tsv``` and to answer the proposed questions. 


* __`images`__: 
    > Folder with the output images for [Command Line Question](#command-line-question) and  [Define a New Score!](#define-new-score).

* __`modules`__: 
    > Folder with the following Python files: 
    * __`currency.py`__: contains a module that handles currency conversion. 
    * __`engine_v1.py`__: contains a module for implementing a search engine based on a dataset of master's degree courses. 
    * __`engine_v2.py`__: extends the search engine from the previous version (__`engine_v1.py`__). It introduces the concept of term frequency-inverse document frequency (tf-idf) for each word in the dataset, aiming to improve information retrieval. The script leverages the scikit-learn TfidfVectorizer to compute tf-idf scores for each term in the vocabulary across all documents.
    * __`engine_v3.py`__: extends the search engine from the previous version (__`engine_v1.py`__). It introduces a new scoring mechanism for each word in each document, combining term frequency (TF) and inverse document frequency (IDF). 

* __`merged_courses.tsv`__: 
    > tsv file with the merge of the all 60.000 courses, created in [Command Line Question](#command-line-question). 
