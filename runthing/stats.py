import sqlite3
from .database import connect_db, get_monthly_summary, get_fastest_run_for_distance, get_last_n_runs

def get_total_distance():
    """Calculates the total distance of all logged runs."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SUM(distance) FROM runs")
        total_distance = cursor.fetchone()[0]
        return total_distance if total_distance is not None else 0.0
    finally:
        conn.close()

def get_total_time():
    """Calculates the total time of all logged runs in seconds."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SUM(time) FROM runs")
        total_time = cursor.fetchone()[0]
        return total_time if total_time is not None else 0
    finally:
        conn.close()

def get_average_pace():
    """Calculates the average pace of all logged runs in minutes per km."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SUM(distance), SUM(time) FROM runs")
        total_distance, total_time = cursor.fetchone()

        if total_distance is not None and total_distance > 0 and total_time is not None:
            average_pace = (total_time / 60) / total_distance
            return average_pace
        else:
            return 0.0
    finally:
        conn.close()

def get_cumulative_progress():
    """Calculates cumulative distance and time over time."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT date, SUM(distance) OVER (ORDER BY date) as cumulative_distance,
                   SUM(time) OVER (ORDER BY date) as cumulative_time
            FROM runs
            ORDER BY date ASC
        """
        )
        return cursor.fetchall()
    finally:
        conn.close()

def predict_performance(target_distance, num_recent_runs=None):
    """Predicts time for a target distance based on average pace of recent runs or all runs."""
    runs_to_consider = []
    if num_recent_runs and num_recent_runs > 0:
        runs_to_consider = get_last_n_runs(num_recent_runs)
    else:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT distance, time FROM runs")
        runs_to_consider = cursor.fetchall()
        conn.close()

    if not runs_to_consider:
        return None

    total_distance_considered = sum(run['distance'] for run in runs_to_consider)
    total_time_considered = sum(run['time'] for run in runs_to_consider)

    if total_distance_considered == 0:
        return None

    average_pace_seconds_per_km = total_time_considered / total_distance_considered
    predicted_time_seconds = int(average_pace_seconds_per_km * target_distance)
    return predicted_time_seconds

def get_best_efforts():
    """Retrieves best efforts for common distances."""
    common_distances = [5.0, 10.0, 21.1, 42.2] # 5k, 10k, Half Marathon, Marathon
    best_efforts = {}
    for dist in common_distances:
        run = get_fastest_run_for_distance(dist)
        if run:
            best_efforts[dist] = run
    return best_efforts
