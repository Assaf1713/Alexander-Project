from django.urls import path

from mysite import settings
from django.conf.urls.static import static
from . import views
from .views import close_order

urlpatterns = [
    path("", views.login_view, name="log-in-page"),
    path('logout/', views.logout_view, name='logout'),
    path("main", views.mainpage, name="main-page"),




    # stock pages functions and views
    path("stock", views.stockView.as_view(), name="stock-page"),
    path("stock/item<int:id>", views.stock_item_View.as_view(), name="item-detail"),
    path('stock/update_quantity/<int:item_id>/',
         views.update_quantity, name='update_quantity'),

    # work-schedual pages functions and views
    path("workschedual", views.workschedual, name="schedual-page"),
    path("workschedual/reset-preferences",
         views.reset_preferences, name="reset-preferences"),
    path("workschedual/shift-builder-tool",
         views.shift_builder, name="shift-builder-tool-page"),
    path("workschedual/shift-builder-tool/remove<int:employee_id>/<int:shift_id>",
         views.remove_employee, name="remove-employee-from-temp-shift"),
    path("workschedual/shift-builder-tool/reset",
         views.reset_builder_table, name="reset-builder"),
    path("workschedual/shift-builder-tool/submit",
         views.submit_builder_table, name="submit-shifts"),
    # shift detail
    path("workschedual/shift<int:shift_id>",
         views.shift_detail, name="shift-detail"),
    # remove-employee-from-shift
    path("workschedual/shift<int:shift_id>/remove<int:user_id>",
         views.remove_employee_from_shift, name="remove-employee-from-shift"),
    path('shift/<int:shift_id>/add/', views.shift_detail,
         name='add-employee-to-shift'),
    # all shifts
    path("workschedual/All-Shifts", views.all_shifts, name="all-shifts-page"),
    # reset-all-shifts-page
    path("workschedual/reset-all-shifts",
         views.reset_all_shifts, name="reset-all-shifts"),



    # control page functions and views
    path("control", views.control, name="control-page"),
    path("control/Add-Supplier", views.Add_Supplier, name="Add-Supplier-Page"),
    path("control/Suppliers", views.Suppliers_Page, name="Suppliers-Page"),
    path("control/Suppliers/Supplier<int:id>",
         views.Update_Supplier, name="edit-supplier-page"),
    path("control/Add-Employee", views.Add_Employee, name="Add-Employee-Page"),
    path("control/Employees", views.Employees_Page, name="Employees-Page"),
    path("control/Employees/Employee<slug:employee_id>",
         views.Update_Employee, name="Update-Employee-Page"),
    path("control/Employees/Permissions<slug:employee_id>",
         views.Update_Employee_Permissions, name="Update-Employee-Permissions-Page"),
    path("control/Add-Raw-Material", views.Add_Raw_Material,
         name="Add-Raw-Material-Page"),
    path("control/Add-Highlight", views.Add_Highlight, name="add-highlight-page"),
    path("control/Highlights", views.Update_Highlight, name="highlights-page"),
    # remove-highlight
    path("control/Remove-Highlight<int:id>",
         views.Remove_Highlight, name="remove-highlight-page"),
    # disable user
    path("control/disableuser<int:employee_id>",
         views.disable_user, name="Disable-User"),

    # my user page functions and views
    path("myuser", views.myuser, name="my-user-page"),

    # reports page functions and views
    path("reports", views.reports, name="reports-page"),
    # sales-report
    path("reports/sales", views.sales_report, name="sales-report-page"),
    # stock-report
    path("reports/stock", views.stock_report, name="stock-report-page"),
    # product-in order
    path("reports/product-in-order", views.product_in_orders_report,
         name="product-report-page"),
    # shift-report
    path("reports/shift-report", views.shifts_report, name="shift-report-page"),


    # orders from suppliers functions and views
    path("makeorder", views.makeorderView.as_view(), name="make-order-page"),
    path('makeorder/submit', views.submit_order, name='submit-order'),
    path('makeorder/resetorder/', views.reset_order, name='reset-order'),
    path('makeorder/remove/<int:supplier_id>/<int:item_id>/',
         views.remove_item_view, name='remove-item'),
    path('makeorder/order<int:id>', views.Raw_Materials_Order_View,
         name='Raw-Materials-Order-Page'),




    # order page functions and views
    path("orders", views.orders, name="order-page"),
    path('orders/Create-New-Order', views.new_order_page,
         name='Create-Order-Page'),  # Create Order view
    # single order page functions and views
    path("orders/order<int:id>", views.order_detail, name="order-detail"),
    path('order/<int:order_id>/close/', views.close_order, name='close_order'),
    path("orders/All-Orders", views.allorders, name="all-orders-page"),
    path("orders/removeproduct/<int:order_id>/<int:product_id>/",
         views.remove_product_from_order, name="remove-product")
] 
