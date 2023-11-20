import pandas as pd
import numpy as np
import json
import heapq
from sklearn.feature_extraction.text import TfidfVectorizer

# Import the previous engine
from . import engine_v1

df_original = pd.DataFrame()

path_courses_matrix_tf_idf = "data/courses_matrix_tf_idf.csv"
path_inverted_index_tf_idf = 'data/inverted_index_tf_idf.json'
path_norms = 'data/norms.csv'


def compute_tf_idf() -> pd.DataFrame:
    """
    Computes the tf-idf for each word in the in each document (i.e. course),
    where tf-idf = tf * idf = term frequency * inverse document frequency.
    Return the correspondent dataframe
    Returns:
        tf_idf: The tf-idf dataframe
    """
    # First of all we get the vocabulary using the engine_v1 module
    vocabulary = engine_v1.get_vocabulary()
    if vocabulary is None:
        return None

    # Create a Scikit-learn TfidfVectorizer object
    tfidf_vec = TfidfVectorizer(input='content', lowercase = False, tokenizer = lambda text: text, vocabulary = vocabulary)
    
    # Load the dataset
    global df_original
    df = df_original
    
    # Transforming the 'prep_description' column into a tf-idf matrix
    # and converting it into a dataframe
    results = tfidf_vec.fit_transform(df['prep_description'])
    result_dense = results.todense()
    tf_idf = pd.DataFrame(result_dense.tolist(), index = df.index, columns=list(vocabulary.keys()).sort())
    
    # Save the tf-idf dataframe in the file courses_matrix_tf_idf.csv
    with open(path_courses_matrix_tf_idf, "w") as f:
        tf_idf.to_csv(f)
        
    # Here we compute the l2 norms for each document
    tf_idf['norm'] = np.linalg.norm(tf_idf.values, axis = 1)
         
    # We also save in the file norms.csv the norm of each document
    with open(path_norms, "w") as f:
        tf_idf['norm'].to_csv(f)
    
    return tf_idf


def get_tf_idf() -> pd.DataFrame:
    """
    This function loads the tf-idf dataframe from the courses_matrix_tf_idf.csv file
    Args:
        df (pd.DataFrame): The dataframe containing the columns 'index' and 'description'
    Returns:
        tf_idf: The tf-idf dataframe
    """
    try:
        with open(path_courses_matrix_tf_idf, "r") as f:
            tf_idf = pd.read_csv(f, index_col = 'index')
        return tf_idf
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
    Computes the inverted tf-idf index for each word in the vocabulary.
    Returns a dictionary of the format:
    {
      term_id_1:[(document1, tfIdf_{term,document1}), (document2, tfIdf_{term,document2}), (document4, tfIdf_{term,document4}), ...],
      term_id_2:[(document2, tfIdf_{term,document1}), (document6, tfIdf_{term,document6}), ...],
        ...
    }
    The dictionary is also saved in the file inverted_index_tf_idf.json for a faster access to it.
    Args:
        df (pd.DataFrame): The document dataframe
    Returns:
        dict: The inverted tf-idf index
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
    tf_idf = compute_tf_idf()

    # Then we compute the inverted index
    for word, term_id in vocabulary.items():
                
        # Retrive the list of tuples where tf_idf > 0
        # to_records() is a pandas function that returns a list of tuples from a dataframe
        # tuple_list = pd.DataFrame(tf_idf[tf_idf[word] > 0][word]).to_records(index = True).tolist()
        tuple_list = pd.DataFrame(tf_idf[tf_idf[term_id] > 0][term_id]).to_records(index = True).tolist()
        
        # We add the list of tuples to the inverted index dictionary
        inverted_index[term_id] = tuple_list    
        
    # Finally we save the inverted index dictionary in the file inverted_index_tf_idf.json
    with open(path_inverted_index_tf_idf, "w") as f:
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
        with open(path_inverted_index_tf_idf, "r") as f:
            inverted_index = json.load(f)
            
        # Converting the keys from string to int, since we have to use them as integers
        inverted_index = {int(key): value for key, value in inverted_index.items()}
        return inverted_index
    except Exception as e:
        return None


# Second version of the search engine
def search(query: str, k: int) -> list:
    """
    For each document we compute the cosine similarity with the query
    using the tf-idf score previously evaluated
    It returns a Heap with the k most similar documents and 
    the relative similarity score
    Args:  
        words (list): The list of words in the query
        k (int): The number of most similar documents to return
    Returns:
        list: The list of the k most similar documents and the relative similarity score
    """
    
    # Preprocess the query
    words = engine_v1.preprocess(query)
    
    # Read the inverted index from the file inverted_index_tf_idf.json
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
    query_words_ids = [engine_v1.get_term_id(word.lower()) for word in words]
    
    # From the term_id access the inverted_index and find the list of tuples (doc_id, tf_idf)
    # for each word in the query
    query_inverted_indexes = {int(word_id): inverted_index[int(word_id)] for word_id in query_words_ids}
    
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