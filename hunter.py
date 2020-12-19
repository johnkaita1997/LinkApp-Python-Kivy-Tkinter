import time
from tkinter import *
import pyperclip
import overall


def myclick(text):
    tittle =  title_Text.get()
    description = description_Text.get()
    add_to_Database(tittle, description, text)


def add_to_Database(tittle, description, text):
    #Add to firebase dateabase
    try:
        datte = {}
        datte["date"] = str(overall.now.date())
        datte["description"] = description
        datte["title"] = tittle
        datte["url"] = text

        overall.db.child("links").push(datte)

    except Exception as exception:
        print(title_Text.insert(0, str(exception)))
        print(description_Text.insert(0, str(exception)))

    else:
        root.destroy()

recent_value = pyperclip.paste()
counter = 0
thelink = ''


while True:

    try:
        print("Waiting for changed clipboard...")
        text = pyperclip.paste()

        counter = counter + 1

        if "http" in text:
            if not text == recent_value and not text == '' and not counter == 0:
                print(text)

                recent_value = text

                thelink = text

                root = Tk()
                root.title("app")
                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()
                root.geometry("550x100+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))
                root.configure(background='gold')
                root.lift()
                root.attributes('-topmost', True)

                label = Label(root)
                label.pack()

                title_Text = Entry(root, width=100)
                title_Text.insert(0, 'Tittle')
                title_Text.pack(side=TOP)

                description_Text = Entry(root, width=100)
                description_Text.insert(0, 'Description')
                description_Text.pack(side=TOP)

                mybutton = Button(root, text="Save Link", padx=300, command=lambda : myclick(text), bg='black', fg='white')
                mybutton.pack()

                mainloop()


        time.sleep(2)
    except KeyboardInterrupt:
        break



