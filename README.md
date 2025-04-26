# Movie Database Query System

A natural language interface for querying a movie database using OpenAI's GPT models and ChromaDB for schema understanding.

## Features

- Natural language to SQL conversion
- Interactive web interface
- Example queries for easy start
- Results export to CSV
- Real-time SQL query preview

## Database Schema

The movie database includes tables for:
- Movies (title, year, rating)
- People (actors, directors, producers)
- Genres
- Languages
- Countries
- Filming Locations
- Various relationship tables (M_Cast, M_Director, etc.)

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Update with your credentials:
     ```
     MARIADB_HOST=your_host
     MARIADB_PORT=your_port
     MARIA_USER=your_username
     MARIA_PASS=your_password
     MARIA_DB=movie_db
     OPENAI_API_KEY=your_openai_key
     ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## Usage

1. Enter your question in natural language
2. The system will convert it to SQL
3. View the results in a table format
4. Optionally download results as CSV

## Example Queries

- "Show me all movies directed by Christopher Nolan"
- "What are the top 10 highest rated movies from 2020?"
- "List all action movies in English"
- "Find movies filmed in New Zealand"
- "Who acted in The Dark Knight?"

## How It Works

1. **Natural Language Understanding**:
   - Uses OpenAI's GPT-3.5 for query understanding
   - ChromaDB for schema matching

2. **Query Processing**:
   - Converts natural language to SQL
   - Handles complex joins automatically
   - Optimizes queries for performance

3. **Results Display**:
   - Clean tabular format
   - Export functionality
   - Error handling

## License

MIT License
