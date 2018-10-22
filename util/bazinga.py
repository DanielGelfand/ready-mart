import sqlite3

# Come to the computer interaction club. #
#squul is cursor
def reset(squul):
    squul.execute("DROP TABLE IF EXISTS stories;")
    squul.execute("DROP TABLE IF EXISTS history;")
    squul.execute("DROP TABLE IF EXISTS users;")

    squul.execute("CREATE TABLE stories (storyid INTEGER PRIMARY KEY, content TEXT, lastedit TEXT);")
    squul.execute("CREATE TABLE history (userid INTEGER PRIMARY KEY);")
    squul.execute("CREATE TABLE users (userid INTEGER PRIMARY KEY, username TEXT, password TEXT);")

def last_story(squul, storyid):
    squul.execute("SELECT lastedit FROM stories WHERE stories.storyid = ?;", (storyid, ))
    return squul.fetchall()[0][0]

def hole_story(squul, storyid):
    squul.execute("SELECT content, lastedit FROM stories WHERE stories.storyid = ?;", (storyid, ))
    return '\n'.join(str(i) for i in squul.fetchall()[0] if i != None)

def edit_story(squul, storyid, shrext, userid):
    if can_edit(squul, storyid, userid):
        squul.execute("UPDATE stories SET content = ? WHERE stories.storyid = ?;", (hole_story(squul, storyid), storyid))
        squul.execute("UPDATE stories SET lastedit = ? WHERE stories.storyid = ?;", (shrext, storyid))
        squul.execute("UPDATE history SET {} = '.' WHERE history.userid = {};".format('s' + str(storyid), userid))

def can_edit(squul, storyid, userid):
    squul.execute("SELECT {} FROM history WHERE history.userid = {};".format('s' + str(storyid), userid))
    return squul.fetchall()[0][0] == 0

def add_story(squul, storyid, shrext, userid,title):
    squul.execute("INSERT INTO stories VALUES(?, ?, ?);", (storyid, title, shrext))
    squul.execute("ALTER TABLE history ADD COLUMN {} INTEGER DEFAULT 0;".format('s' + str(storyid)))
    squul.execute("UPDATE history SET {} = 1 WHERE history.userid = {};".format('s' + str(storyid), userid))

def add_user(squul, userid, username, hashword):
    squul.execute("INSERT INTO users VALUES(?, ?, ?);", (userid, username, hashword))
    squul.execute("INSERT INTO history (userid) VALUES(?);", (userid,));

#Checks whether a user exists in the database
def user_exists(squul,user):
    exist = squul.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username = ?);", (user,))
    return exist.fetchone()[0] == 1

#Checks the user credentials
def check_user(squul,user,pword):
    toCheck = squul.execute("SELECT password from users WHERE username = ?;",(user,))
    return toCheck.fetchone()[0] == pword

# if __name__ == "__main__":
#     db = sqlite3.connect('stories.db')
#     c = db.cursor()
#     add_user(c, 1, "Mr. Kats", "qwerty")
#     add_story(c, 1, "hello does this website work",  1)
#     edit_story(c, 1, "wait i forgot to actually write a story", 1)
#     add_user(c, 2, "Mr. Kats' alt account", "qwertzu")
#     edit_story(c, 1, "i will circumvent this story editing restriction with an alt account", 2)
#     print(hole_story(c, 1))
#     db.commit()
#     db.close()
