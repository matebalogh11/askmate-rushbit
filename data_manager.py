import base64
import csv
from copy import deepcopy

# This module is for import only!


def write_csv(file, data):

    copied_data = deepcopy(data)
    with open(file, "w", newline="") as text:
        writer = csv.writer(text)
        for i, items in enumerate(copied_data):
            for n, details in enumerate(items):
                if n == 4 or n == 5 or n == 6:
                    old_string_obj = copied_data[i][n]
                    byte_obj = bytearray(old_string_obj, "utf-8")
                    base64_obj = base64.b64encode(byte_obj)
                    new_string_obj = base64_obj.decode("utf-8")
                    copied_data[i][n] = new_string_obj
        for story in copied_data:
            writer.writerow(story)


def read_csv(file):

    csv_type = True if file == "question.csv" else False
    with open(file, "r") as text:
        reader = csv.reader(text)
        requested_data = list(reader)
        if csv_type:
            for n, data in enumerate(requested_data):
                for i, items in enumerate(data):
                    if i == 1:
                        requested_data[n][i] = float(requested_data[n][i])
                    if i == 2 or i == 3 or i == 7:
                        requested_data[n][i] = int(requested_data[n][i])
                    if i == 4 or i == 5 or i == 6:
                        requested_data[n][i] = base64.b64decode(requested_data[n][i]).decode("utf-8")
        else:
            for n, data in enumerate(requested_data):
                for i, items in enumerate(data):
                    if i == 1:
                        requested_data[n][i] = float(requested_data[n][i])
                    if i == 2:
                        requested_data[n][i] = int(requested_data[n][i])
                    if i == 4 or i == 5 or i == 6:
                        requested_data[n][i] = base64.b64decode(requested_data[n][i]).decode("utf-8")
    return requested_data
