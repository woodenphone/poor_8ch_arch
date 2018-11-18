#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     18-11-2018
# Copyright:   (c) User 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# StdLib
import time
import os
import random
import logging
import logging.handlers
import datetime
import json
import cookielib
import re
# Remote libraries
import requests# For talking to websites
import requests.exceptions
import py8chan# For talking to 8chan
import sqlite3# Because spinning up a new DB is easier this way
import sqlalchemy# For talking to DBs
from sqlalchemy.ext.declarative import declarative_base
# local
import common



Base = declarative_base()# Setup system to keep track of tables and classes




# We need a DB

# Allocate one table per board because fuck deduplication, that's hard and hard kills projects.

def threads_table_factory(board_name):
    """ We're Java now!"""
    logging.debug('threads_table_factory() args={0!r}'.format(locals()))# Record arguments.
    assert(type(board_name) in [str, unicode])
    table_name = '{0}_threads'.format(board_name)
    # https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
    class BoardThreads(Base):
        __tablename__ = table_name
        # From: https://github.com/bibanon/py8chan/blob/master/py8chan/board.py#L76
        # Use 'board_VarName' format to maybe avoid fuckery. (Name confusion, name collission, etc)
        board_name = sqlalchemy.Column('board_name', sqlalchemy.Integer, nullable=True)
        board_title = sqlalchemy.Column('board_title', sqlalchemy.Integer, nullable=True)
        board_is_worksafe = sqlalchemy.Column('board_is_worksafe', sqlalchemy.Boolean, nullable=True)
        board_page_count= sqlalchemy.Column('board_page_count', sqlalchemy.Integer, nullable=True)
        board_title = sqlalchemy.Column('board_title', sqlalchemy.Integer, nullable=True)
        board_threads_per_page = sqlalchemy.Column('board_threads_per_page', sqlalchemy.Integer, nullable=True)
        # Misc recordkeeping (internal use and also for exporting dumps more easily)
        row_created = sqlalchemy.Column('row_created', sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
        row_updated = sqlalchemy.Column('row_updated', sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
        primary_key = sqlalchemy.Column('primary_key', sqlalchemy.Integer, primary_key=True)


##    metadata = sqlalchemy.MetaData()
##    Threads = sqlalchemy.Table(table_name, metadata,
##        # From: https://github.com/bibanon/py8chan/blob/master/py8chan/board.py#L76
##        # Use 'board_VarName' format to maybe avoid fuckery.
##        sqlalchemy.Column('board_name', sqlalchemy.Integer, nullable=True),
##        sqlalchemy.Column('board_title', sqlalchemy.Integer, nullable=True),
##        sqlalchemy.Column('board_is_worksafe', sqlalchemy.Boolean, nullable=True),
##        sqlalchemy.Column('board_page_count', sqlalchemy.Integer, nullable=True),
##        sqlalchemy.Column('board_title', sqlalchemy.Integer, nullable=True),
##        sqlalchemy.Column('board_threads_per_page', sqlalchemy.Integer, nullable=True),
##        # Misc recordkeeping (internal use and also for exporting dumps more easily)
##        sqlalchemy.Column('row_created', sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow),
##        sqlalchemy.Column('row_updated', sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow),
##        sqlalchemy.Column('primary_key', sqlalchemy.Integer, primary_key=True)
##    )
####    sqlalchemy.clear_mappers()
##    sqlalchemy.mapper(ActualTableObject, Threads)
    return BoardThreads
Threads = threads_table_factory(board_name='pone')


### Disregard this
##def get_dynamic_table_obj_ff(table_name):
##    """Generate a table with a custom name"""
##    # https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
##    logging.debug('import_from_ff_db() args={0!r}'.format(locals()))# Record arguments. WARNING: It is dangerous to record connection string!
##    assert(type(table_name) in [str, unicode])
##    metadata = sqlalchemy.MetaData()
##    table_object = sqlalchemy.Table(table_name, metadata,
####        Column('Column1', DATE, nullable=False),
##        # Foolfuuka media.img_<BOARDNAME> values
##        sqlalchemy.Column('media_id', sqlalchemy.Integer, nullable=True),
##        sqlalchemy.Column('media_hash', sqlalchemy.String(32), nullable=True),
##        sqlalchemy.Column('media', sqlalchemy.String, nullable=True),
##        sqlalchemy.Column('preview_op', sqlalchemy.String, nullable=True),
##        sqlalchemy.Column('preview_reply', sqlalchemy.String, nullable=True),
##        sqlalchemy.Column('total', sqlalchemy.Integer, nullable=True),
##        sqlalchemy.Column('banned', sqlalchemy.Integer, nullable=True),
##        # Recordkeeping about export progress
##        sqlalchemy.Column('media_exported', sqlalchemy.Boolean, nullable=False),
##        sqlalchemy.Column('media_exported_date', sqlalchemy.DateTime, nullable=True),
##        sqlalchemy.Column('op_exported', sqlalchemy.Boolean, nullable=False),
##        sqlalchemy.Column('op_exported_date', sqlalchemy.DateTime, nullable=True),
##        sqlalchemy.Column('reply_exported', sqlalchemy.Boolean, nullable=False),
##        sqlalchemy.Column('reply_exported_date', sqlalchemy.DateTime, nullable=True),
##        # Misc recordkeeping
##        sqlalchemy.Column('row_created', sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow),
##        sqlalchemy.Column('row_updated', sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow),
##        sqlalchemy.Column('primary_key', sqlalchemy.Integer, primary_key=True)
##
##    )
####    sqlalchemy.clear_mappers()
##    sqlalchemy.mapper(ActualTableObject, table_object)
##    return table_object
##f_table = get_dynamic_table_obj_ff(table_name='ftg_testtable')
### /Disregard this












# Threads table


# Posts table



# Images table








# Shove things into the DB







def dev():
    logging.warning('running dev()')



    logging.warning('exiting dev()')
    return


def main():
    dev()
    return


if __name__ == '__main__':
    common.setup_logging(os.path.join("debug", "grab_board_py8ch.log.txt"))# Setup logging
    try:
        # Load configurations here to make them global
        main()
    # Log exceptions
    except Exception, e:
        logging.critical("Unhandled exception!")
        logging.exception(e)
    logging.info("Program finished.")
