# RunThing Architecture

## Overview
RunThing is a command-line interface (CLI) application designed to help runners track and analyze their workout data. It prioritizes simplicity, privacy, and offline functionality by storing all data locally.

## Core Components

### 1. CLI Interface (`cli.py`)
-   Built using the `click` library for intuitive command-line parsing and user interaction.
-   Handles command-line arguments, options, and subcommands (e.g., `runthing log`, `runthing stats`, `runthing pdf`, `runthing predict`, `runthing compare`).
-   Provides interactive prompts for input when arguments or options are not provided.
-   Provides interactive prompts for input when arguments are not provided.
-   Acts as the entry point for the application.

### 2. Data Management (`database.py`)
-   Utilizes SQLite as the local, file-based database for storing run data.
-   Provides functions for:
    -   Connecting to the database.
    -   Initializing the database schema (creating tables).
    -   Performing CRUD (Create, Read, Update, Delete) operations on run records.
    -   Retrieving single run records by ID.
    -   Filtering runs by date range.
    -   Retrieving monthly run summaries.
    -   Retrieving fastest runs for specific distances.
    -   Retrieving the last two runs.

### 3. Data Models (`models.py`)
-   Defines Python classes that represent the structure of a "Run" record.
-   Facilitates object-oriented interaction with the database, abstracting raw SQL queries.

### 4. Utility Functions (`utils.py`)
-   Contains helper functions for common tasks such as:
    -   Date and time conversions (between DD-MM-YYYY, YYYY-MM-DD, and "Day Month Year" formats).
    -   Pace calculations.
    -   Input validation.
    -   Formatting output for display.

### 5. Statistics Engine (`stats.py`)
-   Contains logic for calculating and presenting various running statistics (e.g., total distance, average pace).
-   Includes functions for:
    -   Calculating cumulative progress.
    -   Predicting performance for target distances.
    -   Summarizing monthly run data.
    -   Identifying best efforts for common distances.
    -   Comparing two runs and calculating the percentage improvement in pace.
-   Queries the database via the Data Management component.

### 6. PDF Generator (`pdf_generator.py`)
-   Utilizes the `reportlab` library to create PDF reports.
-   Generates a comprehensive report including overall statistics, monthly summaries, best efforts, and a detailed list of all logged runs.
-   Formats dates as "Day Month Year" and excludes run IDs from the report.

## Data Storage
-   **Type:** SQLite database file (e.g., `runs.db`).
-   **Location:** Stored locally within the user's system, ensuring privacy and offline access.
-   **Schema (Initial `runs` table):**
    -   `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
    -   `date` (TEXT, YYYY-MM-DD format)
    -   `distance` (REAL, in kilometers or miles)
    -   `time` (INTEGER, in seconds)
    -   `pace` (REAL, calculated or input, e.g., minutes per km/mile)
    -   `notes` (TEXT, optional)

## Dependencies
-   `click`: For building the command-line interface.
-   `sqlite3` (built-in Python module): For database interactions.
-   `reportlab`: For PDF generation.

## Future Considerations
-   Configuration management (e.g., units preference: km vs. miles).
-   Import/export functionality.
-   More advanced statistical analysis and visualization.
-   Testing framework integration.
