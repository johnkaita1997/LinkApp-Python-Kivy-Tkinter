from kivy.app import App
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from testmysql import mycursor, seccursor, db
import overall

Config.set('graphics', 'resizable', False)
from pyrebase import pyrebase


Builder.load_file('BaseLogin/login.kv')

class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.3, .3)


class LoginWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        db.autocommit = True

        self.firebaseconfig = {
            "apiKey": "AIzaSyDGsXv0wa7Fc4irPi3MX_uWTIfuWHeEIzU",
            "authDomain": "projectId.firebaseapp.com",
            "databaseURL": "https://cocabpos-e5199.firebaseio.com/",
            "storageBucket": "projectId.appspot.com"
        }

        self.firebase = pyrebase.initialize_app(self.firebaseconfig)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()

        self.ulocation = ''
        self.uusername= ''

        self.notify = Notify()
        self.branch = self.ids.branch

        #Load the values for the spinner
        # Get the credential using password
        mycursor.execute('SELECT * FROM  braches')
        data = mycursor.fetchall()  # get the data in data variabl
        newList = [value[0] for value in data]
        self.branch.values = newList
        # Add the spinner onclickListener
        self.branch.bind(text=self.on_spinner_select)

    def Convert(lst):
        res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
        return res_dct

    def on_spinner_select(self, spinner, text):
        self.spinnertext = text
        # Add Widgets to
        self.ulocation = self.spinnertext
        #Add the active location to the database


    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()

    def login_user(self):
        if(self.ulocation == ''):
            self.notify.add_widget(Label(text='[color=#FF0000][b]Select location[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 3)
        else:
            theemail = self.ids.email.text
            thepassword = self.ids.password.text

            if theemail ==  '' or thepassword == '':
                self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 3)

            else:
                mycursor.execute("SELECT * FROM Users WHERE uid=%s", (thepassword,))
                data = mycursor.fetchone()  # get the data in data variabl

                if data:
                    seccursor.execute('SELECT   *  FROM Users WHERE uid=%s', (thepassword,))
                    secdata = seccursor.fetchone()
                    self.uusername = secdata
                    print(str(self.uusername[0]))

                    name = 'john'
                    mycursor.execute("DELETE  FROM active")
                    mycursor.execute("""INSERT INTO Active (location, username)  VALUES (%(location)s, %(username)s)""",
                                {'location': self.ulocation,
                                 'username': str(self.uusername[0])})

                    print('Done')

                    operator = data[1]
                    if operator == 'Administrator':
                        self.parent.parent.current = 'scrn_admin'
                    elif operator == 'Operator':
                        self.parent.parent.current = 'scrn_pos'
                    else:
                        self.notify.add_widget(Label(text='[color=#FF0000][b]An error occured[/b][/color]', markup=True))
                        self.notify.open()
                        Clock.schedule_once(self.killswitch, 3)

                else:
                    self.notify.add_widget(Label(text='[color=#FF0000][b]Wrong Credentials[/b][/color]', markup=True))
                    self.notify.open()
                    Clock.schedule_once(self.killswitch, 3)


class LogInApp(App):
    def build(self):
        return LoginWindow()


if __name__ == "__main__":
    active_App = LogInApp()
    active_App.run()
