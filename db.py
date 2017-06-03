
import config
import psycopg2


def run_statements(SQL_data_fetch_trios):
    """Run statement(s) and fetch result-set(s) on demand.
    @SQL_data_fetch_trios tuple: contains tuples of 3:
    1. SQL query string, 2. tuple of parameters, 3. boolean.
    @return list: if fetch == 'all' then appends a list of tuple(s),
    elif fetch == 'one' then appends a tuple.
    """
    conn = None
    try:
        conn = psycopg2.connect(config.DNS)
    except psycopg2.OperationalError as oe:
        print("Could NOT connect to database.")
        print(oe)
    else:
        conn.autocommit = True
        with conn.cursor() as cursor:
            result = []
            for SQL, data, fetch in SQL_data_fetch_trios:
                if data:
                    cursor.execute(SQL, data)
                else:
                    cursor.execute(SQL)
                if fetch == "all":
                    result.append(cursor.fetchall())
                elif fetch == "one":
                    result.append(cursor.fetchone())
                elif fetch == "col":
                    result.append([row[0] for row in cursor])
        if result:
            return result
    finally:
        if conn:
            conn.close()
