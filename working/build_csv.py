import sys
import os
import csv
import re

# Regular expression to match a number with exactly 4 digits
number_pattern = re.compile(r'\b\d{4}\b')

# Function to extract directory name, base name, and filtered base name
def extract_info(file_path):
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)

    # filtered_value = re.search(r'\D*(\d{4})', basename)
    filtered_value = re.search(r'^(.*?)(\d{4})(.*)$', basename)
    filtered_title = None
    filtered_year = None
    if filtered_value:
        filtered_title = filtered_value.group(1)
        filtered_year = filtered_value.group(2)
    else:
        filtered_title = basename

    # match = number_pattern.search(basename)
    # if match:
    #     filtered_basename = basename[:match.start() + 4]  # Extract the string until the 4-digit number
    # else:
    #     filtered_basename = ''
    return dirname, basename, filtered_title, filtered_year

# Main function to process input and write to CSV
def main():
    # Create a CSV writer object
    csv_writer = csv.writer(sys.stdout)

    # Write CSV header
    csv_writer.writerow(["path", "directory", "filename", "title", "year"])

    # Read lines from stdin (piped input)
    for line in sys.stdin:
        line = line.strip()
        dirname, basename, title, year = extract_info(line)
        csv_writer.writerow([line, dirname, basename, title, year])

if __name__ == "__main__":
    main()
