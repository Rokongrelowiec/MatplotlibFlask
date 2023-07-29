import pandas as pd
import sqlite3

def process_data(create_db):
    
    conn = sqlite3.connect('local.db')
    cursor = conn.cursor()

    if create_db:
        data = pd.read_excel('proportion_urban.xlsx')
        data = data.drop(columns=['Index', 'Note', 'Country\ncode'])

        data.columns = [data.columns.values[0].split(',')[0], *data.columns.values[1:]]

        num = [f'"{i}" integer' for i in range(1950, 2055, 5)]

        create_table_command = "CREATE TABLE URBAN (Region text"

        for item in range(len(num)):
            create_table_command += f', {num[item]}'
        else:
            create_table_command += ')'

        cursor.execute(create_table_command)

        executemany_commant = "INSERT INTO URBAN VALUES ("
        for _ in range(len(num) + 1):
            executemany_commant += '?,'
        else:
            executemany_commant = executemany_commant[:-1] + ')'

        row_tuple = data.apply(lambda row: tuple(row), axis=1).tolist()
        cursor.executemany(executemany_commant, row_tuple)

        conn.commit()


    lst = []
    for row in cursor.execute('SELECT Region FROM URBAN'):
        lst.append(row[0])

    conn.close()

    return lst
