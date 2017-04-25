"""
● MEID ○ Mobile Equipment Identifier

● HW_TYPE ○ Hardware Type - Smartphone, Feature phone, Tablet, Module, etc.

● SKU ○ Network that the device was designed for (Sprint, Boost, etc.)

● STATUS ○ IN -- checked into inventory ○ OUT -- checked out of inventory for testing ○ ARCHIVED - the device is no longer at DVT&C

○ TesterName - name of the person who has the device ○ DVT Admin - the default owner when the device is still in inventory

● SERIAL NUMBER

● MSL/SPC	Serial No. 	MSL	Date Received	Date Returned	Barcode	Last Location with Date (mm/dd/yy)	Comment

"""

import sqlite3 as sql

columns = ["MEID","OEM","SKU","IMEI","MODEL","HW_TYPE","IN","OUT",
           "ARCHIVED","TesterName","DVTadmin","SERIAL NUMBER","MSL/SPC", "Comment"]


__types__ = {"<type 'list'>": 'json',
             "<type 'unicode'>": 'TEXT',
             "<type 'str'>": 'TEXT',
             "<type 'float'>": 'REAL',
             "<type 'int'>": 'INTEGER',
             "<type 'dict'>": 'json',
             "<type 'bool'>": 'TEXT',
             "<type 'buffer'>": 'BLOB'}

dbfn = "inventory.sqlite"
import os
import path
import json
import sqlite3
import requests
import grequests
from collections import Counter
import time
import sys
reload(sys).setdefaultencoding("utf8")


DEBUG = True
__author__ = 'suber1'
__sqlext__ = '.sqlite'
__sqlsets__ = os.getcwd() + os.sep + 'mtg_sets' + __sqlext__
__sqlcards__ = os.getcwd() + os.sep + 'mtg_cards' + __sqlext__
__sqlfiles__ = [__sqlsets__, __sqlcards__]
__mtgpics__ = os.getcwd() + os.sep + 'pics'
__needs__ = os.getcwd() + os.sep + 'needs_pic_links.json'
__jsonsets__ = 'http://mtgjson.com/json/SetCodes.json'
__jsonupdate__ = 'http://mtgjson.com/json/changelog.json'
__one_set__ = 'http://mtgjson.com/json/{}.json'
__req_limit__ = 21          # can the web server handle getting pounded by this many?
__test_quant__ = 0          # set to zero for normal full run
__max_errors__ = 0          # set positive to explore new import data
__last_update__ = os.getcwd() + os.sep + 'last_update.json'
__set_hdr_excluded__ = [u'cards', u'booster']
__cards_hdr_excluded__ = [u'booster', u'foreignNames']
__newness__ = [u"newSetFiles", u"updatedSetFiles"]
__sets_key__ = u'code'
__sets_t__ = 'set_infos'
__cards_key__ = u'id'
__cards_t__ = 'cards'
__cards_dk__ = u'cards'
__types__ = {"<type 'list'>": 'json',
             "<type 'unicode'>": 'TEXT',
             "<type 'str'>": 'TEXT',
             "<type 'float'>": 'REAL',
             "<type 'int'>": 'INTEGER',
             "<type 'dict'>": 'json',
             "<type 'bool'>": 'TEXT',
             "<type 'buffer'>": 'BLOB'}


class DBMagic (object):
    """
    DBcolumns = {db_tablename: '''CREATE TABLE db_tablename (column_name1 data_type PRIMARY KEY?,
                                column_name2 data_type, )''', ...}
    user: get the columns from the json entry for a card, or make up your own
    """
    def __init__(self, DBfn=None, DBcolumns=None, DB_DEBUG=False):
        self.DB_DEBUG = DB_DEBUG
        self.DBfn = DBfn
        self.DBcolumns = DBcolumns
        if self.DBfn is None:
            self.DBfn = os.path.join(os.path.expanduser('~'), 'Desktop', "MagicDB", __sqlext__)
            print("WARNING, creating/using a default database: {}".format(self.DBfn))
        if not os.path.isdir(os.path.dirname(self.DBfn)):
            os.makedirs(os.path.dirname(self.DBfn))
        sqlite3.register_converter("json", json.loads)
        sqlite3.register_adapter(list, json.dumps)
        sqlite3.register_adapter(dict, json.dumps)
        self.con = sqlite3.connect(self.DBfn, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = sqlite3.OptimizedUnicode
        self.cur = self.con.cursor()
        self.newDB = False
        # check that tables exist. if not, make them
        for t, v in self.DBcolumns.viewitems():
            if not self.cur.execute('''PRAGMA table_info ('{}')'''.format(t)).fetchall():
                self.cur.execute(v)
                self.con.commit()
                print("Created new table: {}".format(t))
                self.newDB = True
            else:
                print("using existing table: {} ".format(t))
            print("in file: {}".format(self.DBfn))
        self.tables = [a[0] for a in
                       self.cur.execute('''SELECT name FROM sqlite_master WHERE type='table' ''').fetchall()]

    def show_columns(self, tablename):
        return [t[1] for t in self.cur.execute('''PRAGMA table_info ('{}')'''.format(tablename)).fetchall()]

    def add_columns(self, tableup, column_map):
        """
        Parameters
        ----------
        tableup: the table to which we are adding columns
        column_map: {'column_foo': sqlite database-type, as string}
                          eg  {'column-name': 'INTEGER', ...}
        """
        present_columns = self.show_columns(tableup)
        for newcol, sql_dtype in column_map.viewitems():
            if newcol not in present_columns:
                self.cur.execute('''ALTER TABLE {} ADD {} {}'''.format(tableup, newcol, sql_dtype))
                if self.DB_DEBUG:
                    print("added column: '{}' of type: '{}' to table: {}".format(newcol, sql_dtype, tableup))
        self.con.commit()

    def add_data(self, data, tbl, key_column=None):
        """
        populate database with list-of-dict values for dict.keys() that are in db-columns
        Parameters
        ----------
        data - list of dict cum json objects whose wanted keys have been made DB column names
        tbl - db_table to which we add this data
        key - the sqlite PRIMARY KEY that the table index is being done on
        Returns
        -------
        side effect = database entry. Made an UPSERT from strings that accepts any number of key: vals
        as long as keys are column names. sqlite3 has no native UPSERT command.
        """
        n, error_count = -1, 0
        if key_column is None:
            hdrs = self.cur.execute('''PRAGMA table_info ({})'''.format(tbl)).fetchall()
            for h in hdrs:
                if bool(h[5]):
                    key_column = h[1]
                    if self.DB_DEBUG:
                        print("guessing primary key is: {}".format(key_column))

        approved_columns = self.show_columns(tbl)

        def hunk(c):
            return c + "=(?)"

        for n, line in enumerate(data):
            line_item = {k: v for k, v in line.viewitems() if k in approved_columns}
            SQL1 = '''INSERT OR IGNORE INTO {}({}) VALUES({})'''.format(str(tbl), ', '.join(line_item.keys()),
                                                                        ':' + ', :'.join(line_item.keys()))
            SQL2 = '''UPDATE {} SET {} WHERE changes()=0 and {}=("{}")'''\
                .format(str(tbl), ", ".join(map(hunk, line_item.keys())), key_column, line_item[key_column])
            try:
                self.cur.execute(SQL1, line_item)
                self.cur.execute(SQL2, line_item.values())
            except (sqlite3.OperationalError, sqlite3.InterfaceError, sqlite3.ProgrammingError) as e:
                error_count += 1
                print("error: {} *****table: {} ***  row#{}   #items={}  >>> {}  ***"
                      .format(error_count, tbl, n, len(line_item), e))
                print(SQL1, SQL2)
                print(line_item)
                if error_count > __max_errors__:
                    print("** data entry has too many problems to ignore. exiting, harshly **")
                    exit(1)
                continue
        self.con.commit()
        return n, error_count


createstr = '''CREATE TABLE {} ({} TEXT PRIMARY KEY)'''
set_db = DBMagic(DBfn=__sqlsets__,
                 DBcolumns={__sets_t__: createstr.format(__sets_t__, __sets_key__)},
                 DB_DEBUG=DEBUG)
card_db = DBMagic(DBfn=__sqlcards__,
                  DBcolumns={__cards_t__: createstr.format(__cards_t__, __cards_key__)},
                  DB_DEBUG=DEBUG)
if __name__ == "__main__":
    pass

