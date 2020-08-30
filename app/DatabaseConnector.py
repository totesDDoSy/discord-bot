"""
DatabaseConnector.py - A file to control the sqlite database connection

@author Cody Sanford <cody.b.sanford@gmail.com>
@date 2020-08-29
"""
import sqlite3
from sqlite3 import Error
from typing import Union, List


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
                                        command_name text NOT NULL UNIQUE,
                                        response text NOT NULL,
                                        admin integer NOT NULL DEFAULT 0
                                    ); """
        create_role_commands_sql = """ CREATE TABLE IF NOT EXISTS role_commands (
                                        id integer PRIMARY KEY,
                                        command_name text NOT NULL UNIQUE
                                    );"""
        create_roles_sql = """ CREATE TABLE IF NOT EXISTS roles (
                                id integer PRIMARY KEY,
                                role_id integer NOT NULL UNIQUE,
                                role_command_id integer NOT NULL,
                                FOREIGN KEY(role_command_id) REFERENCES role_commands(id)
                           );"""

        insert_self_sql = """ INSERT OR IGNORE INTO admins (user_id) VALUES (?)"""

        with db_conn(self.db_file) as c:
            # Create tables
            c.execute(create_su_table_sql)
            c.execute(create_text_commands_sql)
            c.execute(create_role_commands_sql)
            c.execute(create_roles_sql)

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

    def find_role_command(self, command_name):
        select_role_command_sql = """ SELECT id, command_name FROM role_commands 
                                    WHERE command_name=? """
        select_roles_sql = """ SELECT role_id FROM roles WHERE role_command_id=? """
        with db_conn(self.db_file) as c:
            c.execute(select_role_command_sql, [command_name])
            try:
                role_command_id, cmd_name = c.fetchone()
                c.execute(select_roles_sql, [role_command_id])
                role_list = c.fetchall()
                return [role[0] for role in role_list]
            except TypeError as e:
                print(e)
                return None

    def add_role_command(self, command_name: str, roles: List[int]):
        insert_role_command_sql = """ INSERT INTO role_commands (command_name) VALUES (?) """
        insert_role_sql = """ INSERT INTO roles (role_id, role_command_id) VALUES (?, ?) """
        with db_conn(self.db_file) as c:
            c.execute(insert_role_command_sql, [command_name])
            row_id = c.lastrowid
            for role_id in roles:
                c.execute(insert_role_sql, (role_id, row_id))

    def delete_role_command(self, command_name: str):
        delete_roles_sql = """ DELETE FROM roles WHERE role_command_id = ? """
        delete_role_command_sql = """ DELETE FROM role_commands WHERE command_name = ? """
        select_role_command_id = """ SELECT id FROM role_commands WHERE command_name = ? """
        with db_conn(self.db_file) as c:
            c.execute(select_role_command_id, [command_name])
            row_id = c.fetchone()[0]
            c.execute(delete_roles_sql, [row_id])
            c.execute(delete_role_command_sql, [command_name])

    def get_all_role_commands(self):
        select_all_role_commands_sql = """ SELECT * FROM role_commands """
        with db_conn(self.db_file) as c:
            c.execute(select_all_role_commands_sql)
            return c.fetchall()

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
    print(db.get_all_role_commands())
    print(db.find_role_command('roe'))

    # with db_conn('../db/pythonsqlite.db') as cursor:
    #     cursor.execute(""" SELECT * FROM admins """)
    #     print(cursor.fetchall())
    #     cursor.execute(""" SELECT * FROM text_commands """)
    #     print('\n'.join([str(row) for row in cursor.fetchall()]))
    #     cursor.execute(""" SELECT * FROM role_commands """)
    #     print(cursor.fetchall())
    #     cursor.execute(""" SELECT * FROM roles """)
    #    print(cursor.fetchall())
