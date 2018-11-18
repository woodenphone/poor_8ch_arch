#-------------------------------------------------------------------------------
# Name:        grab_board.py
# Purpose:      Grab threads from one board
#
# Author:      User
#
# Created:     18-11-2018
# Copyright:   (c) User 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------




class board():
    """An 8ch board"""
    def __init__(self):
        return


class thread():
    """An 8ch thread"""
    def __init__(self):
        self.posts = []
        return

    def update(self):
        logging.debug('Updating thread {0!r}'.format())
        return

    def db_push(self):
        """Shove the thread into the DB"""


class post():
    """An 8ch post"""
    def __init__(self):
        self.images = []
        return



class image():
    """An 8ch image"""
    def __init__(self):
        self.thumbnail = None
        return


class thumbnail():
    """An 8ch thumbnail"""
    def __init__(self):
        self.url = None
        filename = None
        filepath = None
        time_fetched = None
        time_uploaded = None
        return






def main():
    pass

if __name__ == '__main__':
    main()
