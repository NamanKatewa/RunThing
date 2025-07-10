import sqlite3
import os

DATABASE_FILE = 'runs.db'

def get_db_path():
    """Returns the absolute path to the database file."""
    return os.path.join(os.getcwd(), DATABASE_FILE)

def connect_db():
    """Establishes a connection to the SQLite database."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def init_db():
    """Initializes the database by creating the 'runs' table if it doesn't exist."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                distance REAL NOT NULL,
                time INTEGER NOT NULL,
                pace REAL,
                notes TEXT
            )
        """)
        conn.commit()

def delete_run(run_id):
    """Deletes a run record from the database by its ID."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM runs WHERE id = ?", (run_id,))
        conn.commit()
        return cursor.rowcount > 0 # Returns True if a row was deleted, False otherwise

def get_runs_by_date_range(start_date, end_date):
    """Fetches run records within a specified date range."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, distance, time, pace, notes FROM runs WHERE date BETWEEN ? AND ? ORDER BY date DESC", (start_date, end_date))
        return cursor.fetchall()

def get_run_by_id(run_id):
    """Fetches a single run record by its ID."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, distance, time, pace, notes FROM runs WHERE id = ?", (run_id,))
        return cursor.fetchone()

def update_run(run_id, date, distance, time, pace, notes):
    """Updates an existing run record in the database."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE runs
            SET date = ?, distance = ?, time = ?, pace = ?, notes = ?
            WHERE id = ?
        """, (date, distance, time, pace, notes, run_id))
        conn.commit()
        return cursor.rowcount > 0

def get_monthly_summary():
    """Retrieves total distance and time for each month."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                strftime('%Y-%m', date) AS month,
                SUM(distance) AS total_distance,
                SUM(time) AS total_time
            FROM runs
            GROUP BY month
            ORDER BY month DESC
        """
        )
        return cursor.fetchall()

def get_fastest_run_for_distance(distance):
    """Retrieves the run with the fastest pace for a given exact distance."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, distance, time, pace, notes
            FROM runs
            WHERE distance = ?
            ORDER BY pace ASC
            LIMIT 1
        """, (distance,))
        return cursor.fetchone()

def get_last_n_runs(n):
    """Retrieves the last N runs, ordered by date descending."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, distance, time, pace, notes FROM runs ORDER BY date DESC, id DESC LIMIT ?", (n,))
        return cursor.fetchall()

if __name__ == '__main__':
    # This block is for testing the database initialization
    print(f"Initializing database at: {get_db_path()}")
    init_db()
    print("Database initialized successfully.")