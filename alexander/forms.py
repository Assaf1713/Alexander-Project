
from django import forms
from .models import Admin_Highlights, Cashier_Orders, Employee, Shift_Preferences, Suppliers, User, User_Permissions, Users_in_Shifts
from .models import Products_In_Cashier_Orders, Raw_Materials, Products_In_Order
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
# Cashier orders


# This form is used to create a new order
class CashierOrderForm(forms.ModelForm):
    PickUp_Date = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date'}), label='בחר תאריך לאיסוף')

    class Meta:
        model = Cashier_Orders
        fields = ['Order_Type', 'Customer_Name',
                  'Customer_Last_Name', 'PickUp_Date', 'IsPaid', 'Comments']
        labels = {
            'Order_Type': 'סוג הזמנה',
            'Customer_Name': 'שם הלקוח',
            'Customer_Last_Name': 'שם משפחה',
            'PickUp_Date': 'בחר תאריך לאיסוף',
            'IsPaid': 'האם הזמנה שולמה',
            'Comments': 'הערות',
        }


# This form is used to add products to an order
class AddProductToOrderForm(forms.ModelForm):
    class Meta:
        model = Products_In_Cashier_Orders
        fields = ['product', 'quantity', 'comments']

        labels = {
            'product': 'בחר מוצר',
            'quantity': 'בחר כמות',
            'comments': 'הוסף הערה',
        }


# Raw_Materials


# This form is used to search for raw materials in the stock page
class StockSearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False)


# This form is used to search for orders in the orders page
class OrderSearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False)
    # add a place holder to the search bar
    query.widget.attrs.update({'placeholder': ' הכנס שם לקוח'})


# This form is used to update the quantity of a raw material
class UpdateQuantityForm(forms.ModelForm):
    class Meta:
        model = Raw_Materials
        fields = ['Quantity']
        labels = {
            'Quantity': 'כמות'
        }
        widgets = {
            'Quantity': forms.NumberInput(attrs={'min': 0})
        }


# This form is used to update the supplier of a raw material
class UpdateSupplierForm(forms.ModelForm):
    class Meta:
        model = Raw_Materials
        fields = ['Supplier']
        labels = {
            'Supplier': 'עדכן ספק'
        }
        widgets = {
            'Supplier': forms.Select(attrs={'placeholder': 'בחר ספק'})
        }


# This form is used to update the price of a raw material
class UpdatePriceForm(forms.ModelForm):
    class Meta:
        model = Raw_Materials
        fields = ['Price']
        labels = {
            'Price': 'עדכן מחיר'
        }
        widgets = {
            'Price': forms.NumberInput(attrs={'min': 0})
        }


class AddRawMaterialForm(forms.ModelForm):
    class Meta:
        model = Products_In_Order
        fields = ['Item', 'Quantity']
        labels = {
            'Item': 'בחר חומר גלם',
            'Quantity': 'כמות',
        }

        widgets = {
            'Item': forms.Select(attrs={'class': 'form-control'}),
            'Quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class AddHighlightForm(forms.ModelForm):
    Due_Date = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date'}), label='תאריך יעד')

    class Meta:
        model = Admin_Highlights
        fields = ['Type', 'Due_Date', 'Text']
        labels = {
            'Type': ' קהל היעד ',
            'Due_Date': 'תאריך יעד',
            'Text': ' תוכן הודעה',
        }
        widgets = {
            'Type': forms.Select(attrs={'class': 'form-control'}),
            'Text': forms.Textarea(attrs={'class': 'form-control'}),
        }


class CreateRawMaterialsForm(forms.ModelForm):
    class Meta:
        model = Raw_Materials
        fields = ['Material_Name', 'Lower_Barrier',
                  'Unit', 'Price', 'Supplier', 'Quantity']
        labels = {
            'Material_Name': 'שם חומר גלם',
            'Lower_Barrier': 'רף תחתון',
            'Unit': 'יחידה',
            'Price': 'מחיר',
            'Supplier': 'ספק',
            'Quantity': 'כמות',
        }
        widgets = {
            'Material_Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Lower_Barrier': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'Unit': forms.TextInput(attrs={'class': 'form-control'}),
            'Price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'Supplier': forms.Select(attrs={'class': 'form-control'}),
            'Quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class CreateSuppliersForm(forms.ModelForm):
    class Meta:
        model = Suppliers
        fields = ['Name', 'phone', 'Email']
        labels = {
            'Name': 'שם ספק',
            'phone': 'טלפון',
            'Email': 'אימייל',
        }
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'},),
            'Email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

        error_messages = {
            'Name': {
                'required': "אנא הכנס את שם הספק",
                'max_length': "שם הספק חייב להיות פחות מ-50 תווים",
            },
            'phone': {
                'required': "אנא הכנס מספר טלפון",
                'invalid': "מספר הטלפון חייב להיות בין 9 ל-15 ספרות",
            },
            'Email': {
                'invalid': "אנא הכנס כתובת אימייל תקינה",
            },
        }

# this form is used to create a new employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['Employee_ID', 'First_Name', 'Last_Name',
                  'Birthday', 'Email', 'phone_number']
        labels = {
            'Employee_ID': 'תעודת זהות',
            'First_Name': 'שם פרטי',
            'Last_Name': 'שם משפחה',
            'Birthday': 'תאריך לידה',
            'Email': 'אימייל',
            'phone_number': 'מספר טלפון',
        }
        widgets = {
            'Employee_ID': forms.TextInput(attrs={'class': 'form-control'}),
            'First_Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Last_Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


# this form is used to create a new user
class UserForm(forms.ModelForm):
    Password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['Username', 'Type', 'Password']
        labels = {
            'Username': 'שם משתמש',
            'Type': 'סוג משתמש',
            'Password': 'סיסמא',
        }
        widgets = {
            'Username': forms.TextInput(attrs={'class': 'form-control'}),
            'Type': forms.Select(attrs={'class': 'form-control'}),
            'Password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

# this form is used to update an employee


class UpdateEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['phone_number', 'Email']
        labels = {
            'phone_number': 'מספר טלפון',
            'Email': 'אימייל',
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'phone_number': {
                'required': "אנא הכנס מספר טלפון",
                'invalid': "מספר הטלפון חייב להיות בין 9 ל-15 ספרות",
            },
            'Email': {
                'invalid': "אנא הכנס כתובת אימייל תקינה",
            },
        }

# this form is used to update a user


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['Username', 'Password']
        labels = {
            'Username': 'שם משתמש',
            'Password': 'סיסמא',
        }
        widgets = {
            'Username': forms.TextInput(attrs={'class': 'form-control'}),
            'Password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'Username': {
                'required': "אנא הכנס שם משתמש",
                'max_length': "שם המשתמש חייב להיות פחות מ-50 תווים",
            },
            'Password': {
                'required': "אנא הכנס סיסמא",
                'max_length': "הסיסמא חייבת להיות פחות מ-50 תווים",
            },
        }

# this form is used to update the permissions of a user


class UserPermissionsForm(forms.ModelForm):
    class Meta:
        model = User_Permissions
        fields = ['Is_Granted']
        widgets = {
            'Is_Granted': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }

# this form is used to login


class CustomLoginForm(forms.Form):
    Username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}), label='שם משתמש')
    Password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}), label='סיסמא')

    error_messages = {
        'Username': {
            'required': "אנא הכנס שם משתמש",
            'max_length': "שם המשתמש חייב להיות פחות מ-50 תווים",
        },
        'Password': {
            'required': "אנא הכנס סיסמא",
            'max_length': "הסיסמא חייבת להיות פחות מ-50 תווים",
        },
    }

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('Username')
        password = cleaned_data.get('Password')
        if not User.objects.filter(Username=username).exists():
            self.add_error('Username', 'שם משתמש או סיסמא שגויים')
        else:
            user = User.objects.get(Username=username)
            if not user.Password == password:
                self.add_error('Password', 'שם משתמש או סיסמא שגויים')
        return cleaned_data

# form to update the user password that includes the old password and the new password and the new password confirmation


class UpdatePasswordForm(forms.Form):
    Old_Password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='סיסמא ישנה',
        error_messages={
            'required': "אנא הכנס סיסמא ישנה",
            'max_length': "הסיסמא חייבת להיות פחות מ-50 תווים",
        }
    )
    New_Password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='סיסמא חדשה',
        error_messages={
            'required': "אנא הכנס סיסמא חדשה",
            'max_length': "הסיסמא חייבת להיות פחות מ-50 תווים",
        }
    )
    Confirm_Password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='אמת סיסמא',
        error_messages={
            'required': "אנא אמת את הסיסמא",
            'max_length': "הסיסמא חייבת להיות פחות מ-50 תווים",
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('New_Password')
        confirm_password = cleaned_data.get('Confirm_Password')
        if not new_password == confirm_password:
            self.add_error('Confirm_Password', 'הסיסמאות אינן תואמות')
        return cleaned_data


class generate_sales_form(forms.Form):
    Start_Date = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date'}), label='תאריך התחלה')
    End_Date = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date'}), label='תאריך סיום')
    Report_Type = forms.ChoiceField(choices=[(
        '1', ' תצוגה מצומצמת '), ('2', '  תצוגה מפורטת   ')], label='בחר סוג דוח', )
    Order_Type = forms.ChoiceField(choices=[(
        '1', ' הכל '), ('2', '  אונליין '), ('3', '  דלפק ')], label='בחר סוג הזמנה', )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('Start_Date')
        end_date = cleaned_data.get('End_Date')
        if start_date > end_date:
            self.add_error(
                'End_Date', 'תאריך התחלה חייב להיות קטן מתאריך סיום')
        return cleaned_data


class generate_Products_In_OrderForm(forms.Form):
    Start_Date = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date'}), label='תאריך התחלה')
    End_Date = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date'}), label='תאריך סיום')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('Start_Date')
        end_date = cleaned_data.get('End_Date')
        if start_date > end_date:
            self.add_error(
                'End_Date', 'תאריך התחלה חייב להיות קטן מתאריך סיום')
        return cleaned_data


class generate_shifts_report_form(forms.Form):
    Start_Date = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date'}), label='תאריך התחלה')
    End_Date = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date'}), label='תאריך סיום')
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('Start_Date')
        end_date = cleaned_data.get('End_Date')
        if start_date > end_date:
            self.add_error(
                'End_Date', 'תאריך התחלה חייב להיות קטן מתאריך סיום')
        return cleaned_data




class ShiftPreferenceForm(forms.ModelForm):
    class Meta:
        model = Shift_Preferences
        fields = ['Is_Prefered']


class CashierEmployeeChoiceForm(forms.Form):
    cashiers = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.all(),
        required=False, 
        label="בחר עד שני עובדים"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    
    def clean_cashiers(self):
        data = self.cleaned_data.get('cashiers')
        if len(data) > 2:
            raise forms.ValidationError("You can select up to 2 employees only.")
        return data





class AddEmployeeToShiftForm(forms.ModelForm):
    class Meta:
        model = Users_in_Shifts
        fields = ['User']
        widgets = {
            'User': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'User': 'בחר עובד',
        }

    def __init__(self, *args, **kwargs):
        super(AddEmployeeToShiftForm, self).__init__(*args, **kwargs)
        self.fields['User'].queryset = User.objects.filter(Type='cs', Is_Active=True)


class ShiftSearchForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'type': 'date'}), label='תאריך התחלה')
    end_date = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'type': 'date'}), label='תאריך סיום')
    employee = forms.ChoiceField(required=False, 
        label='בחר עובד', widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(ShiftSearchForm, self).__init__(*args, **kwargs)
        cashiers = User.objects.filter(Type='cs')
        choices = [(user.id, f"{user.Employee.First_Name} {user.Employee.Last_Name}") for user in cashiers]
        self.fields['employee'].choices = [('', '--- בחר עובד מהרשימה ---')] + choices




