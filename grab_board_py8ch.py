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
##import py8chanutf as py8chan# For talking to 8chan, but a fork that demands unicode strings

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
        b_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, unique=True)
        b_name = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        b_title = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        b_is_worksafe = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        b_page_count= sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
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
        t_thread_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, unique=True)
        t_board = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
        t_last_reply_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, unique=True)
        # py8chan.Thread class attributes
        t_closed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        t_sticky = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        t_topic = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
        t_url = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True, unique=True)
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
        p_post_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, unique=True)
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
        p_has_file = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        p_has_extra_files = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
        p_url = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True, unique=True)
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
        m_post_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, unique=True)# TODO: Make this a foreign key linked to posts table
        # py8chan.File class attributes
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


def please_utf(text):
    """Ensure text is unicode"""
    logging.info(u'text={0!r}'.format(text))
    if type(text) is unicode:
        return text
    elif type(text) is str:
        encoded = text.encode('utf8')
        logging.info(u'encoded={0!r}'.format(encoded))
        return encoded
    elif type(text) is type(None):
        return text
    else:
        logging.error('please_unicode() only accepts text objects')
        raise ValueError()


def generate_image_filepath(base, filename):
    """Generate the filepath to use for storing a given filename.
    Consists of variable prefix 'base' and detemanisticly generated subdir.
    <base>/<0,1>/<2,3>/<filename>
    ex: 'images/01/23/12345ABCDE.png'
    TODO: Make more like asagi/foolfuuka for compatability.
    """
    return os.path.join(base, filename[0:2], filename[2:4], filename)


def download_file(reqs_ses, url, filepath):
    res = common.fetch(
        requests_session=reqs_ses,
        url=url,
        method='get',
        expect_status=200,
    )
    common.write_file(# Store page to disk
        file_path=filepath,
        data=res.content
    )
    logging.debug('Saved {0} to {1}'.format(url, filepath))
    return


def process_image(db_ses, board_name, board, thread_id,
    Boards, Threads, Posts, Files,
    dl_dir, reqs_ses, current_file):
    """Put file-level data into DB"""
    logging.info(u'current_file={0!r}'.format(current_file))
    # Generate paths, names, etc.
    file_md5_hex = please_utf(current_file.file_md5_hex)
    archive_filename_file = '{h}.{e}'.format(h=file_md5_hex, e=current_file.file_extension)
    archive_filepath_file = generate_image_filepath(base=dl_dir, filename=archive_filename_file)
    archive_filename_thumbnail = '{h}.{e}'.format(h=file_md5_hex, e=current_file.file_extension)
    archive_filepath_thumbnail = generate_image_filepath(base=dl_dir, filename=archive_filename_thumbnail)
    # Look for existing copies of the file
    file_check_q = db_ses.query(Files)\
        .filter(Files.m_file_md5_hex == file_md5_hex)
    file_check_result = file_check_q.first()
    if file_check_result:
        file_saved = file_check_result.file_saved# Does archive have file?
        thumbnail_saved = file_check_result.thumbnail_saved# Does archive have thumbnail?
        forbidden = file_check_result.forbidden# Has archive forbidden file hash?
        # Already saved?
        if ((file_saved == True) and (thumbnail_saved == True)):
            # Do not save if file and thumbnail have been saved.
            logging.debug(u'File already saved: {0!r}'.format(current_file))
            return
        # Forbidden?
        elif (forbidden == True):
            # If forbidden, do not permit saving file.
            logging.debug(u'File is forbidden: {0!r}, MD5={1!r}'.format(current_file, file_md5_hex))
            return
    else:
        # No existing DB entry for this file
        file_saved = False
        thumbnail_saved = False
    # Do downloads if appropriate
    # Save file
    if (file_saved):
        # Download is appropriate.
        logging.debug(u'Downloading file: {0!r}'.format(current_file.file_url))
        download_file(
            reqs_ses=reqs_ses,
            url=current_file.file_url,
            filepath=archive_filepath_file,
        )
    # Save thumb
    if (thumbnail_saved):
        logging.debug(u'Downloading thumbnail: {0!r}'.format(current_file.thumbnail_url))
        download_file(
            reqs_ses=reqs_ses,
            url=current_file.thumbnail_url,
            filepath=archive_filepath_thumbnail,
        )
    # Once we know we have the file on disk, create an entry on the image table
    # Insert file row
    sqlalchemy.insert(Files)\
        .values(
        # py8chan columns
        m_file_md5_hex = please_utf(current_file.file_md5_hex),
        m_filename_original = please_utf(current_file.filename_original),
        m_filename = please_utf(current_file.filename),
        m_file_url = please_utf(current_file.file_url),
        m_file_extension = please_utf(current_file.file_extension),
        m_file_size = current_file.file_size,
        m_file_width = current_file.file_width,
        m_file_height = current_file.file_height,
        m_thumbnail_width = current_file.thumbnail_width,
        m_thumbnail_height = current_file.thumbnail_height,
        m_thumbnail_fname = please_utf(current_file.thumbnail_fname),
        m_thumbnail_url = please_utf(current_file.thumbnail_url),
        # archive-side data (File present on disk? File forbidden?)
        archive_filename_file = archive_filename_file,# Actual disk filename
        archive_filename_thumbnail = archive_filename_thumbnail,# Actual disk filename
        file_saved = True,# Do we actually have the file, this should be set False if it is lost somehow.
        thumbnail_saved = True,# Do we actually have the thumbnail, this should be set False if it is lost somehow.
    )
    logging.debug(u'Staged file entry')
    return


def process_post(db_ses, board_name, board, thread_id,
    Boards, Threads, Posts, Files, dl_dir, reqs_ses,
    post):
    """Process a single post."""
    # Put post-level data into DB
    logging.info(u'post={0!r}'.format(post))
    post_id = post.post_id
    # Check if post already saved
    post_check_q = db_ses.query(Files)\
        .filter(Posts.p_thread_id == thread_id,)\
        .filter(Posts.p_post_id == post_id)
    post_check_result = post_check_q.first()
    if post_check_result:
        logging.debug('Post {0} in thread {1} already saved'.format(post_id, thread_id))
        return
    else:
        # Insert new post
        # Alternatively, asagi-style 'postid is primary key' trick to overwrite on insert, skipping extra SELECT operation?
        sqlalchemy.insert(Posts)\
            .values(
            p_thread_id = thread_id,
            # py8chan.Post class attributes
            p_post_id = post.post_id,
            p_name = please_utf(post.name),
            p_email = please_utf(post.email),
            p_tripcode = please_utf(post.tripcode),
            p_subject = please_utf(post.subject),
            p_comment = please_utf(post.comment),
            p_html_comment = please_utf(post.html_comment),
            p_text_comment = please_utf(post.text_comment),
            p_is_op = (post == thread.topic),# post.is_op,
            p_timestamp = post.timestamp,
            p_datetime = post.datetime,
            p_has_file = post.has_file,
            p_has_extra_files = post.has_extra_files,
            p_url = please_utf(post.url),
        )
        logging.debug(u'Staged post entry')
        # Insert post to DB
        if post.has_file:
            logging.info(u'Post has file(s)')
            process_image(
                db_ses,
                board_name,
                board,
                thread_id,
                Boards,
                Threads,
                Posts,
                Files,
                dl_dir,
                reqs_ses,
                current_file
            )
            logging.debug(u'Finished this post\'s files')
    return


def process_thread(db_ses, board_name, board, thread_id,
    Boards, Threads, Posts, Files, dl_dir, reqs_ses ):
    """Fetch and insert one thread.
    db_ses: Sqlalchemy DB session
    board: py8chan Board instance
    WARNING: May overwrite existing post/thread data in table!
    TODO: Look into resolutions for this potential issue.
    """
    logging.debug(u'Fetching thread: {0!r}'.format(thread_id))
    # Load thread from site
    thread = board.get_thread(thread_id)
    logging.info(u'thread={0!r}'.format(thread))
    # Check if thread is already in the DB
    thread_check_q = db_ses.query(Threads)\
        .filter(Threads.t_thread_id == thread_id,)
    thread_check_result = thread_check_q.first()
    logging.info(u'thread_check_result={0!r}'.format(thread_check_result))
    # Push thread-leven info to DB
    if (thread_check_result):
        # UPDATE thread entry
        sqlalchemy.update(Threads)\
            .where(Threads.primary_key == thread_check_result.primary_key)\
            .values(
            t_thread_id = thread.id,
            t_board = 0,# TODO Foreign key (thread-to-board association)
            t_last_reply_id = thread.last_reply_id,
            t_closed = thread.closed,
            t_sticky = thread.sticky,
            t_topic = thread.topic.post_id,# TODO Figure out what we want to do here. (Should we even put a topic entry in here? (If so, make foreign key?))
            t_url = thread.url,
        )
        logging.debug(u'Updated thread entry')
    else:
        # INSERT thread entry
        sqlalchemy.insert(Threads)\
            .values(
            t_thread_id = thread.id,
            t_board = 0,# TODO Foreign key (thread-to-board association)
            t_last_reply_id = thread.last_reply_id,
            t_closed = thread.closed,
            t_sticky = thread.sticky,
            t_topic = thread.topic.post_id,# TODO Figure out what we want to do here. (Should we even put a topic entry in here? (If so, make foreign key?))
            t_url = thread.url,
        )
        logging.debug(u'Inserted thread entry')
    # Process all posts in the thread
    for post in thread.all_posts:
        process_post(
        db_ses,
        board_name,
        board,
        thread_id,
        Boards,
        Threads,
        Posts,
        Files,
        dl_dir,
        reqs_ses,
        post
        )
        logging.debug(u'Finished this thread\'s posts')
        continue
    logging.info(u'Fetched thread')
    return


def dev():
    logging.warning(u'running dev()')

    # Set run parameters
    board_name = u'pone'
    db_filepath = os.path.join(u'temp', u'{0}.sqlite'.format(board_name))
    connection_string = convert_filepath_to_connect_string(filepath=db_filepath)
    thread_id = 316521 # https://8ch.net/pone/res/316521.html
    dl_dir = os.path.join('dl', 'test', '{0}'.format(board_name))

    # Setup requests session
    reqs_ses = requests.Session()

    # Prepare board DB classes/table mappers
    Boards = table_factory_boards()
    Threads = table_factory_threads(board_name)
    Posts = table_factory_posts(board_name)
    Files = table_factory_files(board_name)

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
    process_thread(
        db_ses=session,
        board_name=board_name,
        board=pone,
        thread_id=thread_id,
        Boards=Boards,
        Threads=Threads,
        Posts=Posts,
        Files=Files,
        dl_dir=dl_dir,
        reqs_ses=reqs_ses,
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
        main()
    # Log exceptions
    except Exception, e:
        logging.critical(u"Unhandled exception!")
        logging.exception(e)
    logging.info(u"Program finished.")
