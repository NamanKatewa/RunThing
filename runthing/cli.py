import click
import datetime
from .stats import get_total_distance, get_total_time, get_average_pace, predict_performance, get_best_efforts, compare_runs
from .database import init_db, connect_db, delete_run, get_runs_by_date_range, get_run_by_id, update_run, get_monthly_summary, get_last_two_runs
from .pdf_generator import generate_run_report_pdf
from .utils import convert_to_display_date, convert_to_db_date

@click.group()
def cli():
    """A command-line tool for tracking your runs."""
    pass

@cli.command()
def init():
    """Initializes the database for RunThing."""
    init_db()
    click.echo("RunThing database initialized.")

@cli.command()
@click.option('--date', default=None, help='Date of the run (DD-MM-YYYY). Defaults to today.')
@click.option('--distance', type=float, default=None, help='Distance of the run in kilometers.')
@click.option('--time', type=str, default=None, help='Duration of the run (HH:MM:SS or MM:SS).')
@click.option('--pace', type=float, default=None, help='Pace of the run in minutes per kilometer.')
@click.option('--notes', type=str, default=None, help='Optional notes for the run.') # Changed default to None
def log(date, distance, time, pace, notes):
    """Logs a new run. If no arguments are provided, it will prompt for input."""
    if date is None:
        date = click.prompt('Date of the run (DD-MM-YYYY)', default=datetime.date.today().strftime('%d-%m-%Y'))
    
    # Convert input date to DB format
    db_date = convert_to_db_date(date)

    if distance is None:
        distance = click.prompt('Distance of the run in kilometers', type=float)

    if time is None:
        time = click.prompt('Duration of the run (HH:MM:SS or MM:SS)')

    # Convert time to seconds
    time_parts = [int(p) for p in time.split(':')]
    if len(time_parts) == 3:
        hours, minutes, seconds = time_parts
    elif len(time_parts) == 2:
        hours = 0
        minutes, seconds = time_parts
    else:
        click.echo("Error: Time format must be HH:MM:SS or MM:SS.")
        return
    total_seconds = hours * 3600 + minutes * 60 + seconds

    # Calculate pace if not provided
    if pace is None:
        if distance > 0:
            pace = (total_seconds / 60) / distance  # minutes per km
        else:
            click.echo("Error: Distance must be greater than 0 to calculate pace.")
            return
        click.echo(f"Calculated pace: {pace:.2f} min/km")
    
    # Handle notes: if not provided as argument, prompt. If provided as empty string, store as None.
    if notes is None:
        notes = click.prompt('Optional notes for the run', default='', show_default=False)
        if notes == '':
            notes = None
    elif notes == '': # If notes was provided as an empty string argument
        notes = None

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO runs (date, distance, time, pace, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (db_date, distance, total_seconds, pace, notes))
        conn.commit()
        click.echo(f"Run logged successfully on {convert_to_display_date(db_date)}: {distance} km in {time} (Pace: {pace:.2f} min/km).")
    except Exception as e:
        click.echo(f"Error logging run: {e}")
    finally:
        conn.close()

@cli.command()
def list_runs():
    """Lists all logged runs."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, date, distance, time, pace, notes FROM runs ORDER BY date DESC")
        runs = cursor.fetchall()

        if not runs:
            click.echo("No runs logged yet.")
            return

        click.echo("\n--- Your Runs ---")
        for run in runs:
            # Convert total_seconds back to HH:MM:SS or MM:SS for display
            total_seconds = run['time']
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            time_str = f"{minutes:02d}:{seconds:02d}"
            if hours > 0:
                time_str = f"{hours:02d}:" + time_str

            notes_str = f" ({run['notes']})" if run['notes'] else ""
            click.echo(f"ID: {run['id']}, Date: {convert_to_display_date(run['date'])}, Distance: {run['distance']:.2f} km, Time: {time_str}, Pace: {run['pace']:.2f} min/km{notes_str}")
        click.echo("-------------------")

    except Exception as e:
        click.echo(f"Error listing runs: {e}")
    finally:
        conn.close()

@cli.command()
@click.argument('run_id', type=int, required=False)
@click.option('--force', is_flag=True, help='Do not ask for confirmation.')
def delete(run_id, force):
    """Deletes a run by its ID. Prompts for ID if not provided."""
    if run_id is None:
        run_id = click.prompt('Enter the ID of the run to delete', type=int)

    if force or click.confirm(f"Are you sure you want to delete run with ID {run_id}?", abort=True):
        if delete_run(run_id):
            click.echo(f"Run with ID {run_id} deleted successfully.")
        else:
            click.echo(f"Run with ID {run_id} not found.")

@cli.command()
@click.option('--start-date', default=None, help='Start date (DD-MM-YYYY).')
@click.option('--end-date', default=None, help='End date (DD-MM-YYYY). Defaults to start date.')
def filter_runs(start_date, end_date):
    """Filters runs by a date range. Prompts for dates if not provided."""
    if start_date is None:
        start_date = click.prompt('Enter start date (DD-MM-YYYY)')
    
    if end_date is None:
        end_date = click.prompt('Enter end date (DD-MM-YYYY) (leave blank for same as start date)', default=start_date, show_default=False)
        if end_date == '':
            end_date = start_date

    # Convert input dates to DB format
    db_start_date = convert_to_db_date(start_date)
    db_end_date = convert_to_db_date(end_date)

    try:
        # Validate date formats
        datetime.date.fromisoformat(db_start_date)
        datetime.date.fromisoformat(db_end_date)
    except ValueError:
        click.echo("Error: Date format must be DD-MM-YYYY.")
        return

    runs = get_runs_by_date_range(db_start_date, db_end_date)

    if not runs:
        click.echo(f"No runs found between {convert_to_display_date(db_start_date)} and {convert_to_display_date(db_end_date)}.")
        return

    click.echo(f"\n--- Runs from {convert_to_display_date(db_start_date)} to {convert_to_display_date(db_end_date)} ---")
    for run in runs:
        total_seconds = run['time']
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        time_str = f"{minutes:02d}:{seconds:02d}"
        if hours > 0:
            time_str = f"{hours:02d}:" + time_str

        notes_str = f" ({run['notes']})" if run['notes'] else ""
        click.echo(f"ID: {run['id']}, Date: {convert_to_display_date(run['date'])}, Distance: {run['distance']:.2f} km, Time: {time_str}, Pace: {run['pace']:.2f} min/km{notes_str}")
    click.echo("--------------------------")

@cli.command()
@click.argument('run_id', type=int, required=False)
def edit(run_id):
    """Edits an existing run by its ID. Prompts for ID if not provided."""
    if run_id is None:
        run_id = click.prompt('Enter the ID of the run to edit', type=int)

    run = get_run_by_id(run_id)
    if not run:
        click.echo(f"Run with ID {run_id} not found.")
        return

    click.echo(f"\n--- Editing Run ID: {run['id']} ---")
    click.echo(f"Current Date: {convert_to_display_date(run['date'])}")
    new_date = click.prompt('New Date (DD-MM-YYYY)', default=datetime.datetime.strptime(run['date'], '%Y-%m-%d').strftime('%d-%m-%Y'))
    db_new_date = convert_to_db_date(new_date)

    click.echo(f"Current Distance: {run['distance']:.2f} km")
    new_distance = click.prompt('New Distance (km)', type=float, default=run['distance'])

    # Convert current time (seconds) to HH:MM:SS or MM:SS for display
    current_total_seconds = run['time']
    current_hours = current_total_seconds // 3600
    current_minutes = (current_total_seconds % 3600) // 60
    current_seconds = current_total_seconds % 60
    current_time_str = f"{current_minutes:02d}:{current_seconds:02d}"
    if current_hours > 0:
        current_time_str = f"{current_hours:02d}:" + current_time_str

    click.echo(f"Current Time: {current_time_str}")
    new_time_str = click.prompt('New Duration (HH:MM:SS or MM:SS)', default=current_time_str)

    # Convert new_time_str to seconds
    time_parts = [int(p) for p in new_time_str.split(':')]
    if len(time_parts) == 3:
        hours, minutes, seconds = time_parts
    elif len(time_parts) == 2:
        hours = 0
        minutes, seconds = time_parts
    else:
        click.echo("Error: Time format must be HH:MM:SS or MM:SS.")
        return
    new_total_seconds = hours * 3600 + minutes * 60 + seconds

    click.echo(f"Current Pace: {run['pace']:.2f} min/km")
    new_pace = click.prompt('New Pace (min/km) (leave blank to recalculate)', type=float, default=run['pace'], show_default=False)
    if new_pace == run['pace'] and new_pace == '': # If user left blank and it was already blank
        if new_distance > 0:
            new_pace = (new_total_seconds / 60) / new_distance
            click.echo(f"Recalculated pace: {new_pace:.2f} min/km")
        else:
            click.echo("Error: Distance must be greater than 0 to calculate pace.")
            return
    elif new_pace == '': # If user left blank and it had a value, recalculate
        if new_distance > 0:
            new_pace = (new_total_seconds / 60) / new_distance
            click.echo(f"Recalculated pace: {new_pace:.2f} min/km")
        else:
            click.echo("Error: Distance must be greater than 0 to calculate pace.")
            return

    click.echo(f"Current Notes: {run['notes'] if run['notes'] else ''}")
    new_notes = click.prompt('New Notes', default=run['notes'] if run['notes'] else '', show_default=False)
    if new_notes == '':
        new_notes = None

    try:
        if update_run(run_id, db_new_date, new_distance, new_total_seconds, new_pace, new_notes):
            click.echo(f"Run with ID {run_id} updated successfully.")
        else:
            click.echo(f"Failed to update run with ID {run_id}.")
    except Exception as e:
        click.echo(f"Error updating run: {e}")

@cli.command()
@click.argument('target_distance', type=float, required=False)
@click.option('--recent-runs', type=int, default=None, help='Number of most recent runs to consider for prediction.')
def predict(target_distance, recent_runs):
    """Predicts performance for a target distance based on average pace."""
    if target_distance is None:
        target_distance = click.prompt('Enter target distance for prediction in kilometers', type=float)

    if recent_runs is None:
        recent_runs = click.prompt('Number of most recent runs to consider for prediction (leave blank for all runs)', type=int, default=0, show_default=False)
        if recent_runs == 0:
            recent_runs = None # Use None to indicate all runs

    predicted_time_seconds = predict_performance(target_distance, recent_runs)

    if predicted_time_seconds is None:
        click.echo("Not enough data to predict performance. Log more runs.")
        return

    hours = predicted_time_seconds // 3600
    minutes = (predicted_time_seconds % 3600) // 60
    seconds = predicted_time_seconds % 60
    predicted_time_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

    click.echo(f"\n--- Performance Prediction ---")
    click.echo(f"Based on your average pace, you can expect to run {target_distance:.2f} km in approximately {predicted_time_str}.")
    click.echo("------------------------------")

@cli.command()
def stats():
    """Displays overall running statistics, monthly summaries, and best efforts."""
    total_distance = get_total_distance()
    total_time_seconds = get_total_time()
    average_pace = get_average_pace()

    if total_distance == 0:
        click.echo("No runs logged yet to generate statistics.")
        return

    # Format total time
    hours = total_time_seconds // 3600
    minutes = (total_time_seconds % 3600) // 60
    seconds = total_time_seconds % 60
    total_time_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

    click.echo("\n--- Overall Running Statistics ---")
    click.echo(f"Total Distance: {total_distance:.2f} km")
    click.echo(f"Total Time: {total_time_str}")
    click.echo(f"Average Pace: {average_pace:.2f} min/km")
    click.echo("----------------------------------")

    # Monthly Summary
    monthly_summary = get_monthly_summary()
    if monthly_summary:
        click.echo("\n--- Monthly Summary ---")
        for month_data in monthly_summary:
            month_name = datetime.datetime.strptime(month_data['month'], '%Y-%m').strftime('%B %Y')
            month_total_time_seconds = month_data['total_time']
            month_hours = month_total_time_seconds // 3600
            month_minutes = (month_total_time_seconds % 3600) // 60
            month_seconds = month_total_time_seconds % 60
            month_time_str = f"{month_hours:02d}h {month_minutes:02d}m {month_seconds:02d}s"
            click.echo(f"{month_name}: {month_data['total_distance']:.2f} km in {month_time_str}")
        click.echo("-----------------------")

    # Best Efforts
    best_efforts = get_best_efforts()
    if best_efforts:
        click.echo("\n--- Best Efforts (Fastest Pace) ---")
        for distance, run in best_efforts.items():
            total_seconds = run['time']
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            if hours > 0:
                time_str = f"{hours:02d}:" + time_str
            click.echo(f"{distance:.1f} km: {time_str} (Pace: {run['pace']:.2f} min/km) on {convert_to_display_date(run['date'])}")
        click.echo("-----------------------------------")

@cli.command()
@click.option('--filename', default='run_report.pdf', help='Name of the PDF file to generate.')
def pdf(filename):
    """Generates a PDF report of all runs and statistics."""
    try:
        generated_file = generate_run_report_pdf(filename)
        click.echo(f"PDF report generated successfully: {generated_file}")
    except Exception as e:
        click.echo(f"Error generating PDF report: {e}")

@cli.command()
def compare():
    """Compares the last two runs and shows the improvement."""
    runs = get_last_two_runs()
    if len(runs) < 2:
        click.echo("Not enough runs to compare. At least two runs are required.")
        return

    last_run = runs[0]
    second_last_run = runs[1]

    improvement = compare_runs(last_run, second_last_run)

    if improvement is None:
        click.echo("Could not compare runs due to missing data.")
        return

    click.echo(f"Comparing last two runs:")
    click.echo(f"  - Run on {convert_to_display_date(second_last_run['date'])}: Pace: {second_last_run['pace']:.2f} min/km")
    click.echo(f"  - Run on {convert_to_display_date(last_run['date'])}: Pace: {last_run['pace']:.2f} min/km")

    if improvement > 0:
        click.echo(f"Improvement: {abs(improvement):.2f}% slower.")
    else:
        click.echo(f"Improvement: {abs(improvement):.2f}% faster.")


if __name__ == '__main__':
    cli()