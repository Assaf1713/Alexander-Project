from django.contrib import admin

from django.contrib import admin
from alexander.models import (
    Employee,
    User,
    Admin_Highlights,
    Shift_Types,
    Shifts,
    Shift_Preferences,
    Permissions,
    User_Permissions,
    Products,
    Cashier_Orders,
    Products_In_Cashier_Orders,
    Suppliers,
    Raw_Materials,
    Orders_From_Suppliers,
    Products_In_Order,
    UserLoginRecord,
    Users_in_Shifts
)


class cashier_orders_Admin(admin.ModelAdmin):
    list_display = ('id', 'Customer_Name',
                    'Customer_Last_Name', 'Order_Date')


class raw_materials_Admin(admin.ModelAdmin):
    list_display = ('id', 'Material_Name', 'Supplier', 'Quantity')

class Suppliers_Admin(admin.ModelAdmin):
    list_display = ('id', 'Name')

class Employee_Admin(admin.ModelAdmin):
    list_display = ('id', 'First_Name', 'Last_Name')

class User_Admin(admin.ModelAdmin):
    list_display = ('id', 'Username')    

class UserLoginRecord_Admin(admin.ModelAdmin):
    list_display = ('id', 'user', 'login_time', 'logout_time', 'session_duration')

class Shifts_Preferences_Admin(admin.ModelAdmin):
    list_display = ('id', 'User', 'Shift_Type')


class Users_in_Shifts_Admin(admin.ModelAdmin):
    list_display = ('id', 'User', 'Shift')

class shift_types_Admin(admin.ModelAdmin):
    list_display = ('id', 'Shift_Name')

admin.site.register(Employee, Employee_Admin)
admin.site.register(User, User_Admin)
admin.site.register(Admin_Highlights)
admin.site.register(Shift_Types, shift_types_Admin)
admin.site.register(Shifts)
admin.site.register(Shift_Preferences, Shifts_Preferences_Admin)
admin.site.register(Permissions)
admin.site.register(User_Permissions)
admin.site.register(Products)
admin.site.register(Cashier_Orders, cashier_orders_Admin)
admin.site.register(Products_In_Cashier_Orders)
admin.site.register(Suppliers, Suppliers_Admin)
admin.site.register(Raw_Materials, raw_materials_Admin)
admin.site.register(Orders_From_Suppliers)
admin.site.register(Products_In_Order)
admin.site.register(UserLoginRecord, UserLoginRecord_Admin)
admin.site.register(Users_in_Shifts, Users_in_Shifts_Admin)
