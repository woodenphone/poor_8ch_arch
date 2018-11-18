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




def table_factory_boards():# Boards table
    """ We're Java now!
    Make the 'x_board' table for an 8chan board.
    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
    TODO: Sane database design
    """
    table_name = u'boards'
    logging.debug(u'Naming the board table {0!r}'.format(table_name))
    class Boards(Base):
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
    return Boards



def table_factory_threads(board_name):# Threads table
    """We're Java now!
    Make the 'x_threads' table for an 8chan board.
    see https://stackoverflow.com/questions/19163911/dynamically-setting-tablename-for-sharding-in-sqlalchemy
    TODO: Sane database design"""
    logging.debug(u'table_factory_threads() args={0!r}'.format(locals()))# Record arguments.
    assert(type(board_name) in [unicode])
    table_name = u'{0}_threads'.format(board_name)
    logging.debug(u'Naming the thread table {0!r}'.format(table_name))
    class Threads(Base):
        __tablename__ = table_name
        # From: https://github.com/bibanon/py8chan/blob/master/py8chan/thread.py#L10
        # Use 't_VarName' format to maybe avoid fuckery. (Name confusion, name collission, reserved keywords such as 'id', etc)
        t_thread_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        t_board = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        t_last_reply_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        # py8chan.Thread class attributes
        t_closed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        t_sticky = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        t_topic = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        t_posts = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# TODO FIXME (post-to-thread association)
        t_all_posts = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# TODO FIXME (post-to-thread association)
        t_url = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
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
    logging.debug(u'table_factory_posts() args={0!r}'.format(locals()))# Record arguments.
    assert(type(board_name) in [unicode])
    table_name = u'{0}_posts'.format(board_name)
    logging.debug(u'Naming the posts table {0!r}'.format(table_name))
    class Posts(Base):
        __tablename__ = table_name
        # From: https://github.com/bibanon/py8chan/blob/master/py8chan/post.py#L13
        # Use 'p_VarName' format to maybe avoid fuckery. (Name confusion, name collission, reserved keywords such as 'id', etc)
        p_thread_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        # py8chan.Post class attributes
        p_post_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        p_poster_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        p_name = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        p_email = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        p_tripcode = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        p_subject = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        p_comment = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        p_html_comment = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        p_text_comment = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        p_is_op = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        p_timestamp = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        p_datetime = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        p_first_file = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)# TODO FIXME (File-to-post association)
        p_all_files = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)# TODO FIXME (File-to-post association)
        p_extra_files = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)# TODO FIXME (File-to-post association)
        p_has_file = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        p_has_extra_files = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        p_url = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        # 'Unused' attributes:
        p_poster_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        p_file_deleted = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        p_semantic_url = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        p_semantic_slug = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
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
    logging.debug(u'table_factory_files() args={0!r}'.format(locals()))# Record arguments.
    assert(type(board_name) in [unicode])
    table_name = u'{0}_files'.format(board_name)
    logging.debug(u'Naming the file table {0!r}'.format(table_name))
    class File(Base):
        __tablename__ = table_name
        # https://github.com/bibanon/py8chan/blob/master/py8chan/file.py#L15
        # Use 'm_VarName' format to maybe avoid fuckery. (Name confusion, name collission, reserved keywords such as 'id', etc)
        m_post_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)# TODO: Make this a foreign key linked to posts table
        # py8chan.File class attributes
        m_file_md5 = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        m_file_md5_hex = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        m_filename_original = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        m_filename = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        m_file_url = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        m_file_extension = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        m_file_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        m_file_width = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        m_file_height = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        m_thumbnail_width = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        m_thumbnail_height = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        m_thumbnail_fname = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        m_thumbnail_url = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        # 'Unused' attributes:
        # archive-side values
        archive_filename = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)# What the file is called on the archive's disk
        file_saved = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)# Set to False if the file is lost from the server. Will be set to True when file is saved.
        thumbnail_saved = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)# Set to False if the thumbnail is lost from the server. Will be set to True when thumbnail is saved.
        forbidden = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)# If True any file matching this MD5 will not be downloaded.
        # Misc recordkeeping: (internal use and also for exporting dumps more easily)
        row_created = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.utcnow)
        row_updated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
        primary_key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    return File



##class Luggage():
##    """For carrying things around between functions because I don't know what I'm doing.
##    TODO: Replace this with something that doesn't set off all my shit-code alarms.
##    """
##    def __init__(self, Boards, Threads, Posts, File):
##        # Hold onto DB table classes
##        Boards = Boards
##        Threads = Threads
##        Posts = Posts
##        File = File# TODO: Maybe rename this class to avoid conflicts with builtin 'file'
##        #


def convert_filepath_to_connect_string(filepath):
    """Convert a SQLite file filepath to a SQLAlchemy connection string"""
    # Convert windows-style backslashes to required forwardslashes
    fp_fslash = re.sub(ur'\\\\', '/', filepath)
    connect_string = u'sqlite:///{0}'.format(fp_fslash)
    return connect_string


def get_table_from_base(board_name, table_type):
    """Get the a reference to a table.
    Uses sqlalchemy Base."""
    if table_type == u'boards':# Global tables
        return Base.metadata.tables[u'{0}'.format(table_type)]
    else:# Board-specific tables
        return Base.metadata.tables[u'{0}_{1}'.format(board_name, table_type)]


def insert_thread(ses, board_name, board, thread_id, Boards, Threads, Posts, Files):
    """Fetch and insert one thread.
    ses: Sqlalchemy DB session
    board: py8chan Board instance
    WARNING: May overwrite existing post/thread data in table!
    TODO: Look into resolutions for this potential issue.
    """
    logging.debug(u'Fetching thread: {0!r}'.format(thread_id))
##    Boards = get_table_from_base(board_name=board_name, table_type='boards')
##    Threads = get_table_from_base(board_name=board_name, table_type='threads')
##    Posts = get_table_from_base(board_name=board_name, table_type='posts')
##    Files = get_table_from_base(board_name=board_name, table_type='files')

    # Poll DB for existing posts in this thread
    logging.debug(u'Posts={0!r}'.format(Posts))
    before_add_posts_q = ses.query(Posts)\
        .filter(Posts.p_thread_id == thread_id)

    # Load thread from site
    thread = board.get_thread(thread_id)

    # Shove API data into the DB
    # Put thread-level data into DB
    logging.info(u'Fake thread insert')
    logging.info(u'thread={0!r}'.format(thread))
    # TODO: Insert thread-level data into DB
    new_thread = Threads(
        t_thread_id = thread.id,
        t_board = 0,# TODO Foreign key (thread-to-board association)
        t_last_reply_id = thread.last_reply_id,
        t_closed = thread.closed,
        t_sticky = thread.sticky,
        t_topic = thread.topic.post_id,# TODO Figure out what we want to do here. (Should we even put a topic entry in here? (If so, make foreign key?))
        t_posts = None,# TODO FIXME (post-to-thread association)
        t_all_posts = None,# TODO FIXME (post-to-thread association)
        t_url = thread.url,
    )
    ses.add(new_thread)
    logging.debug(u'Staged thread entry')

    for current_post in thread.all_posts:
        # Put post-level data into DB
        logging.info(u'current_post={0!r}'.format(current_post))
        new_post = Posts(
            p_thread_id = thread_id,
        )
        current_post.post_id
        ses.add(new_post)
        logging.debug(u'Staged post entry')

        # TODO: Insert post to DB
        if current_post.has_file:
            logging.info(u'Post has file(s)')
            for current_file in current_post.all_files():
                # Put file-level data into DB
                logging.info(u'Fake file insert')
                logging.info(u'current_file={0!r}'.format(current_file))

                # TODO Fetch media absent from DB
                # Check if file has entry in DB (look for md5 and file_saved=True)
                # If any rows returned, skip download

                # TODO: Skip forbidden images
                # Check if file has entry in DB (look for md5 and forbidden=True)
                # If any rows returned, skip download


                logging.info(u'current_file.file_md5={0!r}'.format(current_file.file_md5))
                logging.info(u'type(current_file.file_md5)={0!r}'.format(type(current_file.file_md5)))

                file_check_q = ses.query(Files)\
                    .filter(Files.m_file_md5 == current_file.file_md5)
                file_check_result = file_check_q.first()
                if file_check_result:
                    file_saved = file_check_result.file_saved# Does archive have file?
                    thumbnail_saved = file_check_result.thumbnail_saved# Does archive have thumbnail?
                    forbidden = file_check_result.forbidden# Has archive forbidden file hash?
                    # Already saved?
                    if ((file_saved == True) and (thumbnail_saved == True)):
                        # Do not save if file and thumbnail have been saved.
                        logging.debug(u'File already saved: {0!r}'.format(current_file))
                        continue
                    # Forbidden?
                    elif (forbidden == True):
                        # If forbidden, do not permit saving file.
                        logging.debug(u'File is forbidden: {0!r}, MD5={1!r}'.format(current_file, current_file.file_md5))
                        continue
                    else:
                        # If neither thumbnail or full file have been saved, and not forbidden, then save the file.
                        logging.debug(u'Downloading file: {0!r}'.format(current_file))

                        # Load remote file
                        # TODO
                        logging.warning(u'Simulate requesting file')

                        # Save file to disk
                        # TODO
                        logging.warning(u'Simulate storing file')

                        # Insert file row
                        new_file = File(
                        # py8chan columns
                            m_file_md5 = current_file.file_md5,
                            m_file_md5_hex = current_file.file_md5_hex,
                            m_filename_original = current_file.filename_original,
                            m_filename = current_file.filename,
                            m_file_url = current_file.file_url,
                            m_file_extension = current_file.file_extension,
                            m_file_size = current_file.file_size,
                            m_file_width = current_file.file_width,
                            m_file_height = current_file.file_height,
                            m_thumbnail_width = current_file.thumbnail_width,
                            m_thumbnail_height = current_file.thumbnail_height,
                            m_thumbnail_fname = current_file.thumbnail_fname,
                            m_thumbnail_url = current_file.thumbnail_url,
                            # archive-side data (File present on disk? File forbidden?)
                            file_saved = True,
                            thumbnail_saved=True,
                            forbidden = True
                        )
                        ses.add(new_file)
                        logging.debug(u'Staged file entry')
                continue
            logging.debug(u'Finished this post\'s files')
            continue
        logging.debug(u'Finished this thread\'s posts')
        continue
    logging.info(u'Fetched thread')
    return


def dev():
    logging.warning(u'running dev()')
    board_name = u'pone'
    db_filepath = os.path.join(u'temp', u'{0}.sqlite'.format(board_name))
    connection_string = convert_filepath_to_connect_string(filepath=db_filepath)
    thread_id = 316521 # https://8ch.net/pone/res/316521.html
    # Prepare board DB classes/table mappers
    Boards = table_factory_boards()
    Threads = table_factory_threads(board_name)
    Posts = table_factory_posts(board_name)
    Files = table_factory_files(board_name)
##    lug = Luggage(# TODO FIX THIS TERRIBLE FEELING MONSTROSITY
##        Boards=Boards,
##        Threads=Threads,
##        Posts=Posts,
##        Files=Files
##    )

    # Setup/start/connect to DB
    logging.debug(u'Connecting to DB')
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
        board_name=board_name,
        board=pone,
        thread_id=thread_id,
        Boards=Boards,
        Threads=Threads,
        Posts=Posts,
        Files=Files,
    )

    # Persist data now that thread has been grabbed
    session.commit()

    logging.info(u'Ending DB session')
    session.close()# Release connection back to pool.
    engine.dispose()# Close all connections.

    logging.warning(u'exiting dev()')
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
        logging.critical(u"Unhandled exception!")
        logging.exception(e)
    logging.info(u"Program finished.")
