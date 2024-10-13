from django.db import models
from django.core.validators import RegexValidator
from django.urls import reverse







class Employee(models.Model):
    nine_digits_validator = RegexValidator(
        regex=r'^\d{9}$', message='ID must be exactly 9 digits.')
    phone_regex = RegexValidator(
        regex=r'^\d{9,15}$', message="Phone number must be between 9 and 15 digits.")
    Employee_ID = models.CharField(max_length=9,
                                   validators=[nine_digits_validator],
                                   unique=True,
                                   help_text="Enter a 9-digit employee ID.")
    First_Name = models.CharField(max_length=10, default="")
    Last_Name = models.CharField(max_length=10, default="")
    Birthday = models.DateField()
    Email = models.EmailField((""), max_length=254)
    phone_number = models.CharField(
        validators=[phone_regex], max_length=15, blank=True)
    Join_Date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.First_Name + " " + self.Last_Name
    
    def get_absolute_url(self):
        return reverse("Update-Employee-Page", args=[self.Employee_ID])


class User(models.Model):
    ADMIN = 'ad'
    BAKER = 'br'
    CASHIER = 'cs'
    CATEGORY_CHOICES = [
        (ADMIN, 'מנהל מערכת'),
        (BAKER, 'קונדיטור'),
        (CASHIER, 'עובד דלפק'),]
    password_regex = RegexValidator(
       regex = r'^[a-zA-Z\d]{8,}$',
       message="Password must be at least 8 characters long and include at least one digit."
    )
    Username = models.CharField(max_length=15, unique=True)
    Type = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=CASHIER)
    Employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    Password = models.CharField(max_length=15, validators=[password_regex])
    Is_Active = models.BooleanField(default=True)

    def __str__(self):
        return self.Username + "(" + self.Type.__str__() + "), " + self.Employee.First_Name
    



class UserLoginRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    session_duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.Username} : {self.login_time} to {self.logout_time}'

    def formatted_login_time(self):
         return self.login_time.strftime('%d/%m/%Y | %H:%M:%S')


class Admin_Highlights(models.Model):
    #choices cashier/baker/admin/all
    CASHIER='cs'
    BAKER='br'
    ADMIN='ad'
    ALL='al'
    CATEGORY_CHOICES = [
        (CASHIER, 'עובד דלפק'),
        (BAKER, 'קונדיטור'),
        (ADMIN, 'מנהל'),
        (ALL, 'כולם'),
    ]
    Submitted_By = models.ForeignKey(User, on_delete=models.CASCADE)
    Due_Date = models.DateField()
    Type = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default=ALL)
    Text = models.TextField(max_length=1000)

    def __str__(self):
        return  "Highlight number: " + str(self.id) + " | By:" + self.Submitted_By.Employee.First_Name 


class Shift_Types(models.Model):
    SUNDAY_MORNING = 'sm'
    SUNDAY_EVENING = 'se'
    MONDAY_MORNING = 'mm'
    MONDAY_EVENING = 'me'
    TUESDAY_MORNING = 'tm'
    TUESDAY_EVENING = 'te'
    WEDNESDAY_MORNING = 'wm'
    WEDNESDAY_EVENING = 'we'
    THURSDAY_MORNING = 'thm'
    THURSDAY_EVENING = 'the'
    FRIDAY_MORNING = 'fm'
    CATEGORY_CHOICES = [
        (SUNDAY_MORNING, 'ראשון-בוקר'),
        (SUNDAY_EVENING, 'ראשון-ערב'),
        (MONDAY_MORNING, 'שני-בוקר'),
        (MONDAY_EVENING, 'שני-ערב'),
        (TUESDAY_MORNING, 'שלישי-בוקר'),
        (TUESDAY_EVENING, 'שלישי-ערב'),
        (WEDNESDAY_MORNING, 'רביעי-בוקר'),
        (WEDNESDAY_EVENING, 'רביעי-ערב'),
        (THURSDAY_MORNING, 'חמישי-בוקר'),
        (THURSDAY_EVENING, 'חמישי-ערב'),
        (FRIDAY_MORNING, 'שישי-בוקר'),
    ]
    Shift_Name = models.CharField(
        max_length=4, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.Shift_Name


class Shifts(models.Model):
    Date = models.DateField()
    Shift_Type = models.ForeignKey(Shift_Types, on_delete=models.CASCADE)

    def __str__(self):
        return "shift number:" + str(self.id) + ", Date:" + str(self.Date)

    def get_absolute_url(self):
        return reverse("shift-detail", args=[self.id])

class Users_in_Shifts(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Shift = models.ForeignKey(Shifts, on_delete=models.CASCADE)

    def __str__(self):
        return self.User.Employee.First_Name + " " + self.User.Employee.Last_Name 

class Shift_Preferences(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_preferences", null=True, blank=True)
    Shift_Type = models.ForeignKey(Shift_Types, on_delete=models.CASCADE)
    Is_Prefered = models.BooleanField(default=True)

    def __str__(self):
        return self.User.Employee.First_Name + " " + self.User.Employee.Last_Name 
        


class Permissions(models.Model):

    VIEW_ORDERS = 'view_orders'
    EDIT_ORDERS = 'edit_orders'
    VIEW_STOCK = 'view_stock'
    EDIT_STOCK = 'edit_stock'
    VIEW_SUPPLIER_ORDERS = 'view_supplier_orders'
    EDIT_SUPPLIER_ORDERS = 'edit_supplier_orders'
    VIEW_SCHEDULE = 'view_schedule'
    EDIT_SCHEDULE = 'edit_schedule'
    VIEW_REPORTS = 'view_reports'
    EDIT_REPORTS = 'edit_reports'
    VIEW_CONTROL = 'view_control'
    EDIT_CONTROL = 'edit_control'

    PERMISSION_CHOICES = [
        (VIEW_ORDERS, 'הזמנות-צפייה'),
        (EDIT_ORDERS, ' הזמנות-עריכה'),
        (VIEW_STOCK, 'מלאי-צפייה'),
        (EDIT_STOCK, 'מלאי-עריכה'),
        (VIEW_SUPPLIER_ORDERS, 'הזמנות מספקים-צפייה'),
        (EDIT_SUPPLIER_ORDERS, 'הזמנות מספקים-עריכה'),
        (VIEW_SCHEDULE, 'משמרות-צפייה'),
        (EDIT_SCHEDULE, 'משמרות-עריכה'),
        (VIEW_REPORTS, 'דוחות-צפייה'),
        (EDIT_REPORTS, 'דוחות-עריכה'),
        (VIEW_CONTROL, 'בקרה-צפייה'),
        (EDIT_CONTROL, 'בקרה-עריכה'),
    ]
    permission = models.CharField(
        max_length=20,
        choices=PERMISSION_CHOICES
    )

    def __str__(self):
        return self.permission


class User_Permissions(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_permissions", null=True)
    Permission_Name = models.ForeignKey(Permissions, on_delete=models.CASCADE)
    Is_Granted = models.BooleanField(default=True)

    def __str__(self):
        return "" + str(self.Permission_Name) +  " | " + str(self.Is_Granted)


class Products(models.Model):
    CAKE = 'cake'
    BREAD = 'bread' 
    COOCKIES = 'coockies'
    OTHER = 'other'

    CATEGORY_CHOICES = [
        (CAKE, 'עוגה'),
        (BREAD, 'לחם'),
        (OTHER, 'אחר'),
        (COOCKIES, 'עוגיות'),
    ]
    Product_Name = models.CharField(max_length=50)
    Price = models.PositiveIntegerField()
    Category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default=OTHER, verbose_name="קטגוריה",null=True)
    def __str__(self):
        return self.Product_Name


# class Order_Type(models.Model):
#     ONLINE_ORDER = 'online_order'
#     DESK_ORDER = 'desk_order'

#     PERMISSION_CHOICES = [
#         (ONLINE_ORDER, 'הזמנה אונליין'),
#         (DESK_ORDER, 'הזמנה בדלפק'),
#     ]
#     Type = models.CharField(max_length=50, choices=PERMISSION_CHOICES)

#     def __str__(self):
#         return self.Type


class Cashier_Orders(models.Model):
    OPEN = 'open'
    CLOSE = 'close'

    ORDER_CHOICES = [
        (OPEN, 'open'),
        (CLOSE, 'close'),
    ]

    ONLINE_ORDER = 'online_order'
    DESK_ORDER = 'desk_order'

    PERMISSION_CHOICES = [
        (ONLINE_ORDER, 'הזמנה אונליין'),
        (DESK_ORDER, 'הזמנה בדלפק'),]
    Created_By = models.ForeignKey(User, verbose_name=(
        "Order submitted by"), null=True, related_name="Orders_Submitted", on_delete=models.SET_NULL)
    Order_Date = models.DateField(verbose_name=(
        "Created At"), auto_now=False, auto_now_add=True)
    Order_Type = models.CharField(("סוג הזמנה"), max_length=50, choices=PERMISSION_CHOICES, default=DESK_ORDER)
    Customer_Name = models.CharField(max_length=50)
    Customer_Last_Name = models.CharField(max_length=50)
    PickUp_Date = models.DateField(auto_now=False, auto_now_add=False)
    Status = models.CharField(
        max_length=5, choices=ORDER_CHOICES, default="open")
    IsPaid = models.BooleanField(default=False)
    Comments = models.CharField(max_length=200, blank=True)
    Last_Modified = models.DateField(
        auto_now=True, auto_now_add=False, editable=False)
    Last_Modified_By = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL)
    # slug = models.SlugField(default="", blank=True, db_index=True)

    def get_absolute_url(self):
        return reverse("order-detail", args=[self.id])

    def __str__(self):
        return "Order Number: " + str(self.id) + "| Customer Name: " + self.Customer_Name + " " + self.Customer_Last_Name + "| Pick Up Date: " + str(self.PickUp_Date)


class Products_In_Cashier_Orders(models.Model):
    order = models.ForeignKey(
        Cashier_Orders, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    comments = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return "Order Number: " + str(self.order.id) + "| Product: " + self.product.__str__() + "| Qty: " + str(self.quantity)


class Suppliers(models.Model):
    Name = models.CharField(max_length=50, verbose_name="Supplier Name")
    phone_regex = RegexValidator(
        regex=r'^\d{9,15}$', message="Phone number must be between 9 and 15 digits.")
    Email = models.EmailField((""), max_length=254, blank=True)
    phone = models.CharField(
        validators=[phone_regex], max_length=15, blank=True, verbose_name="Contact Phone")

    def __str__(self):
        return self.Name


class Raw_Materials(models.Model):
    Material_Name = models.CharField(max_length=100)
    Lower_Barrier = models.PositiveIntegerField()
    Unit = models.CharField(max_length=20)
    Price = models.PositiveIntegerField()
    Supplier = models.ForeignKey(Suppliers, related_name="raw_materials", on_delete=models.SET_NULL, null=True)
    Quantity= models.PositiveIntegerField(default=0)

    def get_absolute_url(self):
        return reverse("item-detail", args=[self.id])

    def __str__(self):
        return self.Material_Name


# class Warehouse(models.Model):
#     Stock_Item = models.ForeignKey(
#         Raw_Materials, verbose_name=("Item"), on_delete=models.CASCADE)
#     Quantity = models.PositiveIntegerField()

#     def __str__(self):
#         return self.Stock_Item + "| Qty: " + str(self.Quantity)


class Orders_From_Suppliers(models.Model):
    Created_By = models.ForeignKey(User, verbose_name=(
        "Order submitted by"), null=True, related_name="Raw_Materials_Orders", on_delete=models.SET_NULL)
    Date = models.DateField(
        auto_now=False, auto_now_add=True, verbose_name="Order Date")
    supplier_List = models.ManyToManyField(Suppliers, related_name="Supplier_Orders")

    def __str__(self):
        return "Order Number: " + str(self.id) + "| Order Placed On: " + str(self.Date) 
    
    def get_absolute_url(self):
        return reverse("Raw-Materials-Order-Page", args=[self.id])

class Products_In_Order(models.Model):
    OrderNum = models.ForeignKey(
        Orders_From_Suppliers, verbose_name=("Order"), on_delete=models.CASCADE)
    Item = models.ForeignKey(Raw_Materials, verbose_name=(
        "Product"), on_delete=models.CASCADE)
    Quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.Item.__str__() + "| Qty: " + str(self.Quantity)


