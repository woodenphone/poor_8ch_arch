#-------------------------------------------------------------------------------
# Name:        grab_board_py4chan_asagi.py
# Purpose:      Python alternative to Asagi.
#
# Author:      User
#
# Created:     19-11-2018
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
import basc_py4chan# For talking to 4chan
import sqlite3# Because spinning up a new DB is easier this way
import sqlalchemy# For talking to DBs
from sqlalchemy.ext.declarative import declarative_base
# local
import common
import tables_4ch_asagi

Base = declarative_base()# Setup system to keep track of tables and classes









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






def process_image():
    return



def process_post(db_ses, board_name, board,
                thread_id, Boards, Threads,
                Posts, Files, dl_dir,
                reqs_ses, post):
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


def is_post_in_results(results, thread_num, num, subnum):
    """Check if the specified post is in the results rows.
    If it is, return that row.
    else, return None
    """
    for result in results:
        tn = (result.thread_num == thread_num)
        pn = (result.num == num)
        sn = (result.subnum == subnum)
        logging.debug(u'tn={0!r}, pn={1!r}, sn={2!r}'.format(tn, pn, sn))# PERFOMANCE: Disable this
        if (tn and pn and sn):
            return result
    return None


def process_thread(db_ses, board_name, board, thread_id,
    Boards, Threads, Posts, Files, dl_dir, reqs_ses, ):
    # Fetch thread
    logging.debug(u'Fetching thread: {0!r}'.format(thread_id))
    thread = board.get_thread(thread_id)# Load thread from site
    logging.info(u'thread={0!r}'.format(thread))
    # Look for thread in DB
    thread_check_q = db_ses.query(Threads)\
        .filter(Threads.t_thread_id == thread_id,)
    thread_check_result = thread_check_q.first()
    logging.info(u'thread_check_result={0!r}'.format(thread_check_result))
    # INSERT/UPDATE thread
    # process posts
    # Look for all posts for this thread in DB
    existing_posts_q = db_ses.query(Posts)\
        .filter(Posts.thread_num == thread_id,)
    existing_posts = existing_posts_q.all()
    logging.info(u'existing_posts={0!r}'.format(existing_posts))
    # Simplify thread rows to a list of postIDs
    existing_post_identifiers = []# [ (thread_num, num, subnum), ... ]
    for existing_post in existing_posts:
        existing_post_intentifier = u'{0}.{1}.{2}'.format(existing_post.thread_num, existing_post.num, existing_post.subnum)
        existing_post_ids.append(existing_post_intentifier)
    # Insert any post not on list of saved postIDs
    for post in thread.all_posts:
        # Determine if we have this post
##        post_intentifier = u'{0}.{1}.{2}'.format(post.thread_num, post.num, post.subnum)
##        have_post = (post_intentifier in existing_post_identifiers)
        have_post = is_post_in_results(results=existing_posts, thread_num=post.thread_num, num=post.num, subnum=post.subnum)
        if (not have_post):
            process_post(
                db_ses, board_name, board,
                thread_id, Boards, Threads,
                Posts, Files, dl_dir,
                reqs_ses, post
            )
    logging.debug(u'Finished this thread\'s posts')
    logging.info(u'Fetched thread: {0!r}'.format(thread_id))
    return


def process_board():

    return


def dev():
    logging.warning(u'running dev()')

    # Set run parameters
    board_name = u'mlp'
    db_filepath = os.path.join(u'temp', u'{0}.sqlite'.format(board_name))
    connection_string = convert_filepath_to_connect_string(filepath=db_filepath)
    thread_id = TODO # TODO
    dl_dir = os.path.join('dl', '8test', '{0}'.format(board_name))

    # Setup requests session
    reqs_ses = requests.Session()

    # Prepare board DB classes/table mappers
    Threads = tables_4ch_asagi.table_factory_threads(board_name)
    Posts = tables_4ch_asagi.table_factory_posts(board_name)
    Files = tables_4ch_asagi.table_factory_files(board_name)

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
    board = basc_py4chan.Board(board_name)

##    # TODO: Whole board grabbing

    # Shove API data into the DB
    process_thread(
        db_ses=session,
        board_name=board_name,
        board=board,
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
    common.setup_logging(os.path.join("debug", "grab_board_py8ch_asagi.log.txt"))# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical(u"Unhandled exception!")
        logging.exception(e)
    logging.info(u"Program finished.")