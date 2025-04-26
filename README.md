# Natural Language to SQL Query System

A powerful natural language interface for querying a movie database. Ask questions in plain English about movies, actors, directors, genres, and more - get instant SQL-powered results with a beautiful interface.

[![Docker Image](https://img.shields.io/docker/v/arjunsah21/movie-query-app?label=docker&logo=docker)](https://hub.docker.com/r/arjunsah21/movie-query-app)

## 📋 Features

- ✨ Natural language to SQL conversion powered by OpenAI GPT
- 🎬 Comprehensive movie database with rich relationships
- 📊 Interactive web interface with Streamlit
- 📤 Export results as CSV or JSON
- 🔍 View the generated SQL query
- 🐳 Containerized for easy deployment
- 📊 Performance metrics and result statistics

## 🏗️ Architecture & Components

### System Architecture

The system consists of two main components:

1. **Frontend & Query Engine (Streamlit App)**
   - User interface for natural language queries
   - OpenAI GPT integration for NL → SQL conversion
   - Query execution and result presentation

2. **Database (MariaDB)**
   - Stores the movie dataset
   - Executes SQL queries

### Technical Components

- **OpenAI Integration**: Uses OpenAI's GPT models to understand natural language queries and generate SQL
- **Database Schema Understanding**: Provides the LLM with schema context for accurate SQL generation
- **Query Execution**: Uses SQLAlchemy for database connectivity and query execution
- **Data Visualization**: Presents results in interactive tables with Streamlit

## 🎬 Data

The application uses the IMDB dataset with the following tables:

### Main Tables
- **movie**: Movie details (MID, title, year, rating, num_votes)
- **person**: People involved in movies (PID, name)
- **genre**: Movie genres (GID, name)
- **language**: Movie languages (LAID, name)
- **country**: Countries (CID, name)
- **location**: Filming locations (LID, name)

### Relationship Tables
- **m_cast**: Links movies with cast members
- **m_director**: Links movies with directors
- **m_producer**: Links movies with producers
- **m_genre**: Links movies with genres
- **m_language**: Links movies with languages
- **m_country**: Links movies with countries
- **m_location**: Links movies with filming locations

The data is sourced from CSV files in the `data/output_csvs/` directory and imported into MariaDB during container initialization.

## 🚀 Running the Application

### Method 1: Using Pre-built Docker Images (Fastest)

1. **Prerequisites**
   - [Docker](https://docs.docker.com/get-docker/)
   - [Docker Compose](https://docs.docker.com/compose/install/)
   - OpenAI API Key

2. **Create a `docker-compose.yml` file**
   ```yaml
   version: '3.8'

   services:
     app:
       image: arjunsah21/movie-query-app:latest
       ports:
         - "8501:8501"
       depends_on:
         - mariadb
       environment:
         - MARIADB_HOST=mariadb
         - MARIADB_PORT=3306
         - MARIA_USER=root
         - MARIA_PASS=rootpassword
         - MARIA_DB=imdb_db
         - OPENAI_API_KEY=your_openai_api_key
       restart: unless-stopped

     mariadb:
       image: arjunsah21/movie-mariadb:latest
       ports:
         - "3306:3306"
       environment:
         - MYSQL_ROOT_PASSWORD=rootpassword
         - MYSQL_DATABASE=imdb_db
       volumes:
         - mariadb_data:/var/lib/mysql
       restart: unless-stopped

   volumes:
     mariadb_data:
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Open your browser and go to http://localhost:8501

### Method 2: Building Docker Images Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/movie-query-system.git
   cd movie-query-system
   ```

2. **Setup Environment**
   - Create `.env` file with your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ```

3. **Build and start the containers**
   ```bash
   docker-compose up --build -d
   ```

4. **Access the application**
   - Open your browser and go to http://localhost:8501

### Method 3: Running Locally Without Docker

1. **Prerequisites**
   - Python 3.9+ installed
   - MariaDB or MySQL installed and running
   - Data imported into your database (use `data/dump_to_mariaDB.ipynb` as reference)

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   - Create `.env` file with your database and OpenAI credentials:
     ```
     MARIADB_HOST=localhost
     MARIADB_PORT=3306
     MARIA_USER=your_username
     MARIA_PASS=your_password
     MARIA_DB=imdb_db
     OPENAI_API_KEY=your_openai_api_key
     ```

4. **Import Data (if needed)**
   - Follow instructions in `data/dump_to_mariaDB.ipynb` to import CSV data to your database
   - Or run the Python script directly:
     ```bash
     python import_data.py
     ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Access the application**
   - Open your browser and go to http://localhost:8501

## 🧠 Query Examples

Try these sample queries to explore the database:

- "Show me all movies directed by Christopher Nolan"
- "What are the top 10 highest rated movies?"
- "List all action movies in English"
- "Find movies filmed in New Zealand"
- "Who acted in The Dark Knight?"
- "Show me movies released in 2020 with a rating above 8"
- "Which actors have worked with director Steven Spielberg?"

## ⚙️ How It Works

1. **Query Processing Flow**:
   - User enters a natural language query
   - OpenAI's GPT model analyzes the query and database schema
   - The model generates appropriate SQL
   - SQL is executed against the MariaDB database
   - Results are displayed in an interactive table

2. **AI-Powered Features**:
   - Schema-aware query generation
   - Automatic handling of complex table relationships
   - SQL optimization for better performance
   - Error recovery and suggestions

## 🔧 Customization

### Using a Different Dataset

To use your own dataset:

1. Prepare your CSV files with a similar structure to those in `data/output_csvs/`
2. Update the schema information in `app.py` under the `get_schema_info()` function
3. Update the import script if your table structure differs significantly

### Model Customization

You can change the OpenAI model by updating the environment variable:
```
OPENAI_MODEL=gpt-4
```

## 📝 Notes

- This application requires an OpenAI API key to function
- The system is optimized for a movie database but can be adapted for other domains
- Default credentials are for development only - use secure passwords in production

## 📄 License

MIT License
