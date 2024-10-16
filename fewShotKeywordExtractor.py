import ollama
from langchain_ollama import ChatOllama
import re
import pandas as pd
import json
from langchain_huggingface import HuggingFaceEmbeddings
from elasticsearch import Elasticsearch
model_name="bert-large-uncased"
embeddings_model1 = HuggingFaceEmbeddings(model_name=model_name)




class FewShotKeywordExtractor:
    def __init__(self, model_name="bert-large-uncased", llm_model="llama3", es_host="http://10.174.134.90:31475", index_name="fewshot"):
        # Initialize the embeddings model
        
        self.embeddings_model = embeddings_model1
        
        
            

        # Initialize the LLM model
        self.llm = ChatOllama(
            model=llm_model,
            temperature=0,
        )
        # Initialize Elasticsearch connection
        self.es = Elasticsearch(es_host)
        self.index_name = index_name
        

    def get_nlq_embedding(self, NLQ):
        """Convert the NLQ into embeddings using HuggingFace model."""
        return self.embeddings_model.embed_documents([NLQ])[0]

    def search_few_shot_examples(self, NLQ_embedding):
        """Search for top 5 similar few-shot examples in Elasticsearch based on NLQ embedding."""
        response = self.es.search(
            index=self.index_name,  
            body={
                "size": 5,  # Get top 5 matches
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'NLQ_embedding') + 1.0",
                            "params": {"query_vector": NLQ_embedding}
                        }
                    }
                }
            }
        )

        few_shot_examples = []
        for hit in response['hits']['hits']:
            example = {
                "NLQ": hit['_source']['NLQ'],
                "keyword_list": hit['_source']['keyword'],
                "sql_query": hit['_source']['sql_query']
            }
            few_shot_examples.append(example)

        return few_shot_examples
    


    def convert_to_sql(self, NLQ):
        """Convert the NLQ to a SQL query using few-shot examples and LLM."""
        # Get NLQ embedding
        
        NLQ_embedding = self.get_nlq_embedding(NLQ)
        # Get the top 5 few-shot examples from Elasticsearch
        few_shot_examples = self.search_few_shot_examples(NLQ_embedding)

        # Format the few-shot examples into the prompt template
        few_shot_str = ""
        for example in few_shot_examples:
            few_shot_str += f'["NLQ": "{example["NLQ"]}", "keyword_list": {example["keyword_list"]}],\n'
        few_shot_str_with_sql = ""
        for example in few_shot_examples:
            few_shot_str_with_sql += f'["NLQ": "{example["NLQ"]}", "keyword_list": {example["keyword_list"]},"sql_query":"{example["sql_query"]}"],\n'
        # Build the prompt template with dynamic few-shot examples
        prompt_template = f"""
        [Extract Corrected Query and necessary keywords from the following natural language query:
        1. First, correct the query by fixing grammatical mistakes and beautifying/simplifying the text.
        2. Use the corrected query to generate the keyword_list.
        3. While generating, strictly do not add any pronoun, verb, or conjunction in the keyword_list.]
        NLQ:
        "{NLQ}"
        4. Extract correct word from NLQ like get the technical key as keyword_list
        Please return keyword_list.
        Keyword List:[]
        do not add anything by yourself
        """

        # Invoke the LLM with the dynamically generated prompt
        response = self.llm.invoke(prompt_template)
        res1 = response.content
        print("res1 is ", res1)
        # Extract keyword list using regex
        # keyword_list_match = re.search(r"\*\*Keyword List:\*\*\n(\[.*\])", res1)
        # if keyword_list_match:
        #     keyword_list = keyword_list_match.group(1)
        # else:
        #     keyword_list = None

        # Use regex to extract the keyword list from res1
        keyword_list_match = re.search(r"Keyword List.*:\s*(\[[^\]]*\])", res1)

        # Check if a match was found and extract the keyword list
        if keyword_list_match:
            # Evaluate the extracted string into a Python list
            keyword_list = eval(keyword_list_match.group(1))
        else:
            keyword_list = None
        return keyword_list,few_shot_str_with_sql

    def sqlgenerator(self,NLQ,column_list):
        # prompt = f"""
        #     You are a helpful assistant that converts natural language queries into SQL queries.
            
            
        #     Table: IMDB_Movie_Data
        #     Columns: {column_list}


        #     Given the following query in natural language, provide the corresponding SQL query:

        #     Natural Language Query: "{NLQ}"
        #     SQL Query:
        #     do not add anything by yourself .
        #     just give me sql query and no other content
        # """

        prompt = f"""
            You are an AI assistant specialized in converting natural language queries into precise SQL queries.

            The following information is provided:
            - **Table Name**: IMDB_Movie_Data
            - **Available Columns**: {column_list}

            Your task is to translate the provided natural language query into a valid SQL query that matches the described requirements.
            
            Please ensure:
            - Use only the provided table name: `IMDB_Movie_Data`.
            - Use only the columns listed in `Available Columns`.
            - The SQL query should be syntactically correct and must accurately reflect the user's request.

            Natural Language Query: "{NLQ}"

            SQL Query:
            do not add anything by yourself .
            just give me sql query and no other content
        """

        sql_query = self.llm.invoke(prompt)
        return sql_query
# Example Usage:
if __name__ == "__main__":
    natural_language_query = "Which movies released in 2016 have a rating above 5 and should be horror movies?"
    extractor = FewShotKeywordExtractor()
    keyword_list,example = extractor.convert_to_sql(natural_language_query)
    print(f"Extracted keyword list: {keyword_list}")
    print(f"Extracted example list: {example}")