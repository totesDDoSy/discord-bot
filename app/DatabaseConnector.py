"""
DatabaseConnector.py - A file to control the sqlite database connection

@author Cody Sanford <cody.b.sanford@gmail.com>
@date 2020-08-29
"""
import sqlite3
from sqlite3 import Error
from typing import Union


class db_conn:
    """
    A context manager for the sqlite database connection
    """
    def __init__(self, db_file=r'../db/pythonsqlite.db'):
        self.db_file = db_file

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


class BotDatabase:
    """
    Database logic for the Discord bot
    """
    def __init__(self, db_file=r'../db/pythonsqlite.db'):
        """
        :param db_file: The file the database is in.
        This init is here to make sure the tables are in place and that the minimum data is populated
        """
        self.db_file = db_file
        create_su_table_sql = """ CREATE TABLE IF NOT EXISTS admins (
                                    id integer PRIMARY KEY,
                                    user_id integer UNIQUE
                              ); """
        create_text_commands_sql = """ CREATE TABLE IF NOT EXISTS text_commands (
                                        id integer PRIMARY KEY,
                                        command_name text UNIQUE,
                                        response text NOT NULL,
                                        admin integer NOT NULL DEFAULT 0
                                    ); """
        insert_self_sql = """ INSERT OR IGNORE INTO admins (user_id) VALUES (?)"""
        with db_conn(self.db_file) as c:
            # Create tables
            c.execute(create_su_table_sql)
            c.execute(create_text_commands_sql)

            # Initial data population
            c.execute(insert_self_sql, ['170045009318510593'])

    def add_admin(self, user_id: Union[str, int]):
        """
        Add an admin user to the database
        :param user_id: User ID from Discord - Unique
        :return:
        """
        insert_admin_sql = """ INSERT INTO admins (user_id) VALUES (?)"""
        with db_conn(self.db_file) as c:
            c.execute(insert_admin_sql, [user_id])

    def add_text_command(self, command_name: str, response: str, admin: bool):
        """
        Add a Text command to the database
        :param command_name: Command name - Unique
        :param response: Text response for the command
        :param admin: Whether or not the command is restricted to admins
        :return:
        """
        insert_text_command_sql = """ INSERT INTO text_commands (command_name, response, admin) VALUES (?,?,?)"""
        with db_conn(self.db_file) as c:
            c.execute(insert_text_command_sql, (command_name, response, admin))

    def delete_admin(self, user_id: Union[str, int]):
        """
        Delete a user from the admins table
        :param user_id: Discord User ID
        :return:
        """
        delete_admin_sql = """ DELETE FROM admins WHERE user_id = ?"""
        with db_conn(self.db_file) as c:
            c.execute(delete_admin_sql, [user_id])

    def delete_text_command(self, command_name: str):
        """
        Delete a text command from the text_commands table
        :param command_name: Name of the text command
        :return:
        """
        delete_text_command_sql = """ DELETE FROM text_commands WHERE command_name = ?"""
        with db_conn(self.db_file) as c:
            c.execute(delete_text_command_sql, [command_name])

    def get_all_text_commands(self, include_admin=False):
        """
        Get all available text commands
        :param include_admin: Whether or not to include admin restricted commands
        :return:
        """
        select_all_text_commands_sql = """ SELECT * FROM text_commands """
        if not include_admin:
            select_all_text_commands_sql += """ WHERE admin = 0 """
        with db_conn(self.db_file) as c:
            c.execute(select_all_text_commands_sql)
            rows = c.fetchall()
            return rows

    def find_text_command(self, name: str, admin=False):
        """
        Find a specific text command
        :param name: Name of the text command
        :param admin: Whether to include admin restricted commands
        :return:
        """
        select_text_command_sql = """ SELECT command_name, response FROM text_commands
                                    WHERE command_name=?  """
        if not admin:
            select_text_command_sql += """ AND admin=0 """
        with db_conn(self.db_file) as c:
            c.execute(select_text_command_sql, [name])
            row = c.fetchone()
            if row:
                row = {'command_name': row[0], 'response': row[1]}
            return row

    def is_user_admin(self, user_id: Union[str, int]):
        """
        Check if a user exists in the admins table
        :param user_id: Discord User ID
        :return:
        """
        select_admin_sql = """ SELECT * FROM admins WHERE user_id=? """
        with db_conn(self.db_file) as c:
            c.execute(select_admin_sql, [user_id])
            return bool(c.fetchone())


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins')
        rows = cursor.fetchall()
        print('admin')
        print('==========================')
        for row in rows:
            print(row)
        cursor.execute('SELECT * FROM text_commands')
        rows = cursor.fetchall()
        print()
        print('text_commands')
        print('==============================================================')
        print('| id | command_name | response                      | admin |')
        print('==============================================================')
        for row in rows:
            print(row)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    # create_connection('../db/pythonsqlite.db')
    db = BotDatabase()
    print(db.find_text_command('test', True))
