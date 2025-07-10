# RunThing CLI

RunThing is a lightweight command-line application to help runners track and analyze their workouts.

## Features
- Log runs with distance, time, date, pace, and notes (interactive input available).
- Store data locally in a SQLite database.
- List all logged runs.
- Delete specific run records (interactive or with `--force`).
- Edit existing run records (interactive).
- Filter runs by date range (interactive).
- View overall running statistics, including monthly summaries, best efforts, and performance predictions.
- Generate a PDF report of all runs and statistics.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/RunThing.git
    cd RunThing
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Initialize the database
Before logging your first run, you need to initialize the database:

```bash
python -m runthing init
```

This will create a `runs.db` file in your current working directory.

### Log a new run

To log a run, use the `log` command. You can provide details as arguments or be prompted interactively.

-   `--date`: (Optional) Date of the run in `DD-MM-YYYY` format. Defaults to today's date.
-   `--distance`: (Optional) Distance of the run (e.g., 5.0 for 5 kilometers).
-   `--time`: (Optional) Duration of the run in `HH:MM:SS` or `MM:SS` format (e.g., `00:30:00` or `30:00`).
-   `--pace`: (Optional) Pace in minutes per kilometer. If not provided, it will be calculated.
-   `--notes`: (Optional) Any notes for the run. If your notes contain spaces, enclose them in quotes (e.g., `--notes "Morning jog in the park."`).

**Interactive Logging:**
If you run `log` without any arguments, it will prompt you for each piece of information:
```bash
python -m runthing log
```

**Examples (Command-line arguments):**

Log a 10km run in 50 minutes:
```bash
python -m runthing log --distance 10.0 --time 50:00
```

Log a 5km run on a specific date with notes:
```bash
python -m runthing log --date 01-07-2023 --distance 5.0 --time 25:30 --notes "Morning jog in the park."
```

Log a run with a specified pace:
```bash
python -m runthing log --distance 7.5 --time 40:00 --pace 5.33
```

### List all runs

To view all your logged runs. Dates will be displayed in "Day Month Year" format.

```bash
python -m runthing list-runs
```

### Delete a run

To delete a run by its ID (you can find the ID using `list-runs`). You will be prompted for confirmation unless `--force` is used.

```bash
python -m runthing delete <RUN_ID>
# Or interactively
python -m runthing delete
# Or without confirmation
python -m runthing delete <RUN_ID> --force
```

**Example:**
```bash
python -m runthing delete 1
```

### Edit a run

To edit an existing run by its ID. You will be prompted for new values for each field. Dates should be entered in `DD-MM-YYYY` format.

```bash
python -m runthing edit <RUN_ID>
# Or interactively
python -m runthing edit
```

**Example:**
```bash
python -m runthing edit 1
```

### Filter runs by date

To filter runs by a specific date or a date range. You can provide dates as arguments or be prompted interactively. Dates should be entered in `DD-MM-YYYY` format.

-   `--start-date`: The start date (DD-MM-YYYY).
-   `--end-date`: (Optional) The end date (DD-MM-YYYY). If omitted, only runs on the start date are shown.

**Interactive Filtering:**
If you run `filter-runs` without any arguments, it will prompt you for the start and end dates:
```bash
python -m runthing filter-runs
```

**Examples (Command-line arguments):**

Filter runs for a specific date:
```bash
python -m runthing filter-runs --start-date 10-07-2025
```

Filter runs within a date range:
```bash
python -m runthing filter-runs --start-date 01-07-2025 --end-date 31-07-2025
```

### View statistics

To see your overall running statistics, monthly summaries, and best efforts:

```bash
python -m runthing stats
```

### Performance Prediction

To predict your performance for a target distance based on your average pace. You can specify the number of most recent runs to consider for the prediction.

```bash
python -m runthing predict <TARGET_DISTANCE> [--recent-runs <NUMBER_OF_RUNS>]
# Or interactively
python -m runthing predict
```

**Examples:**

Predict for 5km using all runs:
```bash
python -m runthing predict 5.0
```

Predict for 10km using the last 3 runs:
```bash
python -m runthing predict 10.0 --recent-runs 3
```

### Generate PDF Report

To generate a PDF report containing all your runs and overall statistics. The PDF will not show run IDs and dates will be formatted as "Day Month Year".

```bash
python -m runthing pdf
# Or specify a filename
python -m runthing pdf --filename "my_runs_report.pdf"
```

## Development

To run the tests or contribute, please refer to the `CONTRIBUTING.md` (future) and `architecture.md` files.