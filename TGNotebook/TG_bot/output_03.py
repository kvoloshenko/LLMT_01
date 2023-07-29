import sys
import datetime

def output2file_on():
    # Get the current date and time
    current_datetime = datetime.datetime.now()

    # Format the date and time as a string
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    # Specify the desired suffix for the file
    suffix = "_log.txt"

    # Combine the formatted date and time with the suffix
    filename = formatted_datetime + suffix

    # Open the file in write mode
    sys.stdout = open(filename, 'w')

def output2file_off():
    # Reset the standard output to the console
    sys.stdout = sys.__stdout__

# Usage
# output2file_on()

# Print statements will now be written to the file
# print("This string will be written to the file")

# output2file_off()

# The rest of your code can continue writing to the console
# print("This will be displayed on the console")