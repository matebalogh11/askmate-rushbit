
import base64
import csv
from copy import deepcopy
import config
import psycopg2


def write_csv(file, data):
    """Write 2d list into CSV file, overwriting existing content."""
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
    """Read CSV file and return 2d list."""
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


def connect_db(func):
    def wrapper(query_args):
        """Return connection object if established. Set autocommit to True."""
        DNS = "dbname='{}' host='{}' user='{}' password='{}'".format(config.DB, config.HOST, config.USER, config.PW)
        try:
            conn = psycopg2.connect(DNS)
            conn.autocommit = True
        except Exception as e:
            print("Cannot connect. Invalid credentials.")
            print(e, end='')
        else:
            print("Connected to database '{}' on '{}' as user '{}'.".format(config.DB, config.HOST, config.USER))
            result = func(conn, query_args)
            return result
        finally:
            if conn:
                conn.close()
    return wrapper


@connect_db
def get_questions(conn, query_args):
    """Return questions list for list.html"""
    columns = query_args.get("columns")
    SQL = """SELECT {},{},{},{},{},{} FROM {} ORDER BY {} {};""".format(columns[0],
                                                                        columns[1],
                                                                        columns[2],
                                                                        columns[3],
                                                                        columns[4],
                                                                        columns[5],
                                                                        query_args.get("table"),
                                                                        query_args.get("criterium"),
                                                                        query_args.get("order"))
    with conn.cursor() as cursor:
        cursor.execute(SQL)
        result = cursor.fetchall()
    #     column_names = [desc[0] for desc in cursor.description]
    # result.insert(0, column_names)
    return result
