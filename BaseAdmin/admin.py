from kivy.config import Config

Config.set('graphics', 'resizable', False)
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup

import webbrowser
import datetime
import tempfile

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView

import overall

Builder.load_file('BaseAdmin/admin.kv')



class TextInputPopup(Popup):
    obj = ObjectProperty(None)
    obj_text = StringProperty("")

    def __init__(self, obj, **kwargs):
        super(TextInputPopup, self).__init__(**kwargs)
        self.obj = obj
        self.obj_text = obj.text


class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableButton(RecycleDataViewBehavior, Button):
    ''' Add selection support to the Button '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    rv = None

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableButton, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableButton, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        self.index = index
        self.rv = rv

    def on_press(self):
        popup = TextInputPopup(self)
        popup.open()

    def get_row_range(self, index: int, num_cols: int) -> range:
        # index - index, which you want the row of
        # num_cols - number of columns in your table
        row = int(index / num_cols)  # the row you want
        return range(row * num_cols, (row + 1) * num_cols)  # the range which that index lies

    def update_changes(self, obj_text):


        # ALERT DIALOG IN  PYTHO
        hello = AdminWindow()
        # Example usage of querying the index '10'
        clicked_index = self.index  # in the event handler get which index was clicked
        num_cols = 4  # your example has 9 columns

        # List
        thelist = []

        for i in self.get_row_range(clicked_index, num_cols):
            thelist.append(self.rv.data[i]["text"])

        date = thelist[0]
        tittle = thelist[1]
        description = thelist[2]
        url = thelist[3]

        hello.openurl(url)





class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.5, .5)


class AdminWindow(BoxLayout):
    data_items = ListProperty([])
    mylocation = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.notify = Notify()
        self.blob_value = None
        self.active = None
        self.prodactive = None
        self.today = datetime.datetime.today()
        self.filename = tempfile.mktemp(".txt")

        self.fectchall()

        self.notify = Notify()

    def openurl(self, text):
        return webbrowser.open(text)


    def search_Description(self):

            inp_description = self.ids.thedescription.text.strip()
            list = []

            if not inp_description:
                self.showAlert("Enter the tittle")
            else:

                ref = overall.dbs.reference('links')
                snapshot = ref.get()

                if not snapshot:
                    self.showAlert("No data")
                else:
                    for value in snapshot.values():
                        date = value['date']
                        description = value['description']
                        title = value['title']
                        url = value['url']

                        if inp_description in description:

                            oldurl = url
                            newurl = ""
                            for i, letter in enumerate(oldurl):
                                if i % 20 == 0:
                                    newurl += '\n'
                                newurl += letter

                            # this is just because at the beginning too a `\n` character gets added
                            newurl = newurl[1:]

                            print(newurl)

                            list.append((date, title, description, newurl))

                            self.data_items = []

                            # create data_items
                            for row in list:
                                for col in row:  self.data_items.append(col)


    def search_Tittle(self):
        inp_tittle = self.ids.thetittle.text.strip()
        list = []

        if not inp_tittle:
            self.showAlert("Enter the tittle")
        else:

            ref = overall.dbs.reference('links')
            snapshot = ref.order_by_child('title').start_at(inp_tittle).end_at(
                inp_tittle + "\uf8ff").get() or ref.order_by_child(
                'title').start_at(inp_tittle.capitalize()).end_at(inp_tittle.capitalize() + "\uf8ff").get()

            if snapshot:

                adate = []
                adescription = []
                atitle = []
                aurl = []

                for value in snapshot.values():
                    date = value['date']
                    adate.append(date)
                    description = value['description']
                    adescription.append(description)
                    title = value['title']
                    atitle.append(title)
                    url = value['url']
                    aurl.append(url)

                    layout = GridLayout(cols=1, row_force_default=True, row_default_height=20, col_default_width=70)

                    layout.add_widget(Label(text=title, color=(.06, .47, .47, 1),
                                            size_hint_x=1, width=40, size_hint_y=None, height=30))

                    layout.add_widget(Label(text=date, halign='left', color=(.06, .47, .47, 1),
                                            size_hint_x=1, width=40, size_hint_y=None, height=30))

                    layout.add_widget(Label(text=description, color=(.06, .47, .47, 1),
                                            size_hint_x=1, width=40, size_hint_y=None, height=30))

                    somebutton = Button(text=url, size_hint_x=1,
                                        on_release=lambda x: self.openurl(somebutton.text.strip()))
                    layout.add_widget(somebutton)

                    oldurl = url
                    newurl = ""
                    for i, letter in enumerate(oldurl):
                        if i % 20 == 0:
                            newurl += '\n'
                        newurl += letter

                    # this is just because at the beginning too a `\n` character gets added
                    newurl = newurl[1:]

                    print(newurl)

                    list.append((date, title, description, newurl))

                    self.data_items = []

                    # create data_items
                    for row in list:
                        for col in row:  self.data_items.append(col)

        pass



    def fectchall(self):

        ref = overall.dbs.reference('links')
        list = []
        snapshot = ref.get()

        if snapshot:
            for value in snapshot.values():
                date = value['date']
                description = value['description']
                title = value['title']
                url = value['url']

                layout = GridLayout(cols=1, row_force_default=True, row_default_height=20, col_default_width=70)

                layout.add_widget(Label(text=title, color=(.06, .47, .47, 1),
                                        size_hint_x=1, width=40, size_hint_y=None, height=30))

                layout.add_widget(Label(text=date, halign='left', color=(.06, .47, .47, 1),
                                        size_hint_x=1, width=40, size_hint_y=None, height=30))

                layout.add_widget(Label(text=description, color=(.06, .47, .47, 1),
                                        size_hint_x=1, width=40, size_hint_y=None, height=30))

                somebutton = Button(text=url, size_hint_x=1,
                                    on_release=lambda x: self.openurl(somebutton.text.strip()))
                layout.add_widget(somebutton)

                oldurl = url
                newurl = ""
                for i, letter in enumerate(oldurl):
                    if i % 20 == 0:
                        newurl += '\n'
                    newurl += letter
                newurl = newurl[1:]

                olddescription = description
                newdescription = ""
                for i, letter in enumerate(olddescription):
                    if i % 20 == 0:
                        newdescription += '\n'
                    newdescription += letter
                newdescription = newdescription[1:]

                list.append((date, title, newdescription, newurl))

                self.data_items = []
                for row in list:
                    for col in row:  self.data_items.append(col)


    def showAlert(self, message):
        self.notify.add_widget(Label(text='[color=#FF0000][b]' + message + '[/b][/color]', markup=True))
        self.notify.open()
        Clock.schedule_once(self.killswitch, 5)


    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()


class AdminApp(App):
    def build(self):
        return AdminWindow()


if __name__ == "__main__":
    active_App = AdminApp()
    active_App.run()
