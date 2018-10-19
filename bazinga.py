import sqlite3

# Come to the computer interaction club. #

def last_story(squul, storyid):
    squul.execute("SELECT lastEdit FROM stories WHERE stories.StoryId = ?;", (storyid, ))
    return squul.fetchall()[0][0]

def hole_story(squul, storyid):
    squul.execute("SELECT content, lastEdit FROM stories WHERE stories.StoryId = ?;", (storyid, ))
    return '\n'.join(squul.fetchall()[0])

def edit_story(squul, storyid, shrext, userid):
    squul.execute("UPDATE stories SET content = ? WHERE stories.StoryId = ?;", (hole_story(squul, storyid), storyid))
    squul.execute("UPDATE stories SET lastEdit = ? WHERE stories.StoryId = ?;", (shrext, storyid))
    squul.execute("UPDATE history SET {} = '.' WHERE history.userId = {};".format('u' + str(storyid), userid))


if __name__ == "__main__":
    db = sqlite3.connect('stories.db')
    c = db.cursor()
    last_story(c, 4321)
    hole_story(c, 4321)
    edit_story(c, 4321, "wow the computer interaction club is so epic", 1877)
    db.commit()
    db.close()
