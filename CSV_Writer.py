import csv

def write_csv_headers(temp_csv_file, csv_headers):
    writer = csv.writer(temp_csv_file, delimiter=',')
    writer.writerow(csv_headers)

def append_to_csv(temp_csv_file, row_counter, c40_list, master_sn_list, child_sn_list, from_lpn_textbox, master_part_textbox, question1_checkbox, child_parts_layout, num_builds):
    from_lpn = from_lpn_textbox.text() if not from_lpn_textbox.isReadOnly() else None
    master_part = master_part_textbox.text() if master_part_textbox.isVisible() else None
    with open(temp_csv_file.name, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        for i in range(num_builds):
            if from_lpn:
                writer.writerow([row_counter, "From LPN   :", "FromLPN", from_lpn])
                row_counter += 1
                from_lpn = None  # Ensure LPN is only written once per batch
            writer.writerow([row_counter, "SEND", "C40", c40_list[i % len(c40_list)] if c40_list else f"C40-{7812765 + i}"])
            row_counter += 1
            if question1_checkbox.isChecked() and master_part:
                writer.writerow([row_counter, "Item       >", "MasterPart1", master_part])
                row_counter += 1
                writer.writerow([row_counter, "Qty        :", "QuantityM1", 1])
                row_counter += 1
                # Write serial number as a string to preserve leading zeros
                writer.writerow([row_counter, "SN         >", "SerialM1", str(master_sn_list[i % len(master_sn_list)]) if master_sn_list else f"0F36XMQ24423K{i+3}"])
                row_counter += 1
                writer.writerow([row_counter, "<Save/Next>", "BLANK", ""])
                row_counter += 1
            for j in range(child_parts_layout.count()):
                child_part_layout = child_parts_layout.itemAt(j).layout()
                writer.writerow([row_counter, "Item       >", f"ChildPart{j+1}:", child_part_layout.itemAt(1).widget().text()])
                row_counter += 1
                writer.writerow([row_counter, "Qty        :", f"QuantityP{j+1}:", child_part_layout.itemAt(3).widget().text()])
                row_counter += 1
                if child_sn_list[j]:
                    sn_count = int(child_part_layout.itemAt(3).widget().text())  # Get quantity to determine how many SNs to write
                    sn_list = child_sn_list[j][i*sn_count:(i+1)*sn_count]  # Slice the SN list for the current build
                    # Write child serial numbers as strings to preserve leading zeros
                    writer.writerow([row_counter, "SN         >", f"SerialP{j+1}:", ", ".join(map(str, sn_list))])
                    row_counter += 1
                writer.writerow([row_counter, "<Save/Next>", "BLANK", ""])
                row_counter += 1
            # Add UPARROW row after each build
            writer.writerow([row_counter, "UPARROW", "UPARROW", ""])
            row_counter += 1
    return row_counter

def read_csv(temp_csv_file):
    with open(temp_csv_file.name, 'r') as file:
        reader = csv.reader(file)
        return list(reader)

def append_finished(temp_csv_file, row_counter):
    with open(temp_csv_file.name, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow([row_counter, "FINISHED", "", ""])

def save_csv(file_name, temp_csv_file, csv_headers):
    with open(temp_csv_file.name, 'r') as temp_file, open(file_name, 'w', newline='') as file:
        reader = csv.reader(temp_file)
        writer = csv.writer(file, delimiter=',')
        writer.writerow(csv_headers)
        for row in reader:
            writer.writerow(row)