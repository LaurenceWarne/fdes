#!/usr/bin/env python3

import os
import argparse
import sqlite3
import configparser
from sqlite3 import Error
from prettytable import PrettyTable


def get_desc(cursor, filename):
    cursor.execute('''SELECT description FROM fdescriptions WHERE filename = ?''', (filename,))
    for (description,) in cursor:
      print(description)


def set_desc(cursor, filename):
  desc = input("Enter file description: ")
  cursor.execute('''INSERT INTO fdescriptions (filename, description) VALUES (?, ?)''', (filename, desc,))


def remove_desc(cursor, filename):
    cursor.execute('''DELETE FROM fdescriptions WHERE filename = ?''', (filename,))


def copy_desc(cursor, filename, newfile):
    cursor.execute('''INSERT INTO fdescriptions (filename, description) SELECT ?, description FROM fdescriptions WHERE filename = ?''', (newfile, filename,))


def cleanup_db(cursor):
    cursor.execute('''SELECT filename FROM fdescriptions''')
    for (filename, ) in cursor:
      if not os.path.exists(filename):
        cursor.execute('''DELETE  FROM fdescriptions WHERE filename=?''', (filename,))
        print('Removed description for deleted file', filename)


def list_all(cursor):
  table =  PrettyTable()
  table.field_names = ["File Name", "Description"]
  cursor.execute('''SELECT filename, description FROM  fdescriptions''')
  for (filename, description,) in cursor:
      table.add_row((filename, description,))
  print(table)


FUNCTION_MAP = {'get' : get_desc, 'set' : set_desc, 'remove': remove_desc, 'cleanup' : cleanup_db, \
               'listall' : list_all, 'copy' : copy_desc}

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('command', choices=FUNCTION_MAP.keys())
  parser.add_argument('-f', '--file', type=str,  help="File name")
  parser.add_argument('-d', '--destination', type=str, help="File name path to copy a description to.")
  args = parser.parse_args()

  config = configparser.ConfigParser()
  config.read_file(open(os.path.expanduser('~/.fdesrc')))
  dbpath = config.get('default','db')

  with sqlite3.connect(os.path.expanduser(dbpath)) as connection:
      cursor = connection.cursor()
      cursor.execute('''CREATE TABLE IF NOT EXISTS fdescriptions (filename TEXT PRIMARY KEY, description TEXT)''')
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


main()
