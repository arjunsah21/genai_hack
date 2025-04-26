import os
import streamlit as st
import pandas as pd
import pymysql
from dotenv import load_dotenv
from openai import OpenAI
import time
from sqlalchemy import create_engine
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Initialize OpenAI client once globally
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
client = OpenAI(api_key=openai_api_key)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MARIADB_HOST', 'localhost'),
    'port': int(os.getenv('MARIADB_PORT', '3306')),
    'user': os.getenv('MARIA_USER', 'root'),
    'password': os.getenv('MARIA_PASS', ''),
    'database': os.getenv('MARIA_DB', 'imdb_db')
}

def get_db_connection_string():
    """Create SQLAlchemy connection string"""
    return f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

def get_schema_info():
    """Get detailed schema information for the movie database"""
    schema = """
Database Schema:

Main Tables:
- movie (Contains movie details)
  - MID (Primary Key)
  - title
  - year
  - rating
  - num_votes

- person (Information about people)
  - PID (Primary Key)
  - Name
  - DOB
  - Gender

- genre
  - GID (Primary Key)
  - Name

- language
  - LAID (Primary Key)
  - Name

- country
  - CID (Primary Key)
  - Name

- location
  - LID (Primary Key)
  - Name

Mapping/Junction Tables:
- m_producer (Links movies with producers)
  - ID (Primary Key)
  - MID (Foreign Key to movie.MID)
  - PID (Foreign Key to person.PID)

- m_director (Links movies with directors)
  - ID (Primary Key)
  - MID (Foreign Key to movie.MID)
  - PID (Foreign Key to person.PID)

- m_cast (Links movies with cast members)
  - ID (Primary Key)
  - MID (Foreign Key to movie.MID)
  - PID (Foreign Key to person.PID)

- m_genre (Links movies with genres)
  - ID (Primary Key)
  - MID (Foreign Key to movie.MID)
  - GID (Foreign Key to genre.GID)

- m_language (Links movies with languages)
  - ID (Primary Key)
  - MID (Foreign Key to movie.MID)
  - LAID (Foreign Key to language.LAID)

- m_country (Links movies with countries)
  - ID (Primary Key)
  - MID (Foreign Key to movie.MID)
  - CID (Foreign Key to country.CID)

- m_location (Links movies with filming locations)
  - ID (Primary Key)
  - MID (Foreign Key to movie.MID)
  - LID (Foreign Key to location.LID)
"""
    return schema

def test_db_connection():
    """Test database connection and validate schema"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            required_tables = ['movie', 'person', 'm_cast', 'm_director', 
                             'm_producer', 'genre', 'm_genre', 'language', 
                             'm_language', 'country', 'm_country', 'location', 'm_location']
            missing_tables = [table for table in required_tables if table not in tables]
            if missing_tables:
                st.warning(f"Warning: The following tables are missing from the database: {', '.join(missing_tables)}")
        connection.close()
        return True
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return False

def generate_sql(query):
    """Generate SQL query from natural language"""
    try:
        schema_context = get_schema_info()

        prompt = f"""You are a SQL expert helping to convert natural language queries to SQL for a movie database.

{schema_context}

Important Instructions:
1. Generate ONLY the SQL query, no explanations
2. Use table and column names exactly as given
3. Use INNER JOIN unless specified otherwise
4. Limit results to 100 rows unless told otherwise
5. Include ORDER BY where appropriate
6. Only SELECT queries allowed

Examples:
Query: "Show me all movies directed by Christopher Nolan"
SQL: SELECT movie.title, movie.year, movie.rating 
FROM movie 
INNER JOIN m_director ON movie.MID = m_director.MID 
INNER JOIN person ON m_director.PID = person.PID 
WHERE person.Name LIKE '%Christopher Nolan%' 
ORDER BY movie.rating DESC 
LIMIT 100;

Query: "What are the top 10 highest rated movies?"
SQL: SELECT title, year, rating, num_votes 
FROM movie 
ORDER BY rating DESC, num_votes DESC 
LIMIT 10;

User Query: {query}

SQL Query:"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": "You are a SQL query generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        sql = response.choices[0].message.content.strip()

        if not sql.lower().startswith('select'):
            return "ERROR: Only SELECT queries are allowed."
        
        return sql

    except Exception as e:
        return f"Error generating SQL: {str(e)}"

def execute_query_bkp(sql_query):
    """Execute SQL query and return results"""
    start_time = time.time()
    try:
        connection_string = get_db_connection_string()
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            df = pd.read_sql(sql_query, connection)
        execution_time = time.time() - start_time
        return df, execution_time
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return pd.DataFrame(), time.time() - start_time
    
def execute_query(sql_query):
    """Execute SQL query and return results"""
    start_time = time.time()
    try:
        connection_string = get_db_connection_string()
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            # Use SQLAlchemy text() to properly handle parameters
            query = text(sql_query)
            df = pd.read_sql(query, connection)
        execution_time = time.time() - start_time
        return df, execution_time
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return pd.DataFrame(), time.time() - start_time

def apply_custom_css():
    """Apply custom CSS"""
    st.markdown("""
    <style>
    .stApp { max-width: 1200px; margin: 0 auto; }
    .result-stats { padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin-bottom: 10px; }
    .sql-query { padding: 15px; border-left: 3px solid #4CAF50; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Movie Database Query System",
        page_icon="🎬",
        layout="wide"
    )

    apply_custom_css()
    st.title("🎬 Movie Database Query System")
    st.markdown("Ask questions about movies in natural language and get results from our IMDB-style database.")

    if 'db_tested' not in st.session_state:
        with st.spinner("Testing database connection..."):
            st.session_state.db_tested = test_db_connection()
            if st.session_state.db_tested:
                st.success("Database connection successful!")

    if 'query_history' not in st.session_state:
        st.session_state.query_history = []

    if 'user_query' not in st.session_state:
        st.session_state.user_query = ""

    with st.sidebar:
        st.title("Query Tools")
        st.subheader("Example Queries")
        examples = [
            "List top 10 famous movies?",
            "List all action movies released after 2013",
            "Show me all movies directed by Rohena Gera"
        ]
        for i, example in enumerate(examples):
            if st.button(f"▶ {example[:40]}...", key=f"example_{i}"):
                st.session_state.user_query = example
                st.rerun()

        if st.session_state.query_history:
            st.subheader("Recent Queries")
            for i, (query, _) in enumerate(st.session_state.query_history[-5:]):
                if st.button(f"🔄 {query[:30]}...", key=f"history_{i}"):
                    st.session_state.user_query = query
                    st.rerun()

    user_input = st.text_input(
        "Enter your question about movies:",
        value=st.session_state.user_query,
        key="user_input_widget",
        placeholder="e.g., Show me all movies directed by Christopher Nolan"
    )

    st.session_state.user_query = user_input

    col1, col2 = st.columns([1, 5])
    with col1:
        execute_button = st.button("Execute Query", type="primary")
    with col2:
        if st.button("Clear"):
            st.session_state.user_query = ""
            st.rerun()

    if user_input and (execute_button or 'last_query' not in st.session_state or st.session_state.last_query != user_input):
        st.session_state.last_query = user_input

        try:
            with st.spinner("Generating SQL query..."):
                sql_query = generate_sql(user_input)

                if sql_query.startswith("ERROR:"):
                    st.error(sql_query)
                else:
                    with st.expander("View SQL Query", expanded=True):
                        st.code(sql_query, language="sql")

                    with st.spinner("Executing query..."):
                        df, execution_time = execute_query(sql_query)

                        st.session_state.query_history.append((user_input, sql_query))

                        if not df.empty:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Results Found", f"{len(df)}")
                            with col2:
                                st.metric("Columns", f"{len(df.columns)}")
                            with col3:
                                st.metric("Query Time", f"{execution_time:.2f}s")

                            st.subheader("Results")
                            st.dataframe(df, use_container_width=True, hide_index=True)

                            col1, col2 = st.columns(2)
                            with col1:
                                csv = df.to_csv(index=False)
                                st.download_button("Download CSV", data=csv, file_name="movie_query_results.csv", mime="text/csv")
                            with col2:
                                json_data = df.to_json(orient="records")
                                st.download_button("Download JSON", data=json_data, file_name="movie_query_results.json", mime="application/json")
                        else:
                            st.info("No results found for your query. Try rephrasing your question.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Try rephrasing your question or check the database connection.")

if __name__ == "__main__":
    main()
