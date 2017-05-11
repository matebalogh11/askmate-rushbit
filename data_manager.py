import base64
import csv

# This module is for import only!


def write_csv(file, data):

    with open(file, "w", newline="") as text:
        writer = csv.writer(text)
        for i, items in enumerate(data):
            for n, details in enumerate(items):
                if n == 4 or n == 5 or i == 6:
                    data[i][n] = base64.b64encode(bytes(data[i][n], "utf-8")).decode("utf-8")
        for story in data:
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
                    if i == 2 or i == 3:
                        requested_data[n][i] = int(requested_data[n][i])
                    if i == 4 or i == 5 or i == 6:
                        requested_data[n][i] = base64.b64decode(requested_data[n][i]).decode("utf-8")
        else:
            for n, data in enumerate(requested_data):
                for i, items in enumerate(data):
                    if i == 1:
                        requested_data[n][i] = float(requested_data[n][i])
                    if i == 0 or i == 2:
                        requested_data[n][i] = int(requested_data[n][i])
                    if i == 4 or i == 5 or i == 6:
                        requested_data[n][i] = base64.b64decode(requested_data[n][i]).decode("utf-8")
    return requested_data
