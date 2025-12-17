import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def find_strings_matching_keyword(
    keyword: str, 
    list_str: list[str],
    transformer_model_name: str = 'all-MiniLM-L6-v2',
    similarity_threshold: float = 0.6
    ) -> list[str]:

    # Initialize the model
    model = SentenceTransformer(transformer_model_name)

    # Define target keyword embedding
    target_embedding = model.encode([keyword])
    # Get embeddings for the list of strings
    list_embeddings = model.encode(list_str)    
    # Compute cosine similarities
    similarities = cosine_similarity(list_embeddings, target_embedding)
    # Define a dataframe to hold results with similarities and strings
    df_results = pd.DataFrame({
        'string': list_str,
        'similarity': similarities.flatten()
    }).sort_values(by='similarity', ascending=False).reset_index(drop=True)

    # Filter results based on similarity threshold
    df_filtered = df_results[df_results['similarity'] >= similarity_threshold]

    return df_filtered

# Find table names matching a keyword or their column names matching the same keyword
def find_table_column_name_matches( 
    df_table: pd.DataFrame,
    keyword: str,
    table_name_column: str = 'table_name',
    column_name_column: str = 'column_name',        
    table_name_similarity_threshold: float = 0.6,
    column_name_similarity_threshold: float = 0.6
    ) -> pd.DataFrame:

    # Ensure input dataframe has required columns
    if table_name_column not in df_table.columns:
        raise ValueError(f"DataFrame must contain column: {table_name_column}") 
    if column_name_column not in df_table.columns:
        raise ValueError(f"DataFrame must contain column: {column_name_column}")
    
    # Ensure table_name_column and column_name_column are of string type
    df_table[table_name_column] = df_table[table_name_column].astype(str)   
    df_table[column_name_column] = df_table[column_name_column].astype(str)

    # Ensure 'table_name_similarity' and 'column_name_similarity' do not already exist in df_table
    if 'table_name_similarity' in df_table.columns or 'column_name_similarity' in df_table.columns:
        raise ValueError("DataFrame must not already contain 'table_name_similarity' or 'column_name_similarity' columns")

    # Get unique table names
    list_table_names = df_table[table_name_column].unique().tolist()
    # Find table names matching the keyword
    df_table_name_matches = find_strings_matching_keyword(
        keyword=keyword,
        list_str=list_table_names,
        similarity_threshold=0.0
    )

    # Get unique column names
    list_column_names = df_table[column_name_column].unique().tolist()
    # Find column names matching the keyword
    df_column_name_matches = find_strings_matching_keyword(     
        keyword=keyword,
        list_str=list_column_names,
        similarity_threshold=0.0
    )

    # Join df_table_name_matches and df_column_name_matches on table names and column names
    # to get the table_name_similarity and column_name_similarity
    df_table = df_table.merge(
        df_table_name_matches,  
        left_on=table_name_column,
        right_on='string',  
        suffixes=('', '_table_name')
    ).rename(columns={'similarity': 'table_name_similarity'}).drop(columns=['string'])  

    df_table = df_table.merge(
        df_column_name_matches,     
        left_on=column_name_column,
        right_on='string',  
        suffixes=('', '_column_name')
    ).rename(columns={'similarity': 'column_name_similarity'}).drop(columns=['string'])

    # Filter based on similarity thresholds
    df_table_filtered = df_table[
        (df_table['table_name_similarity'] >= table_name_similarity_threshold) |
        (df_table['column_name_similarity'] >= column_name_similarity_threshold)
    ]
    df_table_filtered2 = df_table_filtered.loc[df_table_filtered.groupby(table_name_column)["column_name_similarity"].idxmax()]\
        .sort_values(by=['table_name_similarity','column_name_similarity'], ascending=False).reset_index(drop=True)

    return df_table_filtered2