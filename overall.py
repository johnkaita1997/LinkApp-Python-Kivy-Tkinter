#PYREBASE FIREBASE
import datetime

import firebase_admin
import pyrebase
from firebase_admin import credentials
from firebase_admin import db
from kivy.properties import StringProperty

location = StringProperty()
username = StringProperty
heading = "Cocab Tech Solutions POS"

cred = credentials.Certificate('privatekey.json')

dbs = firebase_admin.db

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://link-app-2d9a5.firebaseio.com/'
})

ref = db.reference()

firebaseconfig = {
    "apiKey": "AIzaSyDvLAxJeDMLJPZ_l1twsHizfRgKg9zo4V8",
    "authDomain": "link-app-2d9a5.firebaseapp.com",
    "databaseURL": "https://link-app-2d9a5.firebaseio.com/",
    "storageBucket": "link-app-2d9a5.appspot.com"
}

firebase = pyrebase.initialize_app(firebaseconfig)
auth = firebase.auth()

db = firebase.database()


now = datetime.datetime.now()
hour = now.hour
minute = now.minute
second = now.second
combined_date = str(hour) + str(minute) + str(second)