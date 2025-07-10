import datetime

def convert_to_display_date(date_str):
    """Converts a YYYY-MM-DD date string to 'Day Month Year' format."""
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d %B %Y')
    except ValueError:
        return date_str # Return original if format is unexpected

def convert_to_db_date(date_str):
    """Converts a DD-MM-YYYY date string to YYYY-MM-DD format for database storage."""
    try:
        date_obj = datetime.datetime.strptime(date_str, '%d-%m-%Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return date_str # Return original if format is unexpected (e.g., already YYYY-MM-DD)
