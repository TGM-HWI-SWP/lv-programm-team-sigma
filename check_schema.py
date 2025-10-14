import sqlite3
import streamlit as st

def check_database_schema(db_path='streamlit-projekt/stammdatenverwaltung.db'):
    """
    Check and display the database schema for stammdatenverwaltung.db
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        st.title("Database Schema: stammdatenverwaltung.db")
        
        if not tables:
            st.warning("No tables found in the database.")
            return
        
        # For each table, get its schema
        for table in tables:
            table_name = table[0]
            st.subheader(f"Table: {table_name}")
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Display column information
            st.write("Columns:")
            for col in columns:
                col_id, name, dtype, not_null, default, pk = col
                st.write(f"  - **{name}** ({dtype})" + 
                        (f" - PRIMARY KEY" if pk else "") +
                        (f" - NOT NULL" if not_null else "") +
                        (f" - DEFAULT: {default}" if default else ""))
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            st.info(f"Total rows: {count}")
            st.divider()
        
        conn.close()
        
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    except Exception as e:
        st.error(f"Error: {e}")

if __name__ == "__main__":
    check_database_schema()