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


# Global stuff:
Base = declarative_base()# Setup system to keep track of tables and classes




def table_factory_board(board_name):# Boards table
    """ We're Java now!
    Make the 'x_board' table for an 8chan board.
    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
    TODO: Sane database design
    """
    logging.debug('table_factory_board() args={0!r}'.format(locals()))# Record arguments.
    assert(type(board_name) in [str, unicode])
    table_name = '{0}_board'.format(board_name)
    logging.debug('Naming the board table {0!r}'.format(table_name))
    class Board(Base):
        __tablename__ = table_name
        # From: https://github.com/bibanon/py8chan/blob/master/py8chan/board.py#L76
        # Use 'b_VarName' format to maybe avoid fuckery. (Name confusion, name collission, reserved keywords such as 'id', etc)
        b_name = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        b_title = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        b_is_worksafe = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        b_page_count= sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        b_title = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        b_threads_per_page = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        # Misc recordkeeping (internal use and also for exporting dumps more easily)
        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
        primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    return Board



def table_factory_threads(board_name):# Threads table
    """We're Java now!
    Make the 'x_threads' table for an 8chan board.
    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
    TODO: Sane database design"""
    logging.debug('table_factory_threads() args={0!r}'.format(locals()))# Record arguments.
    assert(type(board_name) in [str, unicode])
    table_name = '{0}_threads'.format(board_name)
    logging.debug('Naming the thread table {0!r}'.format(table_name))
    class Threads(Base):
        __tablename__ = table_name
        # From: https://github.com/bibanon/py8chan/blob/master/py8chan/thread.py#L10
        # Use 't_VarName' format to maybe avoid fuckery. (Name confusion, name collission, reserved keywords such as 'id', etc)
        t_thread_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        t_board = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        t_last_reply_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        # py8chan.Thread class attributes
        t_closed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        t_sticky = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        t_topic = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        t_posts = sqlalchemy.Column(sqlalchemy.String, nullable=True)# TODO FIXME (post-to-thread association)
        t_all_posts = sqlalchemy.Column(sqlalchemy.String, nullable=True)# TODO FIXME (post-to-thread association)
        t_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        # 'Unused' attributes:
        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
        primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    return Threads




def table_factory_posts(board_name):# Posts table
    """We're Java now!
    Make the 'x_posts' table for an 8chan board.
    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
    TODO: Sane database design"""
    logging.debug('table_factory_posts() args={0!r}'.format(locals()))# Record arguments.
    assert(type(board_name) in [str, unicode])
    table_name = '{0}_posts'.format(board_name)
    logging.debug('Naming the posts table {0!r}'.format(table_name))
    class Posts(Base):
        __tablename__ = table_name
        # From: https://github.com/bibanon/py8chan/blob/master/py8chan/post.py#L13
        # Use 'p_VarName' format to maybe avoid fuckery. (Name confusion, name collission, reserved keywords such as 'id', etc)
        # py8chan.Post class attributes
        p_post_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        p_poster_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        p_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        p_email = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        p_tripcode = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        p_subject = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        p_comment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        p_html_comment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        p_text_comment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        p_is_op = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        p_timestamp = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        p_datetime = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        p_first_file = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)# TODO FIXME (File-to-post association)
        p_all_files = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)# TODO FIXME (File-to-post association)
        p_extra_files = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)# TODO FIXME (File-to-post association)
        p_has_file = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        p_has_extra_files = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        p_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        # 'Unused' attributes:
        p_poster_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        p_file_deleted = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        p_semantic_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        p_semantic_slug = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        # Misc recordkeeping (internal use and also for exporting dumps more easily)
        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
        primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    return Posts



def table_factory_files(board_name):# File table
    """We're Java now!
    Make the 'x_files' table for an 8chan board.
    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
    TODO: Sane database design"""
    logging.debug('table_factory_files() args={0!r}'.format(locals()))# Record arguments.
    assert(type(board_name) in [str, unicode])
    table_name = '{0}_files'.format(board_name)
    logging.debug('Naming the file table {0!r}'.format(table_name))
    class File(Base):
        __tablename__ = table_name
        # https://github.com/bibanon/py8chan/blob/master/py8chan/file.py#L15
        # Use 'm_VarName' format to maybe avoid fuckery. (Name confusion, name collission, reserved keywords such as 'id', etc)
        # py8chan.File class attributes
        m_file_md5 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        m_file_md5_hex = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        m_filename_original = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        m_filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        m_file_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        m_file_extension = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        m_file_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        m_file_width = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        m_file_height = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        m_thumbnail_width = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        m_thumbnail_height = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        m_thumbnail_fname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        m_thumbnail_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
        # 'Unused' attributes:
        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
        primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    return File



def convert_filepath_to_connect_string(filepath):
    """Convert a SQLite file filepath to a SQLAlchemy connection string"""
    # Convert windows-style backslashes to required forwardslashes
    fp_fslash = re.sub(r'\\\\', '/', filepath)
    connect_string = 'sqlite:///{0}'.format(fp_fslash)
    return connect_string



def insert_thread(ses, board, thread_id):
    """Fetch and insert one thread.
    ses: Sqlalchemy DB session
    board: py8chan Board instance
    """
    thread = board.get_thread(thread_id)

    # Shove API data into the DB
    # Put thread-level data into DB
    logging.info('Fake thread insert')
    logging.info('thread={0}'.format(thread))
    # TODO: Insert thread-level data into DB
    for current_post in thread.all_posts:
        # Put post-level data into DB
        post = Post()
        logging.info('current_post={0}'.format(current_post))
        # TODO: Insert post to DB
        if current_post.has_file:
            logging.info('Post has file(s)')
            for current_file in current_post.all_files():
                # Put file-level data into DB
                logging.info('Fake file insert')
                logging.info('current_file={0}'.format(current_file))
                # TODO Fetch media absent from DB
    return


def dev():
    logging.warning('running dev()')
    board_name = 'pone'
    db_filepath = os.path.join('temp', '{0}.sqlite'.format(board_name))
    connection_string = convert_filepath_to_connect_string(filepath=db_filepath)
    thread_id = 316521 # https://8ch.net/pone/res/316521.html
    # Prepare board DB classes/table mappers
    Board = table_factory_board(board_name)
    Threads = table_factory_threads(board_name)
    Posts = table_factory_posts(board_name)
    File = table_factory_files(board_name)

    # Setup/start/connect to DB
    logging.debug('Connecting to DB')
    db_dir, db_filename = os.path.split(db_filepath)
    if len(db_dir) != 0:# Ensure DB has a dir to be put in
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    # Start the DB engine
    engine = sqlalchemy.create_engine(
        connection_string,# Points SQLAlchemy at a DB
        echo=True# Output DB commands to log
    )
    # Link table/class mapping to DB engine and make sure tables exist.
    Base.metadata.bind = engine# Link 'declarative' system to our DB
    Base.metadata.create_all(checkfirst=True)# Create tables based on classes
    # Create a session to interact with the DB
    SessionClass = sqlalchemy.orm.sessionmaker(bind=engine)
    session = SessionClass()
    # Fetch from the API
    pone = py8chan.Board(board_name)

##    # TODO: Whole board grabbing
##    thread = pone.get_thread(thread_id)

    # Shove API data into the DB
    insert_thread(
        ses=session,
        board=pone,
        thread_id=thread_id
    )


##    # Put thread-level data into DB
##    logging.info('Fake thread insert')
##    logging.info('thread={0}'.format(thread))
##    for current_post in thread.all_posts:
##        # Put post-level data into DB
##        logging.info('Fake post insert')
##        logging.info('current_post={0}'.format(current_post))
##        if current_post.has_file:
##            logging.info('Post has file(s)')
##            for current_file in current_post.all_files():
##                # Put file-level data into DB
##                logging.info('Fake file insert')
##                logging.info('current_file={0}'.format(current_file))
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
