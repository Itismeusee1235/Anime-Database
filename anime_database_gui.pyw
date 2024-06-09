import tkinter as tk
from tkinter.constants import ANCHOR, END, W
import sqlite3
import difflib
from difflib import SequenceMatcher
import csv
from PIL import Image, ImageTk
from sys import exit

try:
    f = open("anime_list.db", "rb")
    f.close()
except FileNotFoundError:
    exit()

mydb = sqlite3.connect("anime_list.db")
mycursor = mydb.cursor()

table = []
names = []
saved_names = []

src_table = "anime"

entery_format = "INSERT INTO anime(name, stat, episode, comments) VALUES(%s, %d, %s, %s);"
update_format = "UPDATE anime set stat=%d , episode=%s , comments=%s where id=%d"
delete_format = "DELETE FROM anime where id = %d"


def reset():
    load_data()
    typed.set("")
    status.set("")
    episode.set("")
    comments.set("")
    error.set("")
    load(names)
    insert_button.config(state="disabled")
    update_button.config(state="disabled")
    delete_button.config(state="disabled")
    count_label.config(text=str(len(table)))


def load_data():
    global table, names, saved_names
    mycursor.execute("SELECT * FROM %s"%src_table)
    table = [list(data) for data in mycursor]

    for i in range(0, len(table)):
        if table[i][3] is None:
            table[i][3] = ""
        if table[i][4] is None:
            table[i][4] = ""

    names = [name[1] for name in table]
    saved_names = [i.lower() for i in names]


def insert():

    anime_name = typed.get()
    anime_status = status.get()
    anime_episode = episode.get()
    anime_comments = comments.get()

    if anime_status not in ["-2", "-1", "1", "2"]:
        error.set("Invalid status")
        return
    else:
        error.set("")

    anime_status = int(anime_status)

    if anime_episode == "":
        anime_episode = "NULL"
    else:
        anime_episode = '"' + anime_episode + '"'

    if anime_comments == "":
        anime_comments = "NULL"
    else:
        anime_comments = '"' + anime_comments + '"'

    data = ('"' + anime_name + '"', anime_status, anime_episode, anime_comments)
    mycursor.execute(entery_format % data)
    mydb.commit()
    reset()


def update():

    name = typed.get()
    pos = names.index(name)
    data = table[pos]

    anime_id = data[0]
    anime_status = status.get()
    anime_episode = episode.get()
    anime_comments = comments.get()

    if anime_status not in ["-2", "-1", "1", "2"]:
        error.set("Invalid status")
        return
    else:
        error.set("")

    anime_status = int(anime_status)

    if anime_episode == "":
        anime_episode = "NULL"
    else:
        anime_episode = '"' + anime_episode + '"'

    if anime_comments == "":
        anime_comments = "NULL"
    else:
        anime_comments = '"' + anime_comments + '"'

    data = (anime_status, anime_episode, anime_comments, anime_id)
    mycursor.execute(update_format % data)
    mydb.commit()
    reset()


def show():
    name = typed.get()
    pos = names.index(name)
    data = table[pos]

    status.set(data[2])
    episode.set(data[3])
    comments.set(data[4])


def delete():
    name = typed.get()
    pos = names.index(name)
    data = table[pos]

    anime_id = data[0]
    data = (anime_id,)
    mycursor.execute(delete_format % data)
    mydb.commit()
    reset()


def load(data):
    global suggestion_bx

    suggestion_bx.delete(0, END)

    for i in data:
        suggestion_bx.insert(END, i)


def fill(e):
    global search_bx, suggestion_bx

    search_bx.delete(0, END)
    data = suggestion_bx.get(ANCHOR)
    search_bx.insert(0, data)

    insert_button.config(state="disabled")
    update_button.config(state="normal")
    delete_button.config(state="normal")
    show()


def get_similars(name, threshold=0.8):
    similar_names = []

    if name in saved_names:
        pos = saved_names.index(name)
        similar_names.append(names[pos])
        return similar_names

    similars = difflib.get_close_matches(name, saved_names)

    # finding similar entries
    for similar_name in similars:
        if SequenceMatcher(None, name, similar_name).ratio() > threshold:
            pos = saved_names.index(similar_name)
            similar_names.append(names[pos])

    for i in saved_names:
        # Finding entries inside which the name is there
        if (name in i) and (i not in similar_names):
            pos = saved_names.index(i)
            similar_names.append(names[pos])

        # Finding entries which are inside the name
        if i in name:
            pos = saved_names.index(i)
            similar_names.append(names[pos])

    similar_names = list(set(similar_names))

    return similar_names


def check(e):

    if typed.get() == "":
        data = names
        load(data)
        insert_button.config(state="disabled")
        update_button.config(state="disabled")
        delete_button.config(state="disabled")
    else:
        if (typed.get()).lower() in saved_names:
            insert_button.config(state="disabled")
            update_button.config(state="normal")
            delete_button.config(state="normal")
        else:
            insert_button.config(state="normal")
            update_button.config(state="disabled")
            delete_button.config(state="disabled")

        data = get_similars((typed.get()).lower())
        load(data)


def save():
    mycursor.execute("SELECT * FROM anime")
    data = [list(i) for i in mycursor]
    f = open("Anime.csv", "w", newline="")
    writer = csv.writer(f)
    writer.writerow(["ID", "Name", "Status", "Episode", "Comments"])
    writer.writerows(data)
    f.close()

    mycursor.execute("SELECT * FROM Manga")
    data = [list(i) for i in mycursor]
    f = open("Manga.csv", "w", newline="")
    writer = csv.writer(f)
    writer.writerow(["ID", "Name", "Status", "Chapter", "Comments"])
    writer.writerows(data)
    f.close()

    mycursor.execute("SELECT * FROM Light_Novel")
    data = [list(i) for i in mycursor]
    f = open("Light Novel.csv", "w", newline="")
    writer = csv.writer(f)
    writer.writerow(["ID", "Name", "Status", "Chapter", "Comments"])
    writer.writerows(data)
    f.close()


def search():
    anime_status = status.get()
    if anime_status not in ["-2", "-1", "1", "2"]:
        error.set("Invalid status")
        return
    elif anime_status == "":
        reset()
    else:
        error.set("")
    anime_status = int(anime_status)
    animes = []

    for i in table:
        if i[2] == anime_status:
            animes.append(i[1])
    load(animes)
    episode.set("")
    comments.set("")


def switch_src():
    global src_table, entery_format, update_format, delete_format

    if switch_src_button['text'] == "Anime":
        switch_src_button.config(text="Manga")
        src_table = "Manga"
        search_bx_label.config(text="Manga Name:")
        entery_format = "INSERT INTO Manga(name, stat, chapter, comments) VALUES(%s, %d, %s, %s);"
        update_format = "UPDATE Manga set stat=%d , chapter=%s , comments=%s where id=%d"
        delete_format = "DELETE FROM Manga where id = %d"
        episode_label.config(text="Chapter")

    elif switch_src_button['text'] == "Manga":
        switch_src_button.config(text="Light Novel")
        src_table = "Light_Novel"
        search_bx_label.config(text="Light Novel Name:")
        entery_format = "INSERT INTO Light_novel(name, stat, chapter, comments) VALUES(%s, %d, %s, %s);"
        update_format = "UPDATE Light_novel set stat=%d , chapter=%s , comments=%s where id=%d"
        delete_format = "DELETE FROM Light_novel where id = %d"
        episode_label.config(text="Chapter")

    elif switch_src_button['text'] == "Light Novel":
        switch_src_button.config(text="Anime")    
        src_table = "Anime"
        search_bx_label.config(text="Anime Name:")
        entery_format = "INSERT INTO anime(name, stat, episode, comments) VALUES(%s, %d, %s, %s);"
        update_format = "UPDATE anime set stat=%d , episode=%s , comments=%s where id=%d"
        delete_format = "DELETE FROM anime where id = %d"
        episode_label.config(text="Episode")

    reset()


root = tk.Tk()
root.title("Anime Database")
root.geometry("400x300")

reload_img = (Image.open("reload.jpg")).resize((15, 15))
reload_img = ImageTk.PhotoImage(reload_img)

# Creating textvariables ------------------
typed = tk.StringVar()
status = tk.StringVar()
episode = tk.StringVar()
comments = tk.StringVar()
error = tk.StringVar()
error.set("")

# Creating Widgets ----------------------------
search_bx_label = tk.Label(root, text="Anime Name: ", font="Hevetica", anchor=W)
search_bx_label.place(x=0, y=10, width=200, height=20)
search_bx = tk.Entry(root, font="Hevetica", textvariable=typed)
search_bx.place(x=0, y=30, width=300, height=25)

suggestion_bx = tk.Listbox(root, font=("Hevetica", 8))
suggestion_bx.place(x=0, y=60, width=300, height=155)

status_label = tk.Label(root, text="Status: ", font=("Hevetica", 7), anchor=W)
status_label.place(x=0, y=210, width=50, height=25)

status_entry_bx = tk.Entry(root, textvariable=status)
status_entry_bx.place(x=50, y=210, width=250, height=25)

episode_label = tk.Label(root, text="Episode: ", font=("Hevetica", 7), anchor=W)
episode_label.place(x=0, y=235, width=50, height=25)

episode_entry_bx = tk.Entry(root, textvariable=episode)
episode_entry_bx.place(x=50, y=235, width=250, height=25)

comment_label = tk.Label(root, text="Comments: ", font=("Hevetica", 7), anchor=W)
comment_label.place(x=0, y=260, width=50, height=25)

comment_entry_bx = tk.Entry(root, textvariable=comments)
comment_entry_bx.place(x=50, y=260, width=250, height=25)

insert_button = tk.Button(root, text="Insert", font=("Hevetica", 10), command=insert, state="disabled")
insert_button.place(x=300, y=30, width=100, height=45)

search_button = tk.Button(root, text="Search", font=("Hevetica", 10), command=search)
search_button.place(x=300, y=75, width=100, height=45)

update_button = tk.Button(root, text="Update", font=("Hevetica", 10), command=update, state="disabled")
update_button.place(x=300, y=120, width=100, height=45)

delete_button = tk.Button(root, text="Delete", font=("Hevetica", 10), command=delete, state="disabled")
delete_button.place(x=300, y=165, width=100, height=45)

reset_button = tk.Button(root, image=reload_img, command=reset)
reset_button.place(x=380, y=10, width=20, height=20)

switch_src_button = tk.Button(root, text="Anime", font=("Hevetica", 8), command=switch_src)
switch_src_button.place(x=300, y=10, width=80, height=20)

error_label = tk.Label(root, textvariable=error)
error_label.place(x=300, y=210, width=100, height=90)

count_label = tk.Label(root, text=str(len(table)))
count_label.place(x=0, y=285)


reset()

suggestion_bx.bind("<<ListboxSelect>>", fill)

search_bx.bind("<KeyRelease>", check)


def main():
    root.mainloop()
    save()


main()
print("Done")
