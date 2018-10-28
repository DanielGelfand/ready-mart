'''library of functions for interacting with sql database, hashword passing.
   come to the computer interaction club on haloween in room 413
   we're watching the fantastic movie "Killer Klowns From Outer Space"
   the first argument for all these functions should be a database cursor (except for the string parsing helper function, obviously)'''

import sqlite3
from passlib.hash import pbkdf2_sha256

def reset(squul):
    '''clears database of all data, rebuilds tables
       also use to initialize tables'''
    squul.execute("DROP TABLE IF EXISTS stories;")
    squul.execute("DROP TABLE IF EXISTS history;")
    squul.execute("DROP TABLE IF EXISTS users;")

    squul.execute("CREATE TABLE stories (storyid INTEGER PRIMARY KEY, title TEXT, content TEXT, lastedit TEXT);")
    squul.execute("CREATE TABLE history (storyid INTEGER PRIMARY KEY);")
    squul.execute("CREATE TABLE users (userid INTEGER PRIMARY KEY, username TEXT, password TEXT);")


def last_story(squul, storyid):
    '''retrieves the last edit made to story storyid'''
    squul.execute("SELECT lastedit FROM stories WHERE stories.storyid = ?;", (storyid, ))
    return squul.fetchall()[0][0]

def hole_story(squul, storyid):
    '''retrieves full text of story, including last edit'''
    squul.execute("SELECT content, lastedit FROM stories WHERE stories.storyid = ?;", (storyid, ))
    return '\n'.join(str(i) for i in squul.fetchall()[0] if i != None)

def title_story(squul, storyid):
    '''retrives story title'''
    squul.execute("SELECT title FROM stories WHERE stories.storyid = ?;", (storyid, ))
    return squul.fetchall()[0][0]

# TODO: parse the story text for sql trickery -- which i think the ?'s take care of

def edit_story(squul, storyid, shrext, userid):
    '''if user is able, updates user to indicate they have edited story, and adds that users edits to the story'''
    if can_edit(squul, storyid, userid):
        squul.execute("UPDATE stories SET content = ? WHERE stories.storyid = ?;", (hole_story(squul, storyid), storyid))
        squul.execute("UPDATE stories SET lastedit = ? WHERE stories.storyid = ?;", (foo_char_html(shrext), storyid))
        squul.execute("UPDATE history SET {} = 1 WHERE history.storyid = {};".format('u' + str(userid), storyid))

def can_edit(squul, storyid, userid):
    '''returns whether a user should be in editing mode for a particular story
    decide whether to display editing mode of story, or which stories to list on users home page.'''
    squul.execute("SELECT {} FROM history WHERE history.storyid =  {};".format('u' + str(userid), storyid))
    return squul.fetchall()[0][0] == 0

def all_edit(squul, userid):
    '''returns titles and storyids of all stories a user can edit'''
    squul.execute("SELECT stories.storyid, stories.title FROM stories INNER JOIN history ON stories.storyid = history.storyid WHERE history.{} = 0;".format('u' + str(userid)))
    return(squul.fetchall())

def not_edit(squul, userid):
    '''returns titles and storyids of all stories a user CANT edit -- ie they have previously edited'''
    squul.execute("SELECT stories.storyid, stories.title FROM stories INNER JOIN history ON stories.storyid = history.storyid WHERE history.{} = 1;".format('u' + str(userid)))
    return(squul.fetchall())

def add_story(squul, storyid, shrext, userid, title):
    '''creates a new story info in stories and history table'''
    squul.execute("INSERT INTO stories VALUES(?, ?, ?, ?);", (storyid, foo_char_html(title), None, foo_char_html(shrext)))
    squul.execute("INSERT INTO history (storyid) VALUES(?);", (storyid,))
    squul.execute("UPDATE history SET {} = 1 WHERE history.storyid = {};".format('u' + str(userid), storyid))

def add_user(squul, userid, username, hashword):
    '''creates entries for a new user, both for user and in history database'''
    squul.execute("INSERT INTO users VALUES(?, ?, ?);", (userid, foo_char_html(username), pbkdf2_sha256.hash(hashword.encode("ascii", "replace"))))
    squul.execute("ALTER TABLE history ADD COLUMN {} INTEGER DEFAULT 0;".format('u' + str(userid)))

def user_exists(squul, user):
    '''validates a user linked to some username exists'''
    exist = squul.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username = ?);", (foo_char_html(user),))
    return exist.fetchone()[0] == 1


def check_user(squul, user, hashword):
    '''checks if user's password valid'''
    toCheck = squul.execute("SELECT password from users WHERE username = ?;", (foo_char_html(user),))
    return pbkdf2_sha256.verify(hashword.encode("ascii", "replace"), toCheck.fetchone()[0])


def foo_char_html(inp):
    '''string parsing for rude html trickery
    nothing else should not need to call this'''
    return inp.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# tests:

if __name__ == "__main__":
    db = sqlite3.connect('stories.db')
    c = db.cursor()
    reset(c)
    add_user(c, 1, "Mr. Kats", "qwerty")
    add_story(c, 1, "hello does this website work",  1, 'title title title')
    edit_story(c, 1, "wait i forgot to actually write a story", 1)
    add_user(c, 2, "Mr. Kats' alt account", "qwertzu")
    edit_story(c, 1, "i will circumvent this story editing restriction with an alt account", 2)
    add_story(c, 3, ".", 2, "title 2")
    print(check_user(c, "Mr. Kats", "qwerty"))
    print(hole_story(c, 1))
    c.execute("SELECT username, password FROM users;")
    print(c.fetchall())
    print(all_edit(c, 1))
    db.commit()
    db.close()
    print(foo_char_html("<br/>&copy<source>hello</source>"))
