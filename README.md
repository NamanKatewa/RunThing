# RunThing

A simple command-line tool for tracking your runs.

## Summary

RunThing is a CLI application that allows you to log, view, and analyze your running data. It provides features for tracking your progress, predicting performance, and generating reports.

## Features

- Log new runs with details like date, distance, time, and notes.
- List all your logged runs.
- Delete runs by their ID.
- Filter runs by a date range.
- Edit existing runs.
- Predict your performance for a target distance.
- View overall running statistics, monthly summaries, and best efforts.
- Generate a PDF report of all your runs and statistics.
- Compare your last two runs to see your improvement.

## Tools and Technologies

- **Python**: The core programming language.
- **Click**: For creating the command-line interface.
- **SQLite**: For the database to store run data.
- **ReportLab**: For generating PDF reports.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/RunThing.git
   ```
2. Navigate to the project directory:
   ```bash
   cd RunThing
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To use RunThing, you can run the following commands:

- `python -m runthing init`: Initializes the database.
- `python -m runthing log`: Logs a new run.
- `python -m runthing list-runs`: Lists all logged runs.
- `python -m runthing delete`: Deletes a run by its ID.
- `python -m runthing filter-runs`: Filters runs by a date range.
- `python -m runthing edit`: Edits an existing run.
- `python -m runthing predict`: Predicts performance for a target distance.
- `python -m runthing stats`: Displays overall running statistics.
- `python -m runthing pdf`: Generates a PDF report of all runs.
- `python -m runthing compare`: Compares the last two runs.
