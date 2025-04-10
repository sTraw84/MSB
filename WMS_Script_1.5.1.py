import csv
import time
import os

history, file_path, valid_prompts, rows = [], "", [], []
special_commands = {"UPARROW": "\033OA", "DOWNARROW": "\033OB", "ENTER": '\r', "BLANK": '\r', "SEND": None, "FINISHED": None, "NOTHING": None, "F4KEY": chr(27) + "OS", "CLEAR": chr(3)}

class ScriptStoppedException(Exception):
    pass

def send_command(data):
    crt.Screen.Send(data + '\r')
    crt.Screen.WaitForCursor()

def send_special_command(command):
    if command.startswith("WAIT"):
        time.sleep(float(command[4:]))
    elif command == "FINISHED":
        crt.Dialog.MessageBox("The Script has completed!")
        raise SystemExit("The Script has completed!")
    elif command != "SEND" and command != "NOTHING":
        crt.Screen.Send(special_commands.get(command, ''))
        crt.Screen.WaitForCursor()

def record_history(prompt, data):
    global history
    history.append('Prompt: {}, Data: {}'.format(prompt, data))
    if len(history) > 6:
        history.pop(0)

def wait_for_prompt_and_send_data(expected_prompt, data, current_index=None):
    global valid_prompts
    if expected_prompt in special_commands or expected_prompt.startswith("WAIT"):
        if expected_prompt == "SEND":
            send_command(data)
        elif expected_prompt != "NOTHING":
            send_special_command(expected_prompt)
        record_history(expected_prompt, data)
        return True

    start_time = time.time()
    while True:
        crt.Screen.WaitForCursor(1)
        screen_content = crt.Screen.Get(crt.Screen.CurrentRow, 1, crt.Screen.CurrentRow, crt.Screen.Columns).strip()
        if screen_content == expected_prompt or screen_content in valid_prompts:
            if screen_content == expected_prompt:
                send_command(data)
                record_history(expected_prompt, data)
                return True
            else:
                handle_unknown_prompt(screen_content, expected_prompt, data, current_index)
                return False
        if time.time() - start_time > 10:
            handle_unknown_prompt(screen_content, expected_prompt, data, current_index)
            return False
        time.sleep(0.05)

def read_csv(file_path):
    try:
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            required_columns = {'NUMBER', 'PROMPT', 'KEY', 'DATA', 'MARKER'}
            if not required_columns.issubset(set(reader.fieldnames)):
                crt.Dialog.MessageBox("CSV file must contain 'NUMBER', 'PROMPT', 'KEY', 'DATA', and 'MARKER' columns.")
                return None
            return list(reader)
    except IOError as e:
        crt.Dialog.MessageBox("Error opening or reading the CSV file: {}".format(str(e)))
        return None

def write_csv(file_path, rows):
    try:
        with open(file_path, mode='w') as file:
            writer = csv.DictWriter(file, fieldnames=['NUMBER', 'PROMPT', 'KEY', 'DATA', 'MARKER'], lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
    except IOError as e:
        crt.Dialog.MessageBox("Error writing to the CSV file: {}".format(str(e)))

def find_resume_index(rows):
    for index, row in enumerate(rows):
        if row['MARKER'] == 'LAST_PROCESSED':
            return index
    return 0

def check_marker():
    global rows
    last_processed_index = find_resume_index(rows)
    if last_processed_index > 0:
        message = ("A previous run was detected. Please choose an option:\n\n"
                   "1. Proceed from the last processed line (line {}).\n"
                   "2. Clear the marker and start from the beginning.\n"
                   "3. Stop the script.").format(last_processed_index + 1)
        user_option = crt.Dialog.Prompt(message, "Previous Run Detected", "1")
        if user_option == "1":
            return last_processed_index
        elif user_option == "2":
            for row in rows:
                row['MARKER'] = ''
            write_csv(file_path, rows)
            return 0
        elif user_option == "3":
            raise ScriptStoppedException("Script stopped by user.")
    return 0

def main():
    try:
        crt.Screen.Synchronous = True
        global file_path, rows, valid_prompts
        folder_path = "C:\\Users\\trawicks\\Desktop\\WMS Script\\CSV Files"
        csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.csv')]
        if not csv_files:
            crt.Dialog.MessageBox("No CSV files found in the folder: {}".format(folder_path))
            return
        file_options = "\n".join(["{}. {}".format(i + 1, file) for i, file in enumerate(csv_files)])
        selected_option = crt.Dialog.Prompt("Select a CSV file:\n{}".format(file_options), "Select CSV File", "1")
        try:
            selected_index = int(selected_option) - 1
            if selected_index < 0 or selected_index >= len(csv_files):
                raise ValueError
            file_path = os.path.join(folder_path, csv_files[selected_index])
        except (ValueError, IndexError):
            crt.Dialog.MessageBox("Invalid selection. Exiting script.")
            return
        if not os.path.isfile(file_path):
            crt.Dialog.MessageBox("CSV file not found: {}".format(file_path))
            return
        rows = read_csv(file_path)
        if rows is None:
            return
        try:
            number_column = [int(row['NUMBER']) for row in rows]
        except (ValueError, KeyError) as e:
            crt.Dialog.MessageBox("Error with NUMBER column: {}".format(str(e)))
            return
        if number_column != sorted(number_column):
            crt.Dialog.MessageBox("Please sort NUMBER column in numerical order.")
            return
        valid_prompts = [row['PROMPT'].strip() for row in rows]
        start_index = check_marker()
        main_loop(start_index)
    except ScriptStoppedException:
        crt.Dialog.MessageBox("Script stopped by user.")
    finally:
        crt.Screen.Synchronous = False

def main_loop(start_index):
    global rows
    last_processed_row = None
    for index, row in enumerate(rows[start_index:], start=start_index):
        prompt, data = row['PROMPT'].strip(), row['DATA']
        if not prompt:
            crt.Dialog.MessageBox("Encountered empty prompt. Stopping script.")
            update_marker()
            break
        try:
            if wait_for_prompt_and_send_data(prompt, data, index):
                last_processed_row = row
        except ScriptStoppedException:
            raise
        except Exception as e:
            handle_unknown_prompt(prompt, data, e, index)
            break
    if last_processed_row and last_processed_row['PROMPT'].strip() == "FINISHED":
        crt.Screen.Synchronous = False
        return
    update_marker(last_processed_row)
    crt.Screen.Synchronous = False

def handle_unknown_prompt(active_prompt, expected_prompt, data, current_index):
    global history, rows, valid_prompts
    current_row = rows[current_index]
    message = ("Unknown prompt encountered. Please choose an option:\n\n"
               "On-Screen Prompt: {}\nExpected Prompt: {}\n\nChoose a selection:\n\n"
               "1. Enter Key\n2. Clear data next to prompt\n3. Show the last 6 data entries\n4. Show the next 6 data entries\n5. Enter data manually\n6. Stop the script\n7. Wait (10 seconds)").format(
               active_prompt, expected_prompt)
    user_option = crt.Dialog.Prompt(message, "Unknown Prompt Options", "1")
    if user_option == "1":
        send_special_command("ENTER")
        record_history(expected_prompt, "ENTER")
        main_loop(start_index=current_index + 1)
    elif user_option == "2":
        send_special_command("CLEAR")
        main_loop(start_index=current_index)
    elif user_option == "3":
        show_last_six_entries(current_index)
    elif user_option == "4":
        show_next_six_entries(current_index)
    elif user_option == "5":
        manual_data = crt.Dialog.Prompt("Enter Data:", "Manual Data Entry")
        if manual_data is not None:
            send_command(manual_data)
            record_history(expected_prompt, manual_data)
            main_loop(start_index=current_index + 1)
        else:
            handle_unknown_prompt(active_prompt, expected_prompt, data, current_index)
    elif user_option == "6":
        update_marker(rows[current_index])
        raise ScriptStoppedException("Script stopped by user.")
    elif user_option == "7":
        time.sleep(10)
        handle_unknown_prompt(active_prompt, expected_prompt, data, current_index)

def show_last_six_entries(current_index):
    global history, rows
    last_six_entries = history[-6:] if len(history) >= 6 else history
    message = ("Choose a selection:\n\n"
               "{}\n6. Return to main menu").format(
               "\n".join(["{}. {}: {}".format(i + 1, entry.split(", Data: ")[0][8:], entry.split(", Data: ")[1]) for i, entry in enumerate(last_six_entries)]))
    user_option = crt.Dialog.Prompt(message, "Last 6 Data Entries", "1")
    if user_option in ["1", "2", "3", "4", "5", "6"]:
        selected_index = current_index + int(user_option) - 1
        if selected_index < len(rows):
            next_row = rows[selected_index]
            wait_for_prompt_and_send_data(next_row['PROMPT'].strip(), next_row['DATA'], selected_index)
            main_loop(start_index=selected_index + 1)
    elif user_option == "6":
        handle_unknown_prompt(rows[current_index]['PROMPT'].strip(), rows[current_index]['PROMPT'].strip(), rows[current_index]['DATA'], None, current_index)

def show_next_six_entries(current_index):
    global rows
    next_six_entries = rows[current_index:current_index + 6]
    message = ("Choose a selection:\n\n"
               "{}\n6. Return to main menu").format(
               "\n".join(["{}. {}: {}".format(i + 1, row['PROMPT'].strip(), row['DATA']) for i, row in enumerate(next_six_entries)]))
    user_option = crt.Dialog.Prompt(message, "Next 6 Data Entries", "1")
    if user_option in ["1", "2", "3", "4", "5", "6"]:
        selected_index = current_index + int(user_option) - 1
        if selected_index < len(rows):
            next_row = rows[selected_index]
            wait_for_prompt_and_send_data(next_row['PROMPT'].strip(), next_row['DATA'], selected_index)
            main_loop(start_index=selected_index + 1)
    elif user_option == "6":
        handle_unknown_prompt(rows[current_index]['PROMPT'].strip(), rows[current_index]['PROMPT'].strip(), rows[current_index]['DATA'], None, current_index)

def update_marker(last_processed_row=None):
    global rows, file_path
    if last_processed_row:
        error_index = rows.index(last_processed_row)
        if error_index > 0:
            rows[error_index - 1]['MARKER'] = 'LAST_PROCESSED'
        else:
            rows[error_index]['MARKER'] = 'LAST_PROCESSED'
        for row in rows:
            if row != last_processed_row and rows.index(row) != error_index - 1:
                row['MARKER'] = ''
        write_csv(file_path, rows)

main()