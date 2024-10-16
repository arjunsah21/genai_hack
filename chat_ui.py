import streamlit as st
import json
import os
import uuid
import atexit
from datetime import datetime
from pytz import timezone
from query_maria_db import send_sql_query_to_api, get_sql_query
import pandas as pd

def is_running_with_streamlit():
    try:
        from streamlit.runtime.scriptrunner import script_run_context as src
        return src.get_script_run_ctx() is not None
    except ImportError:
        return st._is_running_with_streamlit

def get_ist_timestamp():
    ist = timezone('Asia/Kolkata')
    return datetime.now(ist).isoformat()

def main():
    if not is_running_with_streamlit():
        print("Error: This script should be run using `streamlit run` command.")
        print("Please use: streamlit run <script_name.py>")
        return

    st.set_page_config(page_title="Chat with OpenAI", layout="wide")
    st.title("Chat with OpenAI")

    HISTORY_DIR = "chat_histories"
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

    def get_session_id():
        query_params = st.experimental_get_query_params()
        if "session_id" in query_params:
            return query_params["session_id"][0]
        new_session_id = str(uuid.uuid4())
        st.experimental_set_query_params(session_id=new_session_id)
        return new_session_id

    session_id = get_session_id()

    def get_history_file_path(session_id):
        return os.path.join(HISTORY_DIR, f"chat_history_{session_id}.json")

    def load_chat_history(session_id):
        file_path = get_history_file_path(session_id)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return create_new_session_data(session_id)

    def create_new_session_data(session_id):
        now = get_ist_timestamp()
        return {
            "session_id": session_id,
            "conversation_id": session_id,
            "conversation_history": [],
            "user_context": {
                "user_id": "sample_user_001",
                "language": "en"
            },
            "session_metadata": {
                "session_start_time": now,
                "last_interaction_time": now,
                "expires_in": 1800
            }
        }

    def save_chat_history(session_id, data):
        file_path = get_history_file_path(session_id)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def clear_chat_history(session_id):
        file_path = get_history_file_path(session_id)
        if os.path.exists(file_path):
            os.remove(file_path)

    def delete_session_on_exit():
        clear_chat_history(session_id)

    atexit.register(delete_session_on_exit)

    if "session_data" not in st.session_state:
        st.session_state.session_data = load_chat_history(session_id)

    def display_messages():
        for message in st.session_state.session_data["conversation_history"]:
            with st.chat_message("user"):
                
                st.markdown(f"User Query: {message['query']}")
                st.markdown(f"Corrected Query: {message['corrected_query']}")
            with st.chat_message("assistant"):
                st.markdown(f"SQL Query: ```{message['sql_response']}```")
                # st.markdown(f"Database Result: \n {message['actual_response']}")
                data = message['actual_response']
                # st.markdown(type(data))
                df = pd.DataFrame(data)
                # Reordering columns with 'Rank' and 'Title' as the first two
                cols = ['Rank', 'Title'] + [col for col in df.columns if col not in ['Rank', 'Title']]
                table = df[cols]
                st.table(table)
                col1, col2, col3 = st.columns([1, 1, 8])
                if col1.button("👍", key=f"thumbs_up_{message['sequence_id']}"):
                    message["user_feedback"] = "True"
                    save_chat_history(session_id, st.session_state.session_data)
                    st.rerun()
                if col2.button("👎", key=f"thumbs_down_{message['sequence_id']}"):
                    message["user_feedback"] = "False"
                    save_chat_history(session_id, st.session_state.session_data)
                    st.rerun()
                if "user_feedback" in message:
                    feedback = "👍" if message["user_feedback"] == "True" else "👎"
                    st.write(f"Your feedback: {feedback}")

    st.sidebar.title("Session Info")
    st.sidebar.write(f"Current Session ID: {session_id}")
    st.sidebar.write("Note: Chat history will be deleted when you close the tab.")

    if st.sidebar.button("Clear Chat History"):
        st.session_state.session_data = create_new_session_data(session_id)
        save_chat_history(session_id, st.session_state.session_data)

    display_messages()

    if prompt := st.chat_input("Type your message here..."):
        # Simulate query correction, LLM and database interaction
        corrected_query = f"{prompt}"  # This is a placeholder. Replace with actual correction logic.
        sql_query = get_sql_query(prompt)
        sql_response = sql_query['column_list']
        # actual_response = "This is a mock result from the database"
        actual_response = send_sql_query_to_api(sql_response)

        now = get_ist_timestamp()
        new_message = {
            "sequence_id": len(st.session_state.session_data["conversation_history"]) + 1,
            "query": prompt,
            "corrected_query": corrected_query,
            "sql_response": sql_response,
            "actual_response": actual_response,
            "user_feedback": None,
            "timestamp": now,
            "is_relevant": "true"
        }
        st.session_state.session_data["conversation_history"].append(new_message)
        st.session_state.session_data["session_metadata"]["last_interaction_time"] = now
        save_chat_history(session_id, st.session_state.session_data)

        st.rerun()

if __name__ == "__main__":
    main()