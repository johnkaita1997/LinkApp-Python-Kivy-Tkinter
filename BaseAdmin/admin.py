import fpdf
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

Config.set('graphics', 'resizable', False)
from kivy.lang import Builder
from utils.usersrecycler import DataTable
from testmysql import mycursor
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
import pandas as pd
import xlsxwriter

Builder.load_file('BaseAdmin/admin.kv')


class TextInputPopup(Popup):
    obj = ObjectProperty(None)
    obj_text = StringProperty("")

    def __init__(self, obj, **kwargs):
        super(TextInputPopup, self).__init__(**kwargs)
        self.obj = obj
        self.obj_text = obj.text


class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior,
                                  RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableButton(RecycleDataViewBehavior, Button):
    ''' Add selection support to the Button '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

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

    def on_press(self):
        popup = TextInputPopup(self)
        popup.open()

    def update_changes(self, txt, spinnerinput, obj_text):
        # ALERT DIALOG IN  PYTHO
        hello = AdminWindow()
        try:
            mycursor.execute("""UPDATE products SET availability=%s, stock=%s WHERE id=%s""", (spinnerinput, txt, obj_text))
        except:
            hello.showAlert("An error occured")
        else:
            hello.showAlert("Operation was successful")
            hello.reload_screen()


class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.3, .3)


class AdminWindow(BoxLayout):
    data_items = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.notify = Notify()

        # Load those values from the database
        mycursor.execute("SELECT * FROM Active")
        data = mycursor.fetchall()
        self.location = [value[0] for value in data]
        self.username = [value[1] for value in data]

        # Load the recyclerview
        self.get_users_new()

        content = self.ids.scrn_contents
        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

        productContents = self.ids.scrn_product_contents
        products = self.get_products()
        productstable = DataTable(products)
        productContents.add_widget(productstable)

        salesContents = self.ids.display_sales
        sales = self.get_sales()
        salestable = DataTable(sales)
        salesContents.add_widget(salestable)

        self.loadspinners()
        self.loadtheinitiator()

        self.overalldata = {}

    def export_Sales(self):
        sales = self.get_sales()
        data = pd.DataFrame(sales)

        datatoExcel = pd.ExcelWriter("C:\CocabTechSolutionsPos\Sales.xlsx", engine='xlsxwriter')
        data.to_excel(datatoExcel, sheet_name='Sheet1')
        datatoExcel.save()

        toPrintA = '{:>15} {:>10} '.format("", "")
        toPrintB = []

        text_file = open("C:\CocabTechSolutionsPos\Sales.txt", "w")
        text_file.write("Purchase Amount: %s" % data)
        text_file.close()


        pdf = fpdf.FPDF(format='letter')
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.write(5, str(data))
        pdf.ln()
        pdf.output("C:\CocabTechSolutionsPos\Sales.pdf")


    def exportInventory(self):
        sales = self.get_products()
        data = pd.DataFrame(sales)

        datatoExcel = pd.ExcelWriter("C:\CocabTechSolutionsPos\Inventory.xlsx", engine='xlsxwriter')
        data.to_excel(datatoExcel, sheet_name='Sheet1')
        datatoExcel.save()

        text_file = open("C:\CocabTechSolutionsPos\Inventory.txt", "w")
        text_file.write("Purchase Amount: %s" % data)
        text_file.close()

        pdf = fpdf.FPDF(format='letter')
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.write(5, str(data))
        pdf.ln()
        pdf.output("C:\CocabTechSolutionsPos\Inventory.pdf")


    def reload_screen(self):
        # Change Screen
        content = self.ids.display_searched_products
        content.clear_widgets()


    def get_users_new(self):
        mycursor.execute("SELECT * FROM products")
        rows = mycursor.fetchall()
        arrows = str(mycursor.rowcount)
        self.ids.total_inventory.text = arrows + " Products"
        # create data_items
        for row in rows:
            for col in row:
                self.data_items.append(col)


    def loadtheinitiator(self):
        self.sgday = '0'
        self.sgmonth = '0'
        self.sgyear = '0'

        self.egday = '0'
        self.egmonth = '0'
        self.egyear = '0'


    def loadspinners(self):
        # Prepare the spinners
        self.sday = self.ids.sday
        self.sday.values = [str(x) for x in range(31)]
        self.sday.bind(text=self.sssday)

        self.smonth = self.ids.smonth
        self.smonth.values = [str(x) for x in range(12)]
        self.smonth.bind(text=self.sssmonth)

        self.syear = self.ids.syear
        self.syear.values = [str(x) for x in range(2020, 2030)]
        self.syear.bind(text=self.sssyear)

        # Prepare the spinners
        self.eday = self.ids.eday
        self.eday.values = [str(x) for x in range(31)]
        self.eday.bind(text=self.eeeday)

        self.emonth = self.ids.emonth
        self.emonth.values = [str(x) for x in range(12)]
        self.emonth.bind(text=self.eeemonth)

        self.eyear = self.ids.eyear
        self.eyear.values = [str(x) for x in range(2020, 2030)]
        self.eyear.bind(text=self.eeeyear)


    def sssday(self, spinner, text):
        self.sgday = text


    def sssmonth(self, spinner, text):
        self.sgmonth = text


    def sssyear(self, spinner, text):
        self.sgyear = text


    def eeeday(self, spinner, text):
        self.egday = text


    def eeemonth(self, spinner, text):
        self.egmonth = text


    def eeeyear(self, spinner, text):
        self.egyear = text


    def periodicsearch(self):
        beginday = self.sgday
        beginmonth = self.sgmonth
        beginyear = self.sgyear

        endday = self.egday
        endmonth = self.egmonth
        endyear = self.egyear

        mindate = beginyear + "-" + beginmonth + "-" + beginday
        maxdate = endyear + "-" + endmonth + "-" + endday

        print(mindate, maxdate)

        datte = {}
        datte['mindate'] = mindate
        datte['maxdate'] = maxdate

        mycursor.execute("""select * from sales where date >= %s and date <= %s""",
                         (mindate, maxdate))
        data = mycursor.fetchall()

        date = []
        amount = []
        payment = []
        served = []
        location = []
        confirmationcode = []
        customerpay = []
        balance = []

        total = 0.0

        print(data)

        for sale in data:
            retrieve_date = sale[0]
            date.append(retrieve_date)

            retrieve_amount = sale[4]
            amount.append(retrieve_amount)

            retrieve_amount = sale[4]
            amount.append(retrieve_amount)

            retrieve_payment = sale[6]
            payment.append(retrieve_payment)

            retrieve_served = sale[7]
            served.append(retrieve_served)

            retrieve_location = sale[8]
            location.append(retrieve_location)

            retrieve_confirmationcode = sale[11]
            confirmationcode.append(retrieve_confirmationcode)

            retrieve_customerpay = sale[9]
            customerpay.append(retrieve_customerpay)

            retrieve_balance = sale[10]
            balance.append(retrieve_balance)

            total = total + float(retrieve_amount)

        _sales = dict()
        _sales['Date'] = {}
        _sales['Amount'] = {}
        _sales['Payment'] = {}
        _sales['Served'] = {}
        _sales['Location'] = {}
        _sales['Code'] = {}
        _sales['Customerpay'] = {}
        _sales['Balance'] = {}

        users_length = len(date)
        idx = 0
        while idx < users_length:
            _sales['Date'][idx] = date[idx]
            _sales['Amount'][idx] = amount[idx]
            _sales['Payment'][idx] = payment[idx]
            _sales['Served'][idx] = served[idx]
            _sales['Location'][idx] = location[idx]
            _sales['Code'][idx] = confirmationcode[idx]
            _sales['Customerpay'][idx] = customerpay[idx]
            _sales['Balance'][idx] = balance[idx]

            idx += 1

        # Change the text values
        self.ids.total_sales_select.text = "TOTAL SALES :     KES:" + " " + str(total)
        # Change Screen
        content = self.ids.display_sales
        content.clear_widgets()
        salestable = DataTable(_sales)
        content.add_widget(salestable)


    def logout(self):
        self.parent.parent.current = 'scrn_login'


    def search_Field(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        self.crud_search_word = TextInput(hint_text='Enter Product Code || Product name')
        # Load the values from the database
        crud_search_criteria = Spinner(text='code', values=['code', 'name'])
        crud_submit = Button(text='Search', size_hint_x=None, width=100,
                             on_release=lambda x: self.dotheSearch(self.crud_search_word.text, crud_search_criteria.text))

        target.add_widget(self.crud_search_word)
        target.add_widget(crud_search_criteria)
        target.add_widget(crud_submit)


    def dotheSearch(self, searchWord, searchCriteria):
        content = self.ids.display_searched_products
        content.clear_widgets()

        if searchCriteria == '' or searchWord == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 3)
        else:

            if searchCriteria == 'code':
                mycursor.execute("SELECT * FROM products WHERE code LIKE %s", ("%" + searchWord + "%",))
            elif searchCriteria == 'name':
                mycursor.execute("SELECT * FROM products WHERE name LIKE %s", ("%" + searchWord + "%",))

        data = mycursor.fetchall()  # get the data in data variabl

        name = [value[3] for value in data]
        code = [value[2] for value in data]
        buyingprice = [value[0] for value in data]
        sellingprice = [value[4] for value in data]
        category = [value[1] for value in data]

        _products = dict()
        _products['name'] = {}
        _products['code'] = {}
        _products['buyingprice'] = {}
        _products['sellingprice'] = {}
        _products['category'] = {}

        users_length = len(name)
        idx = 0
        while idx < users_length:
            _products['name'][idx] = name[idx]
            _products['code'][idx] = code[idx]
            _products['buyingprice'][idx] = buyingprice[idx]
            _products['sellingprice'][idx] = sellingprice[idx]
            _products['category'][idx] = category[idx]

            idx += 1

        # Change Screen
        self.ids.scrn_mngr.current = 'screen_search_product'

        # Change the text values
        self.ids.total_sales.text = [sum((float(value[4]) for value in data))]

        productContents = self.ids.display_searched_products
        productstable = DataTable(_products)
        productContents.add_widget(productstable)
        print(productstable)

        self.crud_search_word.text = ''


    def view_categories(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        mycursor.execute("SELECT * FROM categorylist")
        data = mycursor.fetchall()  # get the data in data variabl
        prods = [value[0] for value in data]

        # Load the values from the database
        crud_category = Spinner(text='Select', values=prods)
        crud_submit = Button(text='View', size_hint_x=None, width=100,
                             on_release=lambda x: self.show_product_in_chosen_categories(crud_category.text))

        target.add_widget(crud_category)
        target.add_widget(crud_submit)


    def show_product_in_chosen_categories(self, crud_category):
        content = self.ids.display_categorized_products
        content.clear_widgets()
        mycursor.execute("SELECT * FROM products WHERE category=%s", (crud_category))
        data = mycursor.fetchall()  # get the data in data variabl

        name = [value[3] for value in data]
        code = [value[2] for value in data]
        buyingprice = [value[0] for value in data]
        sellingprice = [value[4] for value in data]
        category = [value[1] for value in data]

        _products = dict()
        _products['name'] = {}
        _products['code'] = {}
        _products['buyingprice'] = {}
        _products['sellingprice'] = {}
        _products['category'] = {}

        users_length = len(name)
        idx = 0
        while idx < users_length:
            _products['name'][idx] = name[idx]
            _products['code'][idx] = code[idx]
            _products['buyingprice'][idx] = buyingprice[idx]
            _products['sellingprice'][idx] = sellingprice[idx]
            _products['category'][idx] = category[idx]

            idx += 1

        # Change Screen
        self.ids.scrn_mngr.current = 'scrn_product_categorized'

        productContents = self.ids.display_categorized_products
        productstable = DataTable(_products)
        productContents.add_widget(productstable)
        print(productstable)


    def remove_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        self.crud_code = TextInput(hint_text='Product Code')
        crud_submit = Button(text='Remove', size_hint_x=None, width=100,
                             on_release=lambda x: self.remove_product(self.crud_code.text))

        target.add_widget(self.crud_code)
        target.add_widget(crud_submit)


    def remove_product(self, code):
        if code == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 3)
        else:

            # ALERT DIALOG IN  PYTHON
            try:
                mycursor.execute("DELETE FROM products WHERE code=%s" % (code,))
            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

        content = self.ids.scrn_product_contents
        content.clear_widgets()
        self.crud_code.text = ''

        prodz = self.get_products()
        stocktable = DataTable(table=prodz)
        content.add_widget(stocktable)


    def update_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        crud_code = TextInput(hint_text='Product Code', multiline=False, write_tab=False)
        crud_name = TextInput(hint_text='Product Name', multiline=False, write_tab=False)
        crud_buyingprice = TextInput(hint_text='Buying Price', multiline=False, write_tab=False)
        crud_selling_price = TextInput(hint_text='Selling Price', multiline=False, write_tab=False)

        prods = self.db.child("MainPos").child("categorylist").get().val()
        print(prods)
        # Load the values from the database
        crud_category = Spinner(text='Prod Category', values=prods.values())
        crud_submit = Button(text='Add', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_product(crud_code.text, crud_name.text,
                                                                   crud_buyingprice.text, crud_selling_price.text,
                                                                   crud_category.text))

        target.add_widget(crud_code)
        target.add_widget(crud_name)
        target.add_widget(crud_buyingprice)
        target.add_widget(crud_selling_price)
        target.add_widget(crud_category)
        target.add_widget(crud_submit)


    def update_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        self.crud_code = TextInput(hint_text='Product Code', multiline=False, write_tab=False)
        self.crud_name = TextInput(hint_text='Update Name', multiline=False, write_tab=False)
        self.crud_buyingprice = TextInput(hint_text='New B.price', multiline=False, write_tab=False)
        self.crud_selling_price = TextInput(hint_text='New S.Price', multiline=False, write_tab=False)

        mycursor.execute("SELECT * FROM categorylist")
        data = mycursor.fetchall()  # get the data in data variabl
        prods = [value[0] for value in data]

        # Load the values from the database
        crud_category = Spinner(text='Prod Category', values=prods)
        crud_submit = Button(text='Update', size_hint_x=None, width=100,
                             on_release=lambda x: self.update_product(self.crud_code.text, self.crud_name.text,
                                                                      self.crud_buyingprice.text,
                                                                      self.crud_selling_price.text,
                                                                      crud_category.text))

        target.add_widget(self.crud_code)
        target.add_widget(self.crud_name)
        target.add_widget(self.crud_buyingprice)
        target.add_widget(self.crud_selling_price)
        target.add_widget(crud_category)
        target.add_widget(crud_submit)


    def update_product(self, code, name, buyingprice, sellingprice, category):
        x = name
        y = ("-".join(x.split()))

        datte = {}
        datte["code"] = code
        datte["name"] = y
        datte["buyingprice"] = buyingprice
        datte["sellingprice"] = sellingprice
        datte["category"] = category

        if code == '' or name == '' or buyingprice == '' or sellingprice == '' or category == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 3)
        else:
            try:
                mycursor.execute(
                    """INSERT INTO products (code, name, buyingprice, sellingprice, category)  VALUES (%(code)s, %(name)s,  %(buyingprice)s,  %(sellingprice)s, %(category)s)""",
                    datte)
            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

        content = self.ids.scrn_product_contents
        content.clear_widgets()

        self.crud_code.text = ''
        self.crud_name.text = ''
        self.crud_buyingprice.text = ''
        self.crud_selling_price.text = ''
        self.crud_code.text = ''
        self.crud_code.text = ''

        users = self.get_products()
        userstable = DataTable(table=users)
        content.add_widget(userstable)


    def add_product_category_field(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        self.categoryName = TextInput(hint_text='Name of the category', multiline=False, write_tab=False)
        crud_submit = Button(text='Add Category', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_product_category(self.categoryName.text))

        target.add_widget(self.categoryName)
        target.add_widget(crud_submit)


    def add_product_category(self, categoryName):
        if categoryName == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 3)

        else:

            datte = {}
            datte["name"] = categoryName

            try:
                mycursor.execute("""INSERT INTO categorylist (name)  VALUES (%(name)s)""", datte)
            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

        # content = self.ids.scrn_product_contents
        # content.clear_widgets()

        self.categoryName.text = ''


    def change_screen(self, instance):
        if instance.text == 'Manage Products':
            self.ids.scrn_mngr.current = 'scrn_product_content'

        elif instance.text == 'Manage Users':
            self.ids.scrn_mngr.current = 'scrn_content_manage_users'

        elif instance.text == 'Point Of Sale':
            self.parent.parent.current = 'scrn_pos'

        elif instance.text == 'Sales':
            self.ids.scrn_mngr.current = 'screen_display_sales'

        elif instance.text == 'Inventory':
            self.ids.scrn_mngr.current = 'screen_inventory'
        else:
            pass


    def add_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        self.crud_code = TextInput(hint_text='Product Code', multiline=False, write_tab=False)
        self.crud_name = TextInput(hint_text='Product Name', multiline=False, write_tab=False)
        self.crud_buyingprice = TextInput(hint_text='Buying Price', multiline=False, write_tab=False)
        self.crud_selling_price = TextInput(hint_text='Selling Price', multiline=False, write_tab=False)

        mycursor.execute("SELECT * FROM categorylist")
        data = mycursor.fetchall()  # get the data in data variabl
        prods = [value[0] for value in data]
        # Load the values from the database
        crud_category = Spinner(text='Prod Category', values=prods)
        crud_submit = Button(text='Add', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_product(self.crud_code.text, self.crud_name.text,
                                                                   self.crud_buyingprice.text, self.crud_selling_price.text,
                                                                   crud_category.text))

        target.add_widget(self.crud_code)
        target.add_widget(self.crud_name)
        target.add_widget(self.crud_buyingprice)
        target.add_widget(self.crud_selling_price)
        target.add_widget(crud_category)
        target.add_widget(crud_submit)


    def add_product(self, code, name, buyingprice, sellingprice, category):
        x = name
        y = ("-".join(x.split()))

        datte = {}
        datte["code"] = code
        datte["name"] = y
        datte["buyingprice"] = buyingprice
        datte["sellingprice"] = sellingprice
        datte["category"] = category
        datte["location"] = str(self.location[0])

        if code == '' or name == '' or buyingprice == '' or sellingprice == '' or category == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 3)
        else:
            try:
                mycursor.execute(
                    """INSERT INTO products (code, name, buyingprice, sellingprice, category, location)  VALUES (%(code)s, %(name)s,  %(buyingprice)s,  %(sellingprice)s,%(category)s,  %(location)s)""",
                    datte)
            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

        content = self.ids.scrn_product_contents
        content.clear_widgets()

        # Empty the widgets
        self.crud_code.text = ''
        self.crud_name.text = ''
        self.crud_buyingprice.text = ''
        self.crud_selling_price.text = ''

        users = self.get_products()
        userstable = DataTable(table=users)
        content.add_widget(userstable)


    def remove_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        self.user = TextInput(hint_text='Id Number')
        crud_submit = Button(text='Remove', size_hint_x=None, width=100,
                             on_release=lambda x: self.remove_user(self.user.text))

        target.add_widget(self.user)
        target.add_widget(crud_submit)


    def showAlert(self, message):
        self.notify.add_widget(Label(text='[color=#FF0000][b]' + message + '[/b][/color]', markup=True))
        self.notify.open()
        Clock.schedule_once(self.killswitch, 3)


    def remove_user(self, user):
        if user == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 3)
        else:

            try:
                mycursor.execute("DELETE FROM users WHERE uid=%s" % (user,))
            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

        self.user.text = ''
        content = self.ids.scrn_contents
        content.clear_widgets()

        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)


    def update_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()

        self.name = TextInput(hint_text='Both Names', multiline=False, write_tab=False)
        self.theid = TextInput(hint_text='id', multiline=False, write_tab=False)
        self.mobile = TextInput(hint_text='Mobile', multiline=False, write_tab=False)
        designation = Spinner(text='Operator', values=['Operator', 'Administrator'])
        crud_submit = Button(text='Update', size_hint_x=None, width=100,
                             on_release=lambda x: self.update_user(self.name.text, self.theid.text, designation.text,
                                                                   self.mobile.text))

        target.add_widget(self.name)
        target.add_widget(self.theid)
        target.add_widget(designation)
        target.add_widget(self.mobile)
        target.add_widget(crud_submit)


    def update_user(self, name, id, mobile, designation):
        if name == '' or id == '' or mobile == '' or designation == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 3)

        else:

            datte = {}
            datte["name"] = name
            datte["mobile"] = mobile
            datte["uid"] = id
            datte["designation"] = designation

            try:
                mycursor.execute("""UPDATE users SET name=%s, mobile=%s, id=%s, designation=%s WHERE uid=%s""",
                                 (name, mobile, id, designation, id))
            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

            content = self.ids.scrn_contents
            content.clear_widgets()

            users = self.get_users()
            userstable = DataTable(table=users)
            content.add_widget(userstable)

            # Empty the widgets
            self.name.text = ''
            self.theid.text = ''
            self.mobile.text = ''


    def add_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()

        self.bothnames = TextInput(hint_text='Both Names', multiline=False, write_tab=False)
        self.mobile = TextInput(hint_text='Mobile', multiline=False, write_tab=False)
        self.idnumber = TextInput(hint_text='Id Number', multiline=False, write_tab=False)
        designation = Spinner(text='Operator', values=['Operator', 'Administrator'])

        crud_submit = Button(text='Add', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_user(self.bothnames.text, self.mobile.text, self.idnumber.text,
                                                                designation.text))

        target.add_widget(self.bothnames)
        target.add_widget(self.mobile)
        target.add_widget(self.idnumber)
        target.add_widget(designation)
        target.add_widget(crud_submit)


    def add_user(self, bothnames, mobile, idnumber, designation):
        datte = {}
        datte["name"] = bothnames
        datte["mobile"] = mobile
        datte["uid"] = idnumber
        datte["designation"] = designation
        datte["location"] = str(self.location[0])

        if (bothnames == '' or mobile == '' or idnumber == '' or designation == ''):
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 3)
        else:

            try:
                mycursor.execute(
                    """INSERT INTO Users (name, mobile, uid, designation, location)  VALUES (%(name)s, %(mobile)s,  %(uid)s,  %(designation)s, %(location)s)""",
                    datte)
            except:
                self.showAlert("An error occured")
            else:
                self.showAlert("Operation was successful")

        content = self.ids.scrn_contents
        content.clear_widgets()

        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

        self.bothnames.text = ''
        self.mobile.text = ''
        self.idnumber.text = ''


    def get_users(self):
        mycursor.execute("SELECT * FROM Users")
        data = mycursor.fetchall()
        name = []
        mobile = []
        id = []
        designation = []

        for user in data:
            retrieve_name = user[0]
            name.append(retrieve_name)

            retrieve_mobile = user[2]
            mobile.append(retrieve_mobile)

            retrieve_id = user[3]
            id.append(retrieve_id)

            retrieve_designation = user[1]
            designation.append(retrieve_designation)

        _users = dict()
        _users['Name'] = {}
        _users['Mobile'] = {}
        _users['Id Number'] = {}
        _users['Designation'] = {}

        users_length = len(name)
        idx = 0
        while idx < users_length:
            _users['Name'][idx] = name[idx]
            _users['Mobile'][idx] = mobile[idx]
            _users['Id Number'][idx] = id[idx]
            _users['Designation'][idx] = designation[idx]

            idx += 1

        return _users


    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()


    def get_sales(self):
        mycursor.execute("SELECT * FROM sales")
        data = mycursor.fetchall()
        date = []
        amount = []
        payment = []
        served = []
        location = []
        confirmationcode = []
        customerpay = []
        balance = []

        self.overalldata = data

        for sale in data:
            retrieve_date = sale[0]
            date.append(retrieve_date)

            retrieve_amount = sale[4]
            amount.append(retrieve_amount)

            retrieve_amount = sale[4]
            amount.append(retrieve_amount)

            retrieve_payment = sale[6]
            payment.append(retrieve_payment)

            retrieve_served = sale[7]
            served.append(retrieve_served)

            retrieve_location = sale[8]
            location.append(retrieve_location)

            retrieve_confirmationcode = sale[11]
            confirmationcode.append(retrieve_confirmationcode)

            retrieve_customerpay = sale[9]
            customerpay.append(retrieve_customerpay)

            retrieve_balance = sale[10]
            balance.append(retrieve_balance)

        _sales = dict()
        _sales['Date'] = {}
        _sales['Amount'] = {}
        _sales['Payment'] = {}
        _sales['Served'] = {}
        _sales['Location'] = {}
        _sales['Code'] = {}
        _sales['Customerpay'] = {}
        _sales['Balance'] = {}

        users_length = len(date)
        idx = 0
        while idx < users_length:
            _sales['Date'][idx] = date[idx]
            _sales['Amount'][idx] = amount[idx]
            _sales['Payment'][idx] = payment[idx]
            _sales['Served'][idx] = served[idx]
            _sales['Location'][idx] = location[idx]
            _sales['Code'][idx] = confirmationcode[idx]
            _sales['Customerpay'][idx] = customerpay[idx]
            _sales['Balance'][idx] = balance[idx]

            idx += 1

        return _sales


    def get_products(self):
        mycursor.execute("SELECT * FROM products ")
        data = mycursor.fetchall()

        name = []
        code = []
        buyingprice = []
        sellingprice = []
        category = []

        for user in data:
            retrieve_name = user[3]
            name.append(retrieve_name)

            retrieve_code = user[2]
            code.append(retrieve_code)

            retrieve_buyingprice = user[0]
            buyingprice.append(retrieve_buyingprice)

            retrieve_sellingprice = user[4]
            sellingprice.append(retrieve_sellingprice)

            retrieve_category = user[1]
            category.append(retrieve_category)

        _products = dict()
        _products['Name'] = {}
        _products['Code'] = {}
        _products['Buyingprice'] = {}
        _products['Sellingprice'] = {}
        _products['Category'] = {}

        users_length = len(name)
        idx = 0
        while idx < users_length:
            _products['Name'][idx] = name[idx]
            _products['Code'][idx] = code[idx]
            _products['Buyingprice'][idx] = buyingprice[idx]
            _products['Sellingprice'][idx] = sellingprice[idx]
            _products['Category'][idx] = category[idx]

            idx += 1

        return _products


    def searchForTheDates(self):
        beginday = self.sgday
        beginmonth = self.sgmonth
        beginyear = self.sgyear

        endday = self.egday
        endmonth = self.egmonth
        endyear = self.egyear

        mindate = beginyear + "-" + beginmonth + "-" + beginday
        maxdate = endyear + "-" + endmonth + "-" + endday

        print(mindate, maxdate)

        datte = {}
        datte['mindate'] = mindate
        datte['maxdate'] = maxdate

        print("Min " + mindate + "\n" + "Max " + maxdate)

        mycursor.execute("""select * from sales where date >= %s and date <= %s""",
                         (mindate, maxdate))
        data = mycursor.fetchall()

        date = []
        amount = []
        payment = []
        served = []
        location = []
        confirmationcode = []
        customerpay = []
        balance = []

        total = 0.0

        for sale in data:
            retrieve_date = sale[0]
            date.append(retrieve_date)

            retrieve_amount = sale[4]
            amount.append(retrieve_amount)

            retrieve_amount = sale[4]
            amount.append(retrieve_amount)

            retrieve_payment = sale[6]
            payment.append(retrieve_payment)

            retrieve_served = sale[7]
            served.append(retrieve_served)

            retrieve_location = sale[8]
            location.append(retrieve_location)

            retrieve_confirmationcode = sale[11]
            confirmationcode.append(retrieve_confirmationcode)

            retrieve_customerpay = sale[9]
            customerpay.append(retrieve_customerpay)

            retrieve_balance = sale[10]
            balance.append(retrieve_balance)

            total = total + float(retrieve_amount)

        _sales = dict()
        _sales['Date'] = {}
        _sales['Amount'] = {}
        _sales['Payment'] = {}
        _sales['Served'] = {}
        _sales['Location'] = {}
        _sales['Code'] = {}
        _sales['Customerpay'] = {}
        _sales['Balance'] = {}

        users_length = len(date)
        idx = 0
        while idx < users_length:
            _sales['Date'][idx] = date[idx]
            _sales['Amount'][idx] = amount[idx]
            _sales['Payment'][idx] = payment[idx]
            _sales['Served'][idx] = served[idx]
            _sales['Location'][idx] = location[idx]
            _sales['Code'][idx] = confirmationcode[idx]
            _sales['Customerpay'][idx] = customerpay[idx]
            _sales['Balance'][idx] = balance[idx]

            idx += 1

        # Change Screen
        content = self.ids.display_sales
        content.clear_widgets()
        salestable = DataTable(_sales)
        content.add_widget(salestable)

        # Try and get the total then update everything
        expensestext = self.ids.the_sales.text
        expenses = float(expensestext)
        sales = sum((float(value[4]) for value in data))

        finalmessage = 'Sales : ' + str(sales) + "\n" + 'Expenses : ' + str(expenses) + "\n"

        if (expenses == sales):
            finalmessage = finalmessage + "Profit = 0.00,   Loss = 0.00"
        elif (expenses < sales):
            finalmessage = finalmessage + "Profit: " + str(sales - expenses)
        elif (expenses > sales):
            finalmessage = finalmessage + "Loss: " + str(expenses - sales)

        # Change the text values

        self.notify.add_widget(Label(text='[color=#FF0000][b]' + str(finalmessage) + '[/b][/color]', markup=True))
        self.notify.open()
        Clock.schedule_once(self.killswitch, 3)

        # content.clear_widgets()
        # result_thesales = self.ids.the_sales.text
        #
        # if result_thesales == '':
        #     self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
        #     self.notify.open()
        #     Clock.schedule_once(self.killswitch, 3)
        # else:
        #     ref = db.reference('MainPos').child('sales')
        #     snapshot = ref.order_by_child('date').start_at(result_thesales).end_at(result_thesales + "\uf8ff").get()
        #
        #     payment = [value['payment'] for value in snapshot.values()]
        #     date = [value['date'] for value in snapshot.values()]
        #     amount = [value['amount'] for value in snapshot.values()]
        #     number = [value['number'] for value in snapshot.values()]
        #
        #     _sales = dict()
        #     _sales['payment'] = {}
        #     _sales['date'] = {}
        #     _sales['amount'] = {}
        #     _sales['number'] = {}
        #
        #     users_length = len(amount)
        #     idx = 0
        #
        #     while idx < users_length:
        #         _sales['payment'][idx] = payment[idx]
        #         _sales['date'][idx] = date[idx]
        #         _sales['amount'][idx] = amount[idx]
        #         _sales['number'][idx] = number[idx]
        #
        #         idx += 1
        #
        #     # Change Screen
        #     self.ids.scrn_mngr.current = 'screen_display_sales'
        #
        #     secondSales = self.ids.display_sales
        #     thesalesresults = DataTable(_sales)
        #     secondSales.add_widget(thesalesresults)


class AdminApp(App):
    def build(self):
        return AdminWindow()


if __name__ == "__main__":
    active_App = AdminApp()
    active_App.run()
