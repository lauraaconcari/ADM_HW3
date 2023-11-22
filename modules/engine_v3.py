import pandas as pd
import numpy as np
import json
import heapq
from sklearn.feature_extraction.text import TfidfVectorizer

# Import the previous engine
from . import engine_v1

df_original = pd.DataFrame()

path_courses_matrix_new_score = "data/courses_matrix_new_score.csv"
path_inverted_index_new_score = 'data/inverted_index_new_score.json'
path_norms = 'data/norms.csv'


def compute_score() -> pd.DataFrame:
    """
    Computes the score for each word in the in each document (i.e. course),
    with the formula 
        Score = TF_{courseName} + (1 + log(TF_{description})) * IDF_{description}
    Return the correspondent dataframe
    Returns:
        new_score: The score dataframe
    """
    # First of all we get the vocabulary using the engine_v1 module
    vocabulary = engine_v1.get_vocabulary()
    if vocabulary is None:
        return None
    
    # Load the dataset
    global df_original
    df = df_original
    
    # Create a Scikit-learn TfidfVectorizer object
    # With the Sublinear option we apply the formula 1 + log(tf) instead of tf
    # In this way we penalise the words that appear a lot of times in a document
    tfidf_vec = TfidfVectorizer(input='content', lowercase = False, tokenizer = lambda text: text, vocabulary = vocabulary, sublinear_tf = True)
    
    # Transforming the 'prep_description' column into a log-tf-idf matrix
    # and converting it into a dataframe
    results = tfidf_vec.fit_transform(df['prep_description'])
    result_dense = results.todense()
    tf_idf = pd.DataFrame(result_dense.tolist(), index = df.index, columns=list(vocabulary.keys()).sort())
    
    # Then compute the tf of the 'courseName' column
    tfidf_vec2 = TfidfVectorizer(input='content', lowercase = False, tokenizer = lambda text: text, vocabulary = vocabulary, use_idf = False)
    results2 = tfidf_vec2.fit_transform(df['courseName'].apply(engine_v1.preprocess))
    result_dense2 = results2.todense()
    tf_idf2 = pd.DataFrame(result_dense2.tolist(), index = df.index, columns=list(vocabulary.keys()).sort())
        
    # Sum the score of the 'courseName' and the score of the 'description'
    new_score = tf_idf + tf_idf2    
    
        
    # Save the score dataframe in the file courses_matrix_new_score.csv
    with open(path_courses_matrix_new_score, "w") as f:
        new_score.to_csv(f)
        
    # Here we compute the l2 norms for each document
    new_score['norm'] = np.linalg.norm(new_score.values, axis = 1)
         
    # We also save in the file norms.csv the norm of each document
    with open(path_norms, "w") as f:
        new_score['norm'].to_csv(f)
    
    return new_score


def get_score() -> pd.DataFrame:
    """
    This function loads the score dataframe from the courses_matrix_new_score.csv file
    Args:
        df (pd.DataFrame): The dataframe containing the columns 'index' and 'description'
    Returns:
        df_score: The score dataframe
    """
    try:
        with open(path_courses_matrix_new_score, "r") as f:
            df_score = pd.read_csv(f, index_col = 'index')
        return df_score
    except Exception as e:
        print("Tf-Idf index has not been computed yet")
        return None


def get_norms() -> pd.DataFrame:
    """
    This function loads the norms dataframe from the norms.csv file
    Returns:
        norms: The norms dataframe
    """
    try:
        with open(path_norms, "r") as f:
            norms = pd.read_csv(f, index_col = 'index')
        return norms
    except Exception as e:
        print("Norms have not been computed yet")
        return None


def create_inverted_index(df: pd.DataFrame) -> dict:
    """
    Computes the inverted score index for each word in the vocabulary.
    Returns a dictionary of the format:
    {
      term_id_1:[(document1, score_{term,document1}), (document2, score_{term,document2}), (document4, score_{term,document4}), ...],
      term_id_2:[(document2, score_{term,document1}), (document6, score_{term,document6}), ...],
        ...
    }
    The dictionary is also saved in the file inverted_index_new_score.json for a faster access to it.
    Args:
        df (pd.DataFrame): The document dataframe
    Returns:
        dict: The inverted score index
    """
    
    # Saving the original dataframe
    global df_original
    df_original = df.copy()

    inverted_index = {}
    
    # Since we use the engine_v1 module we must start the Search Engine (v1)
    vocabulary = engine_v1.create_vocabulary(df)
    
    # Import the vocabulary
    vocabulary = engine_v1.get_vocabulary()
    if vocabulary is None:
        return None
    
    # First of all get the tf-idf index score 
    df_score = compute_score()

    # Then we compute the inverted index
    for word, term_id in vocabulary.items():
                
        # Retrive the list of tuples where tf_idf > 0
        # to_records() is a pandas function that returns a list of tuples from a dataframe
        # tuple_list = pd.DataFrame(tf_idf[tf_idf[word] > 0][word]).to_records(index = True).tolist()
        tuple_list = pd.DataFrame(df_score[df_score[term_id] > 0][term_id]).to_records(index = True).tolist()
        
        # We add the list of tuples to the inverted index dictionary
        inverted_index[term_id] = tuple_list    
        
    # Finally we save the inverted index dictionary in the file inverted_index_new_score.json
    with open(path_inverted_index_new_score, "w") as f:
        json.dump(inverted_index, f)
        
    return inverted_index


def get_inverted_index() -> dict:
    """
    This function loads the inverted index from the inverted_index_new_score.json file
    If the inverted index file does not exists it returns None
    Returns:
        dict: The inverted index
    """
    try:
        with open(path_inverted_index_new_score, "r") as f:
            inverted_index = json.load(f)
            
        # Converting the keys from string to int, since we have to use them as integers
        inverted_index = {int(key): value for key, value in inverted_index.items()}
        return inverted_index
    except Exception as e:
        return None


# Second version of the search engine
def search(query: str, k: int = 10) -> list:
    """
    For each document we compute the cosine similarity with the query
    using the score 
        TF_{courseName} + (1 + log(TF_{description})) * IDF_{description}
    previously evaluated. It returns a Heap with the k most similar documents and 
    the relative similarity score
    Args:  
        words (list): The list of words in the query
        k (int): The number of most similar documents to return
    Returns:
        list: The list of the k most similar documents and the relative similarity score
    """
    
    # Preprocess the query
    words = engine_v1.preprocess(query)
    
    # Get only the documents that contain all the words in the query
    # recycling the code from the search function of the engine_v1 module
    df_result = engine_v1.search(query)
    
    # Read the inverted index from the file inverted_index_new_score.json
    inverted_index = get_inverted_index() 
    if inverted_index is None:
        print("Inverted index has not been computed yet")
        return None
    
    # Read the l2 norms of the cdocuments from the file norms.csv
    norms = get_norms()
    if norms is None:
        print("Norms have not been computed yet")
        return None
    
    global df_original
    
    # Find the term_id for every word in the query
    query_words_ids = [(engine_v1.get_term_id(word.lower()), word) for word in words if engine_v1.get_term_id(word.lower()) is not None]
    
    # Update the preprocessed query to drop the None values i.e. words not in the vocabulary
    words = [tupl[1] for tupl in query_words_ids]
    # Converting the list of tuples to a list of only the tmer_id integers
    query_words_ids = [tupl[0] for tupl in query_words_ids]
    
    # From the term_id access the inverted_index and find the list of tuples (doc_id, score)
    # for each word in the query      
    # We only consider the documents that are in the df_result dataframe, which means that
    # they contain all the words in the query
    query_inverted_indexes = {int(word_id): inverted_index[int(word_id)] for word_id in query_words_ids}
    tmp_dict = {}
    for key, value_list in query_inverted_indexes.items():
        tmp_lst = [item for item in value_list if item[0] in df_result.index]
        tmp_dict[key] = tmp_lst
    query_inverted_indexes = tmp_dict
    
    # If none of the words in the query are in the vocabulary return None
    # otherwise at least one word is in the vocabulary
    if len(query_inverted_indexes) == 0:
        return None
    
    # Now we create a dataframe containing only the documents with id in the query_inverted_indexes list
    # and the columns are the words in the query
    df_tmp = pd.DataFrame(0, columns = [engine_v1.get_word_from_id(word_id) for word_id in query_words_ids], index = [lst[0] for lst in query_inverted_indexes[query_words_ids[0]]])
    for word_id, lst_tuple in query_inverted_indexes.items():
        for lst in lst_tuple:
            df_tmp.loc[lst[0], engine_v1.get_word_from_id(word_id)] = lst[1]    
    # Fill nan's with 0
    df_tmp.fillna(0, inplace = True)
    
    # Evaluate the query tf-idf score 'manually' without using the function tfidf_vectorizer.transform() of sklearn
    doc_frequencies = [(df_tmp[engine_v1.get_word_from_id(word_id)] != 0).sum() for word_id in query_words_ids]
    N = df_original.shape[0]
    # The 1s are added to avoid division by 0
    query_tf_idf = [1+np.log((N+1) / (1+doc_freq)) for doc_freq in doc_frequencies]
    query_norm = np.linalg.norm(query_tf_idf)
            
    # Retrive the norm of each document from the norms.csv file
    df_tmp['norm'] = norms.loc[df_tmp.index]
        
    # Evaluate the cosine similarity between the query and each document
    # and save it in the column 'Similarity'
    df_tmp['Similarity'] = df_tmp.apply(lambda row: np.dot(row[words], query_tf_idf) / (row['norm'] * query_norm), axis = 1)
        
    # Retriving the the k most similar documents from the original dataframe
    # and sorting them using the nlargest() function of the pandas library
    df_results = df_original.copy()
    df_results['Similarity'] = df_tmp['Similarity']
    df_results['Similarity'].fillna(0, inplace = True)
    df_results = df_results[df_results['Similarity'] > 0]
    df_results = df_results.nlargest(k, 'Similarity')
        
    # Finally we create a heap structure to store the k most similary documents
    # to the query and we return its
    heap = []
    for id, row in df_results.iterrows():
        # Adding the element to the heap
        # Since we have a min heap we need to add the negative similarity score
        # to get the max heap
        heapq.heappush(heap, (-float(row['Similarity']), [id] + row.values.tolist()))
    
    return heap