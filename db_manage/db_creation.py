import mysql.connector


def create_database_local_connection():

    database_connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        passwd="lapa2174",
        database="knifes_v2",
    )

    cursor = database_connection.cursor()

    return database_connection, cursor


def create_local_database():

    database_connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        passwd="lapa2174",
    )

    cursor = database_connection.cursor()

    cursor.execute("Create DATABASE `knifes_v2`")


def create_knifes_table():
    database_con, cursor = create_database_local_connection()

    create_base_accounts_table_query = "CREATE TABLE `knifes` (" \
                                       "id int AUTO_INCREMENT PRIMARY KEY," \
                                       "link varchar(256)," \
                                       "cost varchar(128)," \
                                       "datetime date" \
                                       ")"
    cursor.execute(create_base_accounts_table_query)
    cursor.close(),
    database_con.close()


if __name__ == "__main__":
    create_local_database()
    create_knifes_table()