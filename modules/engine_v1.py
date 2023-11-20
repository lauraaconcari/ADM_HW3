import pandas as pd
import json
import nltk
from nltk.corpus import stopwords
import regex as re

# Setting the NLTK environment to work with English language
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
stops = set(stopwords.words('english'))
porterStemmer = nltk.PorterStemmer()

path_vocabulary = 'data/vocabulary.json'
path_vocabulary_inverted = 'data/vocabulary_inverted.json'
path_inverted_index = 'data/inverted_index.json'

df_original = pd.DataFrame()

def create_vocabulary(df: pd.DataFrame) -> dict:
    """
    This function creates a volcabulary from the description column of the dataset
    It creates a single list with all the words in the description column, then it
    sort them and remove duplicates. Finally it creates a dictionary with the words as keys
    and as value a progressive integer starting from 0
    Args:
        df (DataFrame): The all dataset
    Returns:
        dict: The vocabulary
    """
    vocabulary = {}
    vocabulary_inverted = {}
    
    global df_original
    df_original = df.copy()
    
    s = df_original['prep_description']    

    # Merging all the words
    lst_words = [word.lower() for lst in s.values for word in lst]
    # Eliminating duplicates
    lst_words = list(set(lst_words))
    # Sorting the list in alphabetical order
    lst_words.sort()

    for i, word in enumerate(lst_words):
        vocabulary[word] = i
        vocabulary_inverted[i] = word

    # Saving the vocabulary dictionary into a json file
    with open(path_vocabulary, "w") as f:
        json.dump(vocabulary, f)
    # Saving the vocabulary inverted dictionary into a json file
    with open(path_vocabulary_inverted, "w") as f:
        json.dump(vocabulary_inverted, f)

    return vocabulary


def get_vocabulary() -> dict:
    """
    This function loads the vocabulary from the vocabulary.json file
    If the vocabulary file doe not exists it returns None
    Returns:
        dict: The vocabulary
    """
    try:
        with open(path_vocabulary, "r") as f:
            vocabulary = json.load(f)
        return vocabulary
    except Exception as e:
        return None


def get_vocabulary_inverted() -> dict:
    """
    This function loads the vocabulary_inverted from the vocabulary_inverted .json file
    If the vocabulary file does not exists it returns None
    Returns:
        dict: The vocabulary
    """
    try:
        with open(path_vocabulary_inverted, "r") as f:
            vocabulary = json.load(f)
        return vocabulary
    except Exception as e:
        return None


def get_term_id(word: str) -> int:
    """
    This function returns the term_id of a given word
    Args:
        term (str): The word
    Returns:
        int: The term_id (None if in the vocabulary does not exists
            or the vocabulary does not esists)
    """
    vocabulary = get_vocabulary()
    if vocabulary is None:
        return None

    return vocabulary.get(word.lower(), None)


def get_word_from_id(term_id: int) -> str:
    """
    This function returns the term_id of a given word
    Args:
        term_id (ind): The id of the term
    Returns:
        str: The corresponding word
    """
    vocabulary_inverted = get_vocabulary_inverted()
    if vocabulary_inverted is None:
        return None

    return vocabulary_inverted.get(str(term_id), None)


def create_inverted_index() -> dict:
    """
    This function creates an inverted index from the description column of the dataset
    It creates a dictionary where the keys are the term_id and the values are the list of
    the indexes of the courses desccription that contains the term
    Returns:
        dict: The inverted index (None if the vocabulary does not exists)
    """
    vocabulary = get_vocabulary()
    if vocabulary is None:
        return None

    inverted_index = {}

    def invert_description(index, lst_words):
        """
        This function is used to invert the description of a single course
        and to append the result in the inverted_index dictionary
        Args:
            index (int): The index of the course description
            lst_words (list): The list of words in the course description
        Returns:
            None
        """
        
        # We need to access the inverted_index dictionary, so we need to declare it as nonlocal
        nonlocal inverted_index
        
        for word in lst_words:
            # Get the term_id of the word
            term_id = get_term_id(word)
            
            if term_id is not None:
                # If the term_id is not in the dictionary we add that key
                if term_id not in inverted_index:
                    inverted_index[term_id] = []
                # We append the index of the course to the list of the term_id
                inverted_index[term_id].append(index)

                # Finally removing duplicates
                inverted_index[term_id] = list(set(inverted_index[term_id]))
                
        return None

    global df_original
    df_original.apply(lambda row: invert_description(row.name, row['prep_description']), axis = 1)

    # Saving the inverted index dictionary into a json file
    with open(path_inverted_index, "w") as f:
        json.dump(inverted_index, f)

    return inverted_index


def get_inverted_index() -> dict:
    """
    This function loads the inverted index from the inverted_index.json file
    If the inverted index file doe not exists it returns None
    Returns:
        dict: The inverted index
    """
    try:
        with open(path_inverted_index, "r") as f:
            inverted_index = json.load(f)
            
        # Converting the keys from string to int, since we have to use them as integers
        inverted_index = {int(key): value for key, value in inverted_index.items()}
        return inverted_index
    except Exception as e:
        return None


def preprocess(text: str) -> list:
    """
    This function preprocess the text of the query. It applies the following operations:
    lowering the case, removing punctuation, tokenizing, removing stopwords, (Porter) stemming 
    Args:
        text (str): The text of the query
    Returns:
        list: The list of the words after the preprocessing
    """
    # We lower the case of all the words
    text = text.lower()

    # REMOVE PUNCTUATION using regex
    # # n particular we substitute all the punctuation with an empty string, avoiding to remove the dashes inside the words
    # The regex has tre filters: 
    # - the first eliminates everything that is not a letter, a number, a space or a dash
    # - the second and the third eliminate the dashes that are not between two letters
    # Some examples: eye- --> eye, -eye --> eye, eye-catching --> eye-catching

    text = re.sub(r"[^a-zA-Z0-9\s\-]|((?<=[a-zA-Z\W])\-(?=[^a-zA-Z]))|((?<=[^a-zA-Z])\-(?=[a-zA-Z\W]))", "", text)

    # TOKENIZATION using the word_tokenize() function of NLTK
    text = nltk.word_tokenize(text)

    # REMOVING STOPWORDS using the stopwords list of NLTK
    global stops
    text = [x for x in text if x not in stops]

    # STEMMING using the PorterStemmer of NLTK
    global porterStemmer
    text = [porterStemmer.stem(x) for x in text]

    return text

# First version of the search engine
def search(query: str) -> pd.DataFrame:
    """
    First version of the search engine
    This function returns the list of the documents that contains 
    all the list of words in the query with the AND logic
    Args:
        query (str): The query
    Returns:
        pd.DataFrame: The dataframe with the results
    """
    vocabulary = get_vocabulary()
    if vocabulary is None:
        return None
    
    inverted_index = get_inverted_index()
    if inverted_index is None:
        return None
    
    # Preprocessing the query
    words = preprocess(query)
    
    # We use a set because it's easy to apply the AND logic
    # because it correspond to the intersection of the sets
    document_ids = {}
    
    # We also use a boolean variable, because we do not need
    # to do any intersection operation if we are querying the first word
    # of the list
    is_first_word = True
    
    for word in words:
        # For each word in the query we get the term_id
        term_id = get_term_id(word.lower())
        if term_id is not None:
            # Then we get the list of the course indexes that contains the term_id
            tmp_ids = inverted_index.get(term_id, None)
            
            # If the tmp_ids is None it means that the word is not in the vocabulary
            # so we can pass to the next word
            
            if is_first_word and tmp_ids is not None:
                # If it's the first word we just add the list of the course indexes
                # to the set
                document_ids = set(tmp_ids)
                is_first_word = False
                
            elif not is_first_word and tmp_ids is not None:
                # If it's not the first word we do the intersection between the queries
                # results. If the intersection is empty then also the final result will be
                # empty, so we can stop the computation and return an empty list
                document_ids = document_ids.intersection(set(tmp_ids))
                
    # Returning the documents that match the query
    global df_original
    return df_original[df_original.index.isin(document_ids)]