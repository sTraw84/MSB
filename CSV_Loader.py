import csv
import tempfile

def load_and_verify_csv(file_path):
    try:
        rows = []
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames

            # Verify proper column headers
            required_headers = ["NUMBER", "PROMPT", "KEY", "DATA", "MARKER"]
            if headers != required_headers:
                raise ValueError(f"CSV does not have the required headers. Found: {headers}")

            rows = list(reader)

            # Verify NUMBER column is in numerical order
            numbers = [int(row["NUMBER"]) for row in rows]
            if numbers != sorted(numbers):
                raise ValueError("NUMBER column is not in numerical order.")

            # Check and handle the last row
            if rows:
                last_row = rows[-1]
                if last_row["PROMPT"] == "FINISHED":
                    rows.pop()  # Remove the FINISHED row
                    last_row = rows[-1] if rows else None

                if last_row and last_row["PROMPT"] != "UPARROW":
                    # Add UPARROW row
                    rows.append({"NUMBER": str(numbers[-1] + 1), "PROMPT": "UPARROW", "KEY": "UPARROW", "DATA": "", "MARKER": ""})

        # Write the modified rows to a temporary file
        temp_csv_file = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='')
        with open(temp_csv_file.name, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=required_headers)
            writer.writeheader()
            writer.writerows(rows)

        return temp_csv_file

    except Exception as e:
        print(f"Error loading and verifying CSV: {e}")
        raise