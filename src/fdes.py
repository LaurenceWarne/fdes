#!/usr/bin/env python

import os
import argparse
import sqlite3
import configparser
from sqlite3 import Error
from prettytable import PrettyTable

connection = None
cursor = None

def get_desc(filename):
  global cursor
  try:
    cursor.execute('''SELECT description FROM fdescriptions WHERE filename=?''', (filename,))
    rows = cursor.fetchall()
    for row in rows:
      print(row[0])
  except Error as e:
    print(e)

def set_desc(filename):
  global cursor
  desc = input("Enter file description: ")
  try:
    cursor.execute('''INSERT INTO fdescriptions (filename, description) VALUES (?, ?)''', (filename, desc,))
  except Error as e:
    print(e)

def remove_desc(filename):
  global cursor
  try:
    cursor.execute('''DELETE  FROM fdescriptions WHERE filename=?''', (filename,))
  except Error as e:
    print(e)

def copy_desc(filename, newfile):
  global cursor
  try:
    cursor.execute('''INSERT INTO fdescriptions (filename, description) SELECT ?, description FROM fdescriptions WHERE filename = ?''', (newfile, filename,))
  except Error as e:
    print(e)

def cleanup_db():
  global cursor
  try:
    cursor.execute('''SELECT * FROM  fdescriptions''')
    rows = cursor.fetchall()
    for row in rows:
      if not os.path.exists(row[0]):
        cursor.execute('''DELETE  FROM fdescriptions WHERE filename=?''', (row[0],))
        print('Removed description for deleted file', row[0])
  except Error as e:
    print(e)

def list_all():
  global cursor
  table =  PrettyTable()
  table.field_names = ["File Name", "Description"]
  try:
    cursor.execute('''SELECT * FROM  fdescriptions''')
    rows = cursor.fetchall()
    for row in rows:
      table.add_row([row[0],row[1]])
    print(table)
  except Error as e:
    print(e)

FUNCTION_MAP = {'get' : get_desc, 'set' : set_desc, 'remove': remove_desc, 'cleanup' : cleanup_db, \
               'listall' : list_all, 'copy' : copy_desc}

def main():
  global connection
  global cursor
  parser = argparse.ArgumentParser()
  parser.add_argument('command', choices=FUNCTION_MAP.keys())
  parser.add_argument('-f', '--file', type=str,  help="File name")
  parser.add_argument('-d', '--destination', type=str, help="File name path to copy a description to.")
  args = parser.parse_args()

  config = configparser.ConfigParser()
  config.read_file(open(os.path.expanduser('~/.fdesrc')))
  dbpath = config.get('default','db')

  try:
      connection = sqlite3.connect(os.path.expanduser(dbpath))
      cursor = connection.cursor()
      cursor.execute('''CREATE TABLE IF NOT EXISTS fdescriptions (filename TEXT PRIMARY KEY, description TEXT)''')
      func = FUNCTION_MAP[args.command]
      if args.command == 'cleanup' or args.command == 'listall':
        func()
      elif args.command == 'copy':
        filename = os.path.abspath(args.file)
        newfile = os.path.abspath(args.destination)
        func(filename, newfile)
      else:
        filename = os.path.abspath(args.file)
        func(filename)
      connection.commit()
  except Error as e:
        print(e)
  finally:
    if connection:
      connection.close()

main()
