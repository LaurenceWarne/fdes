#!/usr/bin/env python3

import os
import argparse
import sqlite3
import configparser
from prettytable import PrettyTable


def get_desc(cursor, filename):
    cursor.execute(
        '''SELECT description
        FROM fdescriptions
        WHERE filename = ?''', (filename,)
    )
    for (description,) in cursor:
        print(description)


def set_desc(cursor, filename):
    desc = input("Enter file description: ")
    cursor.execute(
        '''INSERT INTO fdescriptions (filename, description)
        VALUES (?, ?)''', (filename, desc,)
    )


def remove_desc(cursor, filename):
    cursor.execute(
        '''DELETE FROM fdescriptions WHERE filename = ?''', (filename, )
    )

def remove_all_dir(cursor, filename):
    cursor.execute(
        '''DELETE FROM fdescriptions WHERE filename LIKE ?''', (filename+"%", )
    )


def copy_desc(cursor, filename, newfile):
    cursor.execute(
        '''INSERT INTO fdescriptions (filename, description)
        SELECT ?, description
        FROM fdescriptions
        WHERE filename = ?''', (newfile, filename,)
    )


def cleanup_db(cursor):
    cursor.execute('''SELECT filename FROM fdescriptions''')
    for (filename, ) in cursor:
        if not os.path.exists(filename):
            cursor.execute(
                '''DELETE  FROM fdescriptions
                WHERE filename=?''', (filename, )
            )
            print('Removed description for deleted file', filename)


def list_all(cursor):
    table = PrettyTable()
    table.field_names = ["File Name", "Description"]
    cursor.execute('''SELECT filename, description FROM  fdescriptions''')
    for (filename, description,) in cursor:
        table.add_row((filename, description,))
    print(table)


def create_default_config_file(filename):
    default_config = configparser.ConfigParser()
    default_config.add_section('default')
    default_config.set('default', 'db', '~/.local/share/fdes/fdes.db')
    directory, _ = os.path.split(filename)
    directory = os.path.expanduser(directory)

    if (not os.path.exists(directory)):
        os.makedirs(directory)
    with open(os.path.expanduser(filename), 'w') as f:
        default_config.write(f)
    return default_config


FUNCTION_MAP = {
    'get': get_desc,
    'set': set_desc,
    'remove': remove_desc,
    'removedir': remove_all_dir,
    'cleanup': cleanup_db,
    'listall': list_all,
    'copy': copy_desc
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=FUNCTION_MAP.keys())
    parser.add_argument('-f', '--file', type=str,  help="File name")
    parser.add_argument(
        '-d',
        '--destination',
        type=str, help="File name path to copy a description to."
    )
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config_location = '~/.config/fdes/fdesrc'
    try:
        config.read_file(open(os.path.expanduser(config_location)))
    except FileNotFoundError:
        # Create config file
        print("Creating a default config file at: " + config_location)
        config = create_default_config_file(config_location)

    full_path = config.get('default', 'db')
    dbpath, _ = os.path.split(full_path)
    dbpath = os.path.expanduser(dbpath)
    if (not os.path.exists(dbpath)):
        os.makedirs(dbpath)

    with sqlite3.connect(os.path.expanduser(full_path)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS
            fdescriptions (filename TEXT PRIMARY KEY, description TEXT)'''
        )
        func = FUNCTION_MAP[args.command]
        if args.command == 'cleanup' or args.command == 'listall':
            func(cursor)
        elif args.command == 'copy':
            filename = os.path.abspath(args.file)
            newfile = os.path.abspath(args.destination)
            func(cursor, filename, newfile)
        else:
            filename = os.path.abspath(args.file)
            func(cursor, filename)
            connection.commit()


if __name__ == "__main__":
    main()
