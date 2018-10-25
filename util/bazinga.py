import sqlite3

# Come to the computer interaction club. #
#squul is cursor

# clears database of all data, rebuilds tables
def reset(squul):
    squul.execute("DROP TABLE IF EXISTS stories;")
    squul.execute("DROP TABLE IF EXISTS history;")
    squul.execute("DROP TABLE IF EXISTS users;")

    squul.execute("CREATE TABLE stories (storyid INTEGER PRIMARY KEY, title TEXT, content TEXT, lastedit TEXT);")
    squul.execute("CREATE TABLE history (storyid INTEGER PRIMARY KEY);")
    squul.execute("CREATE TABLE users (userid INTEGER PRIMARY KEY, username TEXT, password TEXT);")

# last edit of story
def last_story(squul, storyid):
    squul.execute("SELECT lastedit FROM stories WHERE stories.storyid = ?;", (storyid, ))
    return squul.fetchall()[0][0]

# entiretity of story; what would be displayed to a user who edited said story
def hole_story(squul, storyid):
    squul.execute("SELECT content, lastedit FROM stories WHERE stories.storyid = ?;", (storyid, ))
    return '\n'.join(str(i) for i in squul.fetchall()[0] if i != None)

# retrieve story title 
def title_story(squul, storyid):
    squul.execute("SELECT title FROM stories WHERE stories.storyid = ?;", (storyid, ))
    return squul.fetchall()[0][0]
# updates last edit and content of story to reflect edit.
# also updates history to show user has edited story

# TODO: parse the story text for html/sql trickery

def edit_story(squul, storyid, shrext, userid):
    if can_edit(squul, storyid, userid):
        squul.execute("UPDATE stories SET content = ? WHERE stories.storyid = ?;", (hole_story(squul, storyid), storyid))
        squul.execute("UPDATE stories SET lastedit = ? WHERE stories.storyid = ?;", (foo_char_html(shrext), storyid))
        squul.execute("UPDATE history SET {} = 1 WHERE history.storyid = {};".format('u' + str(userid), storyid))

# returns whether a user should be in editing mode for a particular story
# decide whether to display editing mode of story, or which stories to list on users home page.
def can_edit(squul, storyid, userid):
    squul.execute("SELECT {} FROM history WHERE history.storyid =  {};".format('u' + str(userid), storyid))
    return squul.fetchall()[0][0] == 0

def all_edit(squul, userid):
    squul.execute("SELECT * FROM stories INNER JOIN history ON stories.storyid = history.storyid WHERE history.{} = 0;".format('u' + str(userid)))
    return(squul.fetchall())
# creates a new story info in stories and history table

# TODO: currently, people editing story will be unable to see title -- is this our prefered functionality??
# could keep as is, or add seperate title field to display story title.
def add_story(squul, storyid, shrext, userid, title):
    squul.execute("INSERT INTO stories VALUES(?, ?, ?, ?);", (storyid, foo_char_html(title), None, foo_char_html(shrext)))
    squul.execute("INSERT INTO history (storyid) VALUES(?);", (storyid,))
    squul.execute("UPDATE history SET {} = 1 WHERE history.storyid = {};".format('u' + str(userid), storyid))

# creates entries for a new user, both for user and in history database
def add_user(squul, userid, username, hashword):
    squul.execute("INSERT INTO users VALUES(?, ?, ?);", (userid, foo_char_html(username), hashword))
    squul.execute("ALTER TABLE history ADD COLUMN {} INTEGER DEFAULT 0;".format('u' + str(userid)))
# validates a username exists
def user_exists(squul, user):
    exist = squul.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username = ?);", (foo_char_html(user),))
    return exist.fetchone()[0] == 1

# checks if user's password valid
def check_user(squul, user, pword):
    toCheck = squul.execute("SELECT password from users WHERE username = ?;", (foo_char_html(user),))
    return toCheck.fetchone()[0] == pword

# string parsing for rude trickery
def foo_char_html(inp):
    return inp.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# unit tests:

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
    print(hole_story(c, 1))
    
    print(all_edit(c, 1))
    db.commit()
    db.close()
    print(foo_char_html("<br/>&copy<source>hello</source>"))
