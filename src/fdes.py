#!/usr/bin/env python

import os
import argparse
import sqlite3
import configparser
from sqlite3 import Error
from prettytable import PrettyTable

conn = None
c = None	

def get_desc(filename):
  global c
  try:
    c.execute('''SELECT description FROM fdescriptions WHERE filename=?''', (filename,))
    rows = c.fetchall()
    for row in rows:
      print(row[0])
  except Error as e:
    print(e)

def set_desc(filename):
  global c
  desc = input("Enter file description: ")
  try:
    c.execute('''INSERT INTO fdescriptions (filename, description) VALUES (?, ?)''', (filename, desc,))
  except Error as e:
    print(e)

def remove_desc(filename):
  global c
  try:
    c.execute('''DELETE  FROM fdescriptions WHERE filename=?''', (filename,))
  except Error as e:
    print(e)

def cleanup_db():
  global c
  try:
    c.execute('''SELECT * FROM  fdescriptions''')
    rows = c.fetchall()
    for row in rows:
      if not os.path.exists(row[0]):
        c.execute('''DELETE  FROM fdescriptions WHERE filename=?''', (row[0],))
        print('Removed description for deleted file', row[0])
  except Error as e:
    print(e)

def list_all():
  global c
  table =  PrettyTable()
  table.field_names = ["File Name", "Description"]
  try:
    c.execute('''SELECT * FROM  fdescriptions''')
    rows = c.fetchall()
    for row in rows:
      table.add_row([row[0],row[1]])
    print(table)
  except Error as e:
    print(e)

FUNCTION_MAP = {'get' : get_desc, 'set' : set_desc, 'remove': remove_desc, 'cleanup' : cleanup_db, 'listall': list_all}

def main():
  global conn
  global c
  parser = argparse.ArgumentParser()
  parser.add_argument('command', choices=FUNCTION_MAP.keys())
  parser.add_argument('-f', '--file', type=str,  help="File name")
  args = parser.parse_args()

  config = configparser.ConfigParser()
  config.read_file(open(os.path.expanduser('~/.fdesrc')))
  dbpath = config.get('default','db')

  try:
      conn = sqlite3.connect(os.path.expanduser(dbpath))
      c = conn.cursor()
      c.execute('''CREATE TABLE IF NOT EXISTS fdescriptions (filename TEXT PRIMARY KEY, description TEXT)''')
      func = FUNCTION_MAP[args.command]
      if args.command == 'cleanup' or args.command == 'listall':
        func()
      else:
        filename = os.path.abspath(args.file)
        func(filename)
      conn.commit()
  except Error as e:
        print(e)
  finally:
    if conn:
      conn.close()

main()
