import pandas as pd
import pymysql
from flask import Flask, request, jsonify
from columnNameExtractor import VectorDatabaseSearcher
from fewShotKeywordExtractor import FewShotKeywordExtractor
from config import MARIADB_HOST, MARIADB_PORT, MARIA_USER, MARIA_DB, MARIA_PASS, MARIA_DB

app = Flask(__name__)

# Status endpoint to check if the server is up
@app.route("/status", methods=["GET","POST"])
def get_status():
    return jsonify({"status": "Server is up and running"})

@app.route("/search", methods=["POST","GET"])
def search_natural_language_query():
    # Get the natural language query from the request body
    data = request.get_json()
    natural_language_query = data.get("natural_language_query")
    
    if not natural_language_query:
        return jsonify({"error": "natural_language_query is required"}), 400

    # Extract keywords from the natural language query
    extractor = FewShotKeywordExtractor()
    print("ok1")
    
    # # return natural_language_query
    # keyword_list, _ = extractor.convert_to_sql(natural_language_query)
    # # return keyword_list
    # print("my keyword list ",keyword_list)



    import spacy

    # Load a pre-trained English model
    nlp = spacy.load('en_core_web_sm')

    def extract_meaningful_words(text):
        doc = nlp(text)
        # Extract nouns, proper nouns, and named entities
        keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
        # Add named entities for more context
        keywords.extend([ent.text for ent in doc.ents])
        return list(set(keywords))
        # return natural_language_query
        keyword_list, _ = extractor.convert_to_sql(natural_language_query)
        # return keyword_list
        print("my keyword list ",keyword_list)

    keyword_list = extract_meaningful_words(query)



    # Initialize the searcher
    searcher = VectorDatabaseSearcher()

    # Set to track unique results
    unique_results = set()
    column_list = []

    # Search for each keyword
    # for item in keyword_list:
    #     result = searcher.search(item)
    #     print("result are ",result)
    #     # result_tuple = (
    #     #     result["schema_column_name"],
    #     #     result["schema_column_type"],
    #     #     result["metadata_column_name"],
    #     #     result["metadata_column_type"]
    #     # )
    #     # if result_tuple not in unique_results:
    #     #     unique_results.add(result_tuple)
    #     #     column_list.append(result)
    # print("column list ",column_list)





    # Initialize a set to track unique column pairs
    unique_columns1 = set()
    unique_columns2 = set()
    column_list = []

    # Iterate through the results obtained from the searcher
    for item in keyword_list:
        result = searcher.search(item)
        print("result are ", result)
        
        # Create a tuple of schema and metadata column names to check for uniqueness
        column_pair1 = (
            result["schema_column_name"] 
        )

        column_pair2 = (
            result["metadata_column_name"]
        )
        
        
        if column_pair1 not in unique_columns1:
            
            unique_columns1.add(column_pair1)
            
            column_list.append(result)
        
        if column_pair2 not in unique_columns2:
            
            unique_columns2.add(column_pair2)
            
            column_list.append(result)

    unique_columns = set()

    # Iterate through each result
    for result in column_list:
        # Extract schema and metadata column details
        schema_pair = (result['schema_column_name'], result['schema_column_type'])
        metadata_pair = (result['metadata_column_name'], result['metadata_column_type'])
        
        # Add these pairs to the set to ensure uniqueness
        unique_columns.add(schema_pair)
        unique_columns.add(metadata_pair)

    # Print the unique column pairs
    print("Unique column pairs:", unique_columns)

    
    sql_query = extractor.sqlgenerator(natural_language_query,unique_columns)
    # print("sql_query ",sql_query.content)
    cleaned_sql_query = sql_query.content.replace("\n", "").strip()
    print("cleaned sql query ",cleaned_sql_query)
    return jsonify({"column_list": cleaned_sql_query})


# Define the database connection parameters
db_config = {
    "host": MARIADB_HOST,
    "user": MARIA_USER,
    "password": MARIA_PASS,
    "database": MARIA_DB,
    "port": MARIADB_PORT 
}

# Define a route for querying the database
@app.route('/query', methods=['POST'])
def query_database():
    try:
        # Get the SQL query from the request JSON payload
        payload = request.get_json()
        query = payload.get('query')

        if not query:
            return jsonify({"error": "No query provided"}), 400

        # Establish the connection
        connection = pymysql.connect(**db_config)
        print("ok1")
        # Execute the query and load the results into a Pandas DataFrame
        df = pd.read_sql(query, connection)

        # Close the connection
        connection.close()

        # Convert DataFrame to JSON and return as API response
        # return jsonify(df.to_dict(orient="records"))
        return jsonify(df.to_dict())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
