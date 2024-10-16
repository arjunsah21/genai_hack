import requests
import pandas as pd
from config import QUERY_API_URL, SQL_QUERY_API

def send_sql_query_to_api(sql_query):
    api_url = QUERY_API_URL  
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": sql_query
    }
    
    try:
        # Send the POST request with the SQL query as payload
        response = requests.post(api_url, json=payload, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()  # Return the result from the API
        else:
            return {"error": f"Failed to execute query. Status code: {response.status_code}"}
    
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def get_sql_query(prompt):
    api_url = SQL_QUERY_API  
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "natural_language_query": prompt
    }
    
    try:
        # Send the POST request with the SQL query as payload
        response = requests.post(api_url, json=payload, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()  # Return the result from the API
        else:
            return {"error": f"Failed to execute query. Status code: {response.status_code}"}
    
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    # Example usage:
    # sql_query = "SELECT * FROM IMDB_Movie_Data LIMIT 3"
    sql_query = get_sql_query("Which movies released in 2016 have a rating above 8?")

    print("-----------------")
    print(sql_query)
    print("-----------------")
    data = send_sql_query_to_api(sql_query['column_list'])
    df = pd.DataFrame(data)
    
    # Reordering columns with 'Rank' and 'Title' as the first two
    cols = ['Rank', 'Title'] + [col for col in df.columns if col not in ['Rank', 'Title']]
    # return df[cols]
    print(df[cols])
