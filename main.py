import re
import os
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from receipt_checker import ReceiptEntryList, ReceiptEntryNode

def build_list_from_file(file):
    receipt = ReceiptEntryList()

    try:
        contents = file.read()
        ctr = 0
        for value in contents.splitlines():
            splitted_value = value.split()
            check_line_length(ctr, splitted_value, value)

            if ctr == 0:
                check_header_line(ctr, splitted_value, value)
                receipt.receipt_number = splitted_value[0]
                receipt.date = splitted_value[1]
                receipt.time = splitted_value[2]
            else:
                check_receipt_entry(ctr, splitted_value, value)
                new_node = ReceiptEntryNode(splitted_value[0], splitted_value[1], float(splitted_value[2][1:]))

                if receipt.head is None:
                    receipt.head = new_node
                    receipt.tail = new_node
                else:
                    receipt.tail.next_node = new_node
                    new_node.previous_node = receipt.tail
                    receipt.tail = new_node
            ctr += 1
    except FileNotFoundError:
        print("ERROR: INPUT.txt was not found in the working directory of this script file. Please ensure that the file exists and has the correct filename and file extension.")
        exit(0)

    return receipt

def create_list_from_user(self):
    ctr = 1
    while True:
        print("\nEntry #", ctr, sep="")
        while True:
            item_name = str(input("Enter item name without spaces: "))
            if re.search(r"\s", item_name):
                (print("\nINVALID: Please ensure item name has no spaces."))
            else:
                break
        while True:
            quantity = str(input("Enter quantity:"))
            if re.search(r"^(?!0+(?:\.0+)?(?:g|kg|mL|L)?$)([1-9]\d*|0)(\.\d+(g|kg|mL|L))?(g|kg|mL|L)?$", quantity):
                break
            else:
                print("\nERROR: Invalid quantity. Quantity must be a positive integer (1 and above) or a combination of positive integer/floating number and a unit (i.e., g, kg, mL, or L).")
        while True:
            unit_price = str(input("Enter unit price: "))
            if re.search(r"^P(?:\d+)?(?:\.\d+)?$", unit_price):
                break
            else:
                print("\nERROR: Invalid unit price. Please ensure that it is in correct format (e.g., P250.46, P100.00)")

        new_node = ReceiptEntryNode(item_name, quantity, unit_price[1:])

        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next_node = new_node
            new_node.previous_node = self.tail
            self.tail = new_node

        while True:
            try:
                option = int(input("\nAdd more entry?\n1 = Yes\n2 = No\n\nEnter num: "))
                if option == 1:
                    break
                elif option == 2:
                    self.ask_confirmation()
            except ValueError:
                print("INVALID: Invalid value. Please enter a correct number.")

        ctr += 1

def check_line_length(ctr, splitted_value, value):
    if len(splitted_value) >= 4:
        if ctr == 0:
            print("ERROR: Multiple values found in the header line of text file. Please ensure that receipt number, date, and, time are the only values at the header line. Receipt registration will be cancelled.")
        else:
            print(f"ERROR: Multiple values found in the receipt entry placed at Line #{ctr + 1} ({value}) of text file. Please ensure that each line of receipt entry contains only the item name, quantity, and unit price. Receipt registration will be cancelled.")
        exit(0)
    elif len(splitted_value) <= 2:
        if ctr == 0:
            print("ERROR: Header line lacks at least one required values (i.e., receipt number, date, or, time). Receipt registration will be cancelled.")
            exit(0)
        else:
            if len(splitted_value) == 0:
                print(f"ERROR: Receipt entry at Line #{(ctr+1)} lacks at least one required values (i.e., item name, quantity, or unit price). Receipt registration will be cancelled.")
            else:
                print(f"ERROR: Receipt entry at Line #{(ctr+1)} ({value}) lacks at least one required values (i.e., item name, quantity, or unit price). Receipt registration will be cancelled.")
            exit(0)

def check_header_line(ctr, splitted_value, value):
    if ctr == 0:
        # Uses RegEx to check if it's a valid receipt number
        filtered_receipt_number = re.search(r"^\d{1}-\d{2}-\d{4}-\d{2}$", splitted_value[0])
        if filtered_receipt_number is None:
            print("ERROR: Invalid receipt number. Ensure that the receipt number is in correct format (i.e., x-xx-xxxx-xx, where x is a positive whole number). Receipt registration will be cancelled.")
            exit(0)
        
        # Uses datetime module to check if date is valid or not
        try:
            filtered_time = re.search(r"^([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$", splitted_value[2])
            if filtered_time is None:
                print("ERROR: Invalid date/time. The date and time is set in the future. Receipt registration will be cancelled.")
                exit(0)

            filtered_date = datetime.strptime(splitted_value[1] + " " + splitted_value[2], "%m/%d/%Y %H:%M:%S")
            current_date = datetime.now()

            if filtered_date > current_date:
                print("ERROR: Invalid date/time. The date and time is set in the future. Receipt registration will be cancelled.")
                exit(0)
        except ValueError:
            print("ERROR: Invalid date/time. Either date is not in proper MM/DD/YYYY format or time is not in HH:mm:SS format. Receipt registration will be cancelled.")
            exit(0)

def check_receipt_entry(ctr, splitted_value, value):
    filtered_item_name = re.search(r"^(\w+(_)?){1,}$", splitted_value[0])
    if filtered_item_name is None:
        print(f"ERROR: Invalid item name at Line #{(ctr + 1)} (>>>{splitted_value[0]}<<<, {splitted_value[1]}, {splitted_value[2]}). Item name must only include letters and numbers and can only be separated by underscore.")
        exit()
    
    splitted_item_name = splitted_value[0].split("_")
    splitted_value[0] = '_'.join(word.capitalize() for word in splitted_item_name)

    filtered_quantity = re.search(r"^(?!0+(?:\.0+)?(?:g|kg|mL|L)?$)([1-9]\d*|0)(\.\d+(g|kg|mL|L))?(g|kg|mL|L)?$", splitted_value[1])
    if filtered_quantity is None:
        print(f"ERROR: Invalid quantity at Line #{(ctr + 1)} ({splitted_value[0]}, >>>{splitted_value[1]}<<<, {splitted_value[2]}). Quantity must be a positive integer (1 and above) or a combination of positive integer/floating number and a unit (i.e., g, kg, mL, or L).")
        exit()
    
    filtered_unit_price = re.search(r"^P(?:\d+)?(?:\.\d+)?$", splitted_value[2])
    if filtered_unit_price is None:
        print(f"ERROR: Invalid unit price at Line #{(ctr + 1)} ({splitted_value[0]}, {splitted_value[1]}, >>>{splitted_value[2]}<<<). Ensure that it is in correct format (e.g., P250.46, P100.00)")
        exit()

def ask_confirmation(receipt_obj):
    display_entries(receipt_obj)
    while True:
        try:
            choosen_option = int(input("\nChoose what you want to do with the result:\n1 = Write the results into a file.\n2 = Sort the list by total price in descending order\n3 = Discard and exit the program.\n\nEnter num: "))

            if choosen_option == 1:
                write_receipt_output_file(receipt_obj)
                input("\nPress Enter to exit...")
                exit(0)
            elif choosen_option == 2:
                receipt_obj.sort_list()
            elif choosen_option == 3:
                print("The program will now exit.")
                input("\nPress Enter to exit...")
                exit(0)
        except ValueError:
            print("\nInvalid value. Please enter a correct number.")

def display_entries(receipt_obj):
    total_price = 0.0
    total_of_items = 0
    current = receipt_obj.head

    print("\nThis is the result of your receipt entry.\n\n--------------------")
    if receipt_obj.date and receipt_obj.time:
        formatted_date, formatted_time = get_formatted_date_and_time(receipt_obj.date, receipt_obj.time)
        print(f"{receipt_obj.receipt_number} {formatted_date} {formatted_time}")
    while current is not None:
        print(f"{current.entry.item_name} {current.entry.quantity} P{current.entry.unit_price:.2f} P{current.entry.total_price:.2f}")
        total_price += current.entry.total_price

        total_price = round_num(total_price)
        total_of_items += add_entry_quantity(current.entry.quantity)

        current = current.next_node

    if total_of_items > 1 or total_of_items == 0:
        item_string = "items"
    else:
        item_string = "item"
    print(f"P{total_price:.2f} {total_of_items}_{item_string}")
    print("--------------------")

def write_receipt_output_file(receipt_obj):
    while True:
        output = str(input("\nEnter the filename w/ \".txt\" in the end: "))
        if not re.search(r"^[\w\-. ]+$", output):
            print(r"ERROR: Invalid filename. Ensure that no illegal characters are used (i.e., \ / : * ? \" < > |)")
        elif os.path.exists(output):
            print(f"ERROR: File \"{output}\" already exist. Please use a different filename.")
        else:
            break

    with open(output, "w") as f:
        if receipt_obj.date and receipt_obj.time:
            formatted_date, formatted_time = get_formatted_date_and_time(receipt_obj.date, receipt_obj.time)
            f.write(f"{receipt_obj.receipt_number} {formatted_date} {formatted_time}\n")

        current = receipt_obj.head
        total_price = 0.0
        total_of_items = 0

        while current is not None:
            f.write(f"{current.entry.item_name} {current.entry.quantity} P{current.entry.unit_price:.2f} P{current.entry.total_price:.2f}\n")
            total_price += current.entry.total_price

            total_price = round_num(total_price)
            total_of_items += add_entry_quantity(current.entry.quantity)

            current = current.next_node
        
        if total_of_items > 1 or total_of_items == 0:
            item_string = "items"
        else:
            item_string = "item"

        f.write(f"P{total_price:.2f} {total_of_items}_{item_string}")
        print(f"\nSUCCESS: The results has been saved to \"{output}\"")

def get_formatted_date_and_time(date, time):
    # Parses the time and date stored from header line using datetime module
    date = datetime.strptime(receipt_obj.date, "%m/%d/%Y")
    time = datetime.strptime(receipt_obj.time, "%H:%M:%S")

    formatted_date = date.strftime("%Y/%m/%d")
    formatted_time = time.strftime("%I:%M:%S %p")

    return formatted_date, formatted_time

def add_entry_quantity(entry_quantity):
    # Since quantities with units are treated 1, they must be filtered here using RegEx
    filtered_quantity = re.search(r"^(?:0*[1-9][0-9]*)?(?:\.\d*|0+\.\d+)?(?:g|mL|L|kg)$", entry_quantity)
    if filtered_quantity:
        return 1
    else:
        return int(entry_quantity)

def round_num(value):
    num = Decimal(str(value))
    rounded_num = num.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return float(rounded_num)

if __name__ == "__main__":
    receipt_objects = []

    print("Welcome to ReceiptChecker!")
    print("Please choose a number on what you want to do:\n1 = Read from file\n2 = Enter entries manually\n3 = Exit\n\nEnter num: ")
    while True:
        try:
            choosen_num = int(input(">>> "))

            if choosen_num == 1:
                print("\nEnter the filename including its extension (e.g., data.txt): ")
                while True:
                    file = str(input(">>> "))
                    try:
                        with open(file, "r") as file:
                            receipt_obj = build_list_from_file(file)
                            ask_confirmation(receipt_obj)
                            input("\nPress Enter to exit...")
                            break
                    except FileNotFoundError:
                        print(f"\nERROR: {file} is not found.")
            elif choosen_num == 2:
                r = ReceiptEntryList()
                r.create_list_from_user()
                input("\nPress Enter to exit...")
                break
            elif choosen_num == 3:
                input("\nPress Enter to exit...")
                break
        except ValueError:
            print("\nInvalid value. Please enter a correct number.")
