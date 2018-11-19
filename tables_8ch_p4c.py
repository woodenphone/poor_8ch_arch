#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     19-11-2018
# Copyright:   (c) User 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# StdLib
import logging
import logging.handlers
import datetime
# Remote libraries
import sqlalchemy# For talking to DBs
from sqlalchemy.ext.declarative import declarative_base
# local



def table_factory_boards(Base):# Boards table
    """ We're Java now!
    Make the 'x_board' table for an 8chan archive.
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



def table_factory_threads(Base, board_name):# Threads table
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




def table_factory_posts(Base, board_name):# Posts table
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



def table_factory_files(Base, board_name):# File table
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












def main():
    pass

if __name__ == '__main__':
    main()
