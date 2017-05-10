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

    x = 1 if file == "question.csv" else 0
    with open(file, "r") as text:
        reader = csv.reader(text)
        requested_data = list(reader)
        for n, data in enumerate(requested_data):
            for i, items in enumerate(data):
                if i == x or i == x+1 or i == x+2:
                    requested_data[n][i] = int(requested_data[n][i])
                if i == 4 or i == 5 or i == 6:
                    requested_data[n][i] = base64.b64decode(requested_data[n][i]).decode("utf-8")

    return requested_data
