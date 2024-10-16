from elasticsearch import Elasticsearch
from langchain_huggingface import HuggingFaceEmbeddings
from fewShotKeywordExtractor import FewShotKeywordExtractor

class VectorDatabaseSearcher:
    def __init__(self, model_name="bert-large-uncased", es_host="http://10.174.134.90:31475", schema_index="schema", metadata_index="metadata"):
        # Initialize the embeddings model
        self.embeddings_model = HuggingFaceEmbeddings(model_name=model_name)
        # Initialize Elasticsearch connection
        self.es = Elasticsearch(es_host)
        self.schema_index = schema_index
        self.metadata_index = metadata_index

    def get_embedding(self, text):
        """Convert the text (keyword list) into embeddings."""
        # print("my text ", text)
        return self.embeddings_model.embed_documents([text])[0]

    def search_schema(self, keyword_embedding):
        """Search the schema index using the keyword embedding to find the most matching column."""
        response = self.es.search(
            index=self.schema_index,
            body={
                "size": 1,  # Get top 1 match
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'column_name_embedding') + 1.0",
                            "params": {"query_vector": keyword_embedding}
                        }
                    }
                }
            }
        )
        
        if response['hits']['hits']:
            best_match = response['hits']['hits'][0]['_source']
            column_name = best_match['column_name']
            column_type = best_match['column_type']
            return column_name, column_type
        else:
            return None, None

    def search_metadata(self, keyword_embedding):
        """Search the metadata index using the keyword embedding to find the most matching column value."""
        response = self.es.search(
            index=self.metadata_index,
            body={
                "size": 1,  # Get top 1 match
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'column_name_embedding') + 1.0",
                            "params": {"query_vector": keyword_embedding}
                        }
                    }
                }
            }
        )
        
        if response['hits']['hits']:
            best_match = response['hits']['hits'][0]['_source']
            column_name = best_match['column_name']
            column_type = best_match['column_type']
            return column_name, column_type
        else:
            return None, None

    def merge_results(self, schema_result, metadata_result):
        """Merge the column name and column type results from the schema and metadata tables."""
        merged_columns = {
            "schema_column_name": schema_result[0],
            "schema_column_type": schema_result[1],
            "metadata_column_name": metadata_result[0],
            "metadata_column_type": metadata_result[1]
        }
        return merged_columns

    def search(self, keyword_list):
        """Perform the entire search process and return the merged results."""
        # Generate embeddings for the keyword list
        keyword_embedding = self.get_embedding(keyword_list)
       
        schema_result = self.search_schema(keyword_embedding)
       
        metadata_result = self.search_metadata(keyword_embedding)
        # print("metadata results are ",metadata_result)
        # Merge results
        final_result = self.merge_results(schema_result, metadata_result)
        return final_result


# Example Usage:
if __name__ == "__main__":
    natural_language_query = "Which movies released in 2016 have a rating above 5 and should be horror movies?"
    extractor = FewShotKeywordExtractor()
    keyword_list,sql_example  = extractor.convert_to_sql(natural_language_query)
    print(f"Extracted keyword list: {keyword_list}")
    
    keyword_list = ['horror', 'released in 2016', 'rating above 5']
    searcher = VectorDatabaseSearcher()

    # # keyword_list = "movies released in 2016 with a rating above 5"  # Example keyword list
    # column_list = []
    # for item in keyword_list:
    #     result = searcher.search(item)
    #     column_list.append(result)

    # print(f"Merged result: {column_list}")
    

    # Initialize an empty set to track unique results
    unique_results = set()
    column_list = []

    # Loop through each item in the keyword list
    for item in keyword_list:
        result = searcher.search(item)
        
        # Convert the result to a tuple so it can be added to the set
        result_tuple = (
            result["schema_column_name"],
            result["schema_column_type"],
            result["metadata_column_name"],
            result["metadata_column_type"]
        )
        
        # Check if the result is already in the set of unique results
        if result_tuple not in unique_results:
            # If it's not in the set, add it to the set and the list
            unique_results.add(result_tuple)
            column_list.append(result)
    # return column_list
    # Print the unique merged results
    print(f"Unique merged result: {column_list}")
