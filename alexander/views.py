from datetime import datetime, timedelta
from email.utils import parsedate
import json
from django.contrib import messages
from django.forms import FloatField
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render
from django.urls import reverse
from .models import Admin_Highlights, Cashier_Orders, Employee, Orders_From_Suppliers, Permissions, Products_In_Order, Shift_Preferences, Shift_Types, Shifts, Suppliers, User, Products_In_Cashier_Orders, Raw_Materials, User_Permissions, UserLoginRecord, Users_in_Shifts
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AddEmployeeToShiftForm, AddHighlightForm, Cashier_Orders, AddProductToOrderForm, CashierEmployeeChoiceForm, CashierOrderForm, CreateRawMaterialsForm, CreateSuppliersForm, CustomLoginForm, EmployeeForm, OrderSearchForm, ShiftPreferenceForm, ShiftSearchForm, StockSearchForm, UpdateEmployeeForm, UpdatePasswordForm, UpdateQuantityForm, UpdateSupplierForm, UpdatePriceForm, AddRawMaterialForm, UpdateUserForm, UserForm, UserPermissionsForm, generate_Products_In_OrderForm, generate_sales_form, generate_shifts_report_form
from django.views import View
from django.views.generic import DetailView
from django.db.models import F, ExpressionWrapper, FloatField, Q
from django.db.models.functions import Round
from django.shortcuts import render, redirect
import logging
logging.basicConfig(level=logging.DEBUG)


def check_user_permissions(request, user, permission_lst):
    user_permissions = User_Permissions.objects.filter(User=user)
    for perm in permission_lst:
        # debug
        logging.debug(f'Checking if user has permission {perm}')
        # debug
        if not user_permissions.filter(Permission_Name__permission=perm, Is_Granted=True).exists():
            messages.error(
                request, 'הופנת בחזרה לדף הבית מאחר וחסרה לך הרשאה/ות מתאימה/ות')
            return redirect('main-page')
    return True


def check_if_user_is_logged_in(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            logged_in_user = get_object_or_404(User, id=user_id)
            return logged_in_user
        except User.DoesNotExist:
            return redirect('log-in-page')
    else:
        return redirect('log-in-page')


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('Username')
            password = form.cleaned_data.get('Password')
            try:
                user = User.objects.get(Username=username, Password=password)
                if user:
                    if user.Is_Active == False:
                        messages.error(request, 'המשתמש נחסם על ידי המנהל')
                        return redirect('log-in-page')
                    request.session['user_id'] = user.id
                    request.session['username'] = user.Username
                    UserLoginRecord.objects.create(user=user)
                    return redirect('main-page')
            except User.DoesNotExist:
                form.add_error(None, 'שם משתמש או סיסמה שגויים')
    else:
        form = CustomLoginForm()
    return render(request, 'alexander/index.html', {'form': form})


def logout_view(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            login_record = UserLoginRecord.objects.filter(
                user=user).latest('login_time')
            login_record.logout_time = timezone.now()
            login_record.session_duration = login_record.logout_time - login_record.login_time
            login_record.save()
        except (User.DoesNotExist, UserLoginRecord.DoesNotExist):
            pass
    request.session.flush()
    return redirect('log-in-page')


# orders views and functions


def close_order_after_3_days():
    today = timezone.now().date()
    orders = Cashier_Orders.objects.filter(Status='open')
    for order in orders:
        if order.PickUp_Date < today - timedelta(days=2):
            order.Status = 'close'
            order.save()


def orders(request):
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    permission_lst = [Permissions.VIEW_ORDERS]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    close_order_after_3_days()
    today = timezone.now().date()
    end_date = today + timedelta(days=3)
    orders = Cashier_Orders.objects.filter(
        Status='open', PickUp_Date__range=(today, end_date))
    for order in orders:
        print(order.PickUp_Date)
    All_Orders = Cashier_Orders.objects.all()
    return render(request, "alexander/orders.html", {
        "orders": orders,
        "All_Orders": All_Orders
    })


# all orders view

def allorders(request):
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    permission_lst = [Permissions.VIEW_ORDERS]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    close_order_after_3_days()
    form = OrderSearchForm(request.GET)
    orders = Cashier_Orders.objects.all()
    today = timezone.now().date()
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            orders = Cashier_Orders.objects.filter(
                Customer_Name__icontains=query)
        else:
            orders = Cashier_Orders.objects.all()

    return render(request, "alexander/allorders.html", {
        "orders": orders, 'form': form, 'today': today
    })


def new_order_page(request):
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    permission_lst = [Permissions.VIEW_ORDERS, Permissions.EDIT_ORDERS]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    if request.method == 'POST':
        form = CashierOrderForm(request.POST)
        if form.is_valid():
            pickupdate = form.cleaned_data.get('PickUp_Date')
            if pickupdate < timezone.now().date():
                messages.error(request, ' תאריך האיסוף חייב להיות תאריך עתידי')
            else:
                new_order = form.save(commit=False)
                request.user = User.objects.get(id=request.session.get('user_id'))
                new_order.Created_By = request.user
                new_order.Last_Modified_By = request.user
                new_order.Status = Cashier_Orders.OPEN
                # i want to make sure that online orders are always paid when first created
                if new_order.Order_Type == Cashier_Orders.ONLINE_ORDER:
                    new_order.IsPaid = True
                new_order.save()
                messages.success(request, 'ההזמנה נוצרה בהצלחה')
                return redirect('order-detail', id=new_order.id)
    else:
        form = CashierOrderForm()

    return render(request, 'alexander/Create_Order.html', {'form': form})


def order_detail(request, id):
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user

    order = get_object_or_404(Cashier_Orders, pk=id)
    products = Products_In_Cashier_Orders.objects.filter(order=order)
    order_total = 0
    if request.method == 'POST':
        permission_lst = [Permissions.VIEW_ORDERS, Permissions.EDIT_ORDERS]
        permission_check = check_user_permissions(
            request, logged_in_user, permission_lst)
        if isinstance(permission_check, HttpResponseRedirect):
            return permission_check
        # view logic
        form = AddProductToOrderForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            comments = form.cleaned_data.get('comments', '')
            existing_product_in_order = Products_In_Cashier_Orders.objects.filter(
                order=order, product=product).first()
            if existing_product_in_order:
                old_quantity = existing_product_in_order.quantity
                new_quantity = old_quantity + quantity
                existing_product_in_order.quantity = new_quantity
                order_total += product.Price * quantity
                existing_product_in_order.save()

            else:
                new_product_in_order = Products_In_Cashier_Orders(
                    order=order,
                    product=product,
                    quantity=quantity,
                    comments=comments
                )
                new_product_in_order.save()
                order_total += product.Price * quantity
            messages.success(request, 'המוצר התווסף להזמנה בהצלחה')
            return redirect('order-detail', id)
    else:
        order_total = sum(
            [product.product.Price * product.quantity for product in products])
        form = AddProductToOrderForm()

    context = {
        'order': order,
        'products': products,
        'form': form,
        'order_total': order_total
    }

    return render(request, 'alexander/order_detail.html', context)


def remove_product_from_order(request, order_id, product_id):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_ORDERS, Permissions.EDIT_ORDERS]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    if request.method == "POST":
        order= get_object_or_404(Cashier_Orders, id=order_id)
        if(order.Status == 'close'):
            messages.error(request, 'לא ניתן להסיר מוצר מהזמנה סגורה')
            return redirect('order-detail', id=order_id)
        product = get_object_or_404(
            Products_In_Cashier_Orders, order=order_id, product=product_id)
        product.delete()
        messages.success(request, 'המוצר הוסר מההזמנה בהצלחה')
        return redirect('order-detail', id=order_id)


def close_order(request, order_id):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_ORDERS, Permissions.EDIT_ORDERS]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    order = get_object_or_404(Cashier_Orders, id=order_id)
    if request.method == 'POST':
        order.Status = 'close'
        request.user = User.objects.get(id=request.session.get('user_id'))
        order.Last_Modified_By = request.user
        order.IsPaid = True
        order.save()
        return redirect('order-page')
    messages.success(request, 'ההזמנה נסגרה בהצלחה')
    return redirect('order-detail', id=order_id)

# main page view


def mainpage(request):
    try:
        user_id = request.session.get('user_id')
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('log-in-page')
    
    highlights = Admin_Highlights.objects.all()
    today = timezone.now().date()
    start_date = today - timedelta(days=2)
    end_date = today 
    if user.Type == User.ADMIN:
        highlights = Admin_Highlights.objects.all()
    elif user.Type == User.BAKER:
        highlights = Admin_Highlights.objects.filter(
            Q(Type='br') | Q(Type='al'),
            Due_Date__range=(start_date, end_date)
        )
    elif user.Type == User.CASHIER:
        highlights = Admin_Highlights.objects.filter(
            Q(Type='cs') | Q(Type='al'),
            Due_Date__range=(start_date, end_date)
        )
    CakesInOrder = Products_In_Cashier_Orders.objects.filter(
        product__Category='cake', order__Status='open', order__PickUp_Date__range=(today, today))
    CakesInOrderDict = {}
    for cake in CakesInOrder:
        if cake.product.Product_Name not in CakesInOrderDict:
            CakesInOrderDict[cake.product.Product_Name] = 0
        CakesInOrderDict[cake.product.Product_Name] += cake.quantity

    return render(request, 'alexander/main.html', {'highlights': highlights, 'CakesInOrderDict': CakesInOrderDict})


class stockView(View):
    def get(self, request):
        logged_in_user = check_if_user_is_logged_in(request)
        if isinstance(logged_in_user, HttpResponseRedirect):
            return logged_in_user
        # check if user has permissions
        permission_lst = [Permissions.VIEW_STOCK]
        permission_check = check_user_permissions(
            request, logged_in_user, permission_lst)
        if isinstance(permission_check, HttpResponseRedirect):
            return permission_check
        # view logic

        form = StockSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            if query:
                warehouse = Raw_Materials.objects.filter(
                    Material_Name__icontains=query)
            else:
                warehouse = Raw_Materials.objects.all().order_by('Material_Name')
        else:
            warehouse = Raw_Materials.objects.all().order_by('Material_Name')

        return render(request, 'alexander/stock.html', {'form': form, 'warehouse': warehouse})


class stock_item_View(View):
    def get(self, request, id):
        logged_in_user = check_if_user_is_logged_in(request)
        if isinstance(logged_in_user, HttpResponseRedirect):
            return logged_in_user
        # check if user has permissions
        permission_lst = [Permissions.VIEW_STOCK]
        permission_check = check_user_permissions(
            request, logged_in_user, permission_lst)
        if isinstance(permission_check, HttpResponseRedirect):
            return permission_check
        # view logic
        flag = False
        if User_Permissions.objects.filter(User=logged_in_user, Permission_Name__permission=Permissions.EDIT_STOCK, Is_Granted=True).exists():
            flag = True
        item = get_object_or_404(Raw_Materials, pk=id)
        form = UpdateSupplierForm(instance=item)
        form2 = UpdatePriceForm(instance=item)
        return render(request, 'alexander/stock_item.html', {'item': item, 'form': form, 'form2': form2, 'flag': flag})

    def post(self, request, id):
        logged_in_user = check_if_user_is_logged_in(request)
        if isinstance(logged_in_user, HttpResponseRedirect):
            return logged_in_user
        # check if user has permissions
        permission_lst = [Permissions.VIEW_STOCK, Permissions.EDIT_STOCK]
        permission_check = check_user_permissions(
            request, logged_in_user, permission_lst)
        if isinstance(permission_check, HttpResponseRedirect):
            return permission_check
        # view logic
        item = get_object_or_404(Raw_Materials, pk=id)
        form = UpdateSupplierForm(request.POST, instance=item)
        form2 = UpdatePriceForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'הפריט עודכן בהצלחה')
            return redirect(reverse('item-detail', args=[id]))
        if form2.is_valid():
            form2.save()
            messages.success(request, 'המחיר עודכן בהצלחה')
            return redirect(reverse('item-detail', args=[id]))
        return render(request, 'alexander/stock_item.html', {'item': item, 'form': form, 'form2': form2})


def update_quantity(request, item_id):
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    item = get_object_or_404(Raw_Materials, id=item_id)
    if request.method == 'POST':
        # check if user has permissions
        permission_lst = [Permissions.VIEW_STOCK, Permissions.EDIT_STOCK]
        permission_check = check_user_permissions(
            request, logged_in_user, permission_lst)
        if isinstance(permission_check, HttpResponseRedirect):
            return permission_check
        # view logic
        form = UpdateQuantityForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'הכמות עודכנה בהצלחה')
            return redirect('stock-page')
    else:
        form = UpdateQuantityForm(instance=item)
    return render(request, 'alexander/stock.html', {'form': form, 'item': item})


def control(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    return render(request, "alexander/control.html")

# my user page view


def myuser(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # view logic
    last_log_in = UserLoginRecord.objects.filter(
        user=logged_in_user).latest('login_time')
    Last_Log_in_Date_Format = last_log_in.formatted_login_time()
    user_permissions = User_Permissions.objects.filter(
        User=logged_in_user, Is_Granted=True)
    permissions_by_category = {
        'הזמנות': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_ORDERS, Permissions.EDIT_ORDERS]),
        'מלאי': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_STOCK, Permissions.EDIT_STOCK]),
        'הזמנות מספקים': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_SUPPLIER_ORDERS, Permissions.EDIT_SUPPLIER_ORDERS]),
        'סידור משמרות': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_SCHEDULE, Permissions.EDIT_SCHEDULE]),
        'דוחות': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_REPORTS, Permissions.EDIT_REPORTS]),
        'בקרה': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]),
    }
    if request.method == 'POST':
        form = UpdatePasswordForm(request.POST)
        if form.is_valid():
            if logged_in_user.Password != form.cleaned_data.get('Old_Password'):
                form.add_error(None, 'סיסמה ישנה שגויה')
            else:
                new_password = form.cleaned_data.get('New_Password')
                logged_in_user.Password = new_password
                logged_in_user.save()
                messages.success(request, 'הסיסמה עודכנה בהצלחה')
                return redirect('my-user-page')
    else:
        form = UpdatePasswordForm()
    return render(request, "alexander/myuser.html", {'user': logged_in_user, 'permissions_by_category': permissions_by_category, 'Last_Log_in_Date_Format': Last_Log_in_Date_Format, 'form': form})


def UpdateMyPassword(request):
    # check if user is logged in
    user = check_if_user_is_logged_in(request)
    if isinstance(user, HttpResponseRedirect):
        return user
    # view logic
    if request.method == 'POST':
        form = UpdatePasswordForm(request.POST)
        if form.is_valid():
            if user.Password != form.cleaned_data.get('Old_Password'):
                form.add_error(None, 'סיסמה ישנה שגויה')
            else:
                new_password = form.cleaned_data.get('New_Password')
                user.Password = new_password
                user.save()
                messages.success(request, 'הסיסמה עודכנה בהצלחה')
                return redirect('my-user-page')
    else:
        form = UpdatePasswordForm()
    return render(request, 'alexander/myuser.html', {'form': form})


# orders from suppliers views
# This view is used to make an order from suppliers

class makeorderView(View):
    def get(self, request):
        # check if user is logged in
        logged_in_user = check_if_user_is_logged_in(request)
        if isinstance(logged_in_user, HttpResponseRedirect):
            return logged_in_user
        # check if user has permissions
        permission_lst = [Permissions.VIEW_SUPPLIER_ORDERS]
        permission_check = check_user_permissions(
            request, logged_in_user, permission_lst)
        if isinstance(permission_check, HttpResponseRedirect):
            return permission_check
        # view logic
        orders = Orders_From_Suppliers.objects.all()
        temp_order = request.session.get('temp_order', {})
        form2 = AddRawMaterialForm()
        form = StockSearchForm(request.GET)
        total_order_price = 0
        if form.is_valid():
            query = form.cleaned_data.get('query')
            if query:
                raw_materials = Raw_Materials.objects.filter(
                    Material_Name__icontains=query).annotate(percentage_diff=Round(ExpressionWrapper((F('Quantity') - F('Lower_Barrier')) * 100.0 / F('Lower_Barrier'),output_field=FloatField()),1))
            else:
                raw_materials = Raw_Materials.objects.filter(Quantity__lte=F('Lower_Barrier')).annotate(percentage_diff=Round(ExpressionWrapper((F('Quantity') - F('Lower_Barrier')) * 100.0 / F('Lower_Barrier'),output_field=FloatField()),1))
        else:
            # raw_materials = Raw_Materials.objects.filter(
            #     Quantity__lte=F('Lower_Barrier'))
            raw_materials = Raw_Materials.objects.filter(Quantity__lte=F('Lower_Barrier')).annotate(percentage_diff=Round(ExpressionWrapper((F('Quantity') - F('Lower_Barrier')) * 100.0 / F('Lower_Barrier'),output_field=FloatField()),1))
        suppliers = Suppliers.objects.all()

        for supplier_id, items in temp_order.items():
            for item in items:
                total_order_price += item['total']
        context = {
            'orders': orders,
            'form2': form2,
            'form': form,
            'raw_materials': raw_materials,
            'temp_order': temp_order,
            'suppliers': suppliers,
            'total_order_price': total_order_price,
        }
        return render(request, 'alexander/makeorder.html', context)

    def post(self, request):
        # check if user is logged in
        logged_in_user = check_if_user_is_logged_in(request)
        if isinstance(logged_in_user, HttpResponseRedirect):
            return logged_in_user
        # check if user has permissions
        permission_lst = [Permissions.VIEW_SUPPLIER_ORDERS,
                          Permissions.EDIT_SUPPLIER_ORDERS]
        permission_check = check_user_permissions(
            request, logged_in_user, permission_lst)
        if isinstance(permission_check, HttpResponseRedirect):
            return permission_check
        # view logic
        flag = True
        orders = Orders_From_Suppliers.objects.all()
        temp_order = request.session.get('temp_order', {})
        form2 = AddRawMaterialForm(request.POST)
        total_order_price = 0
        if form2.is_valid():
            item = form2.cleaned_data['Item']
            quantity = form2.cleaned_data['Quantity']
            supplier_id = str(item.Supplier.id)

            if supplier_id not in temp_order.keys():
                temp_order[supplier_id] = []

            for existing_item in temp_order[supplier_id]:
                if existing_item['item_id'] == item.id:
                    existing_item['quantity'] += quantity
                    flag = False
                    break
            total = item.Price * quantity
            if flag:
                temp_order[supplier_id].append({
                    'item_id': item.id,
                    'item_name': item.Material_Name,
                    'quantity': quantity,
                    'unit': item.Unit,
                    'price': item.Price,
                    'total': total
                })
            for supplier_id, items in temp_order.items():
                for item in items:
                    total_order_price += item['total']

            request.session['temp_order'] = temp_order
            return redirect('make-order-page')

        # In case form is not valid, redisplay the form with errors
        form = StockSearchForm(request.GET)

        if form.is_valid():
            query = form.cleaned_data.get('query')
            if query:
                raw_materials = Raw_Materials.objects.filter(
                    Material_Name__icontains=query)
            else:
                raw_materials = Raw_Materials.objects.filter(
                    Quantity__lte=F('Lower_Barrier'))
        else:
            raw_materials = Raw_Materials.objects.filter(
                Quantity__lte=F('Lower_Barrier'))
        suppliers = Suppliers.objects.all()
        context = {
            'orders': orders,
            'form2': form2,
            'form': form,
            'raw_materials': raw_materials,
            'temp_order': temp_order,
            'suppliers': suppliers,
            'total_order_price': total_order_price,
        }
        return render(request, 'alexander/makeorder.html', context)


# this view is used to reset the temorary order

def reset_order(request):
    if 'temp_order' in request.session:
        del request.session['temp_order']
    messages.success(request, 'הטיוטה נמחקה בהצלחה')
    return redirect('make-order-page')

# this view is used to remove an item from the temporary order


def remove_item_view(request, supplier_id, item_id):
    temp_order = request.session.get('temp_order', {})
    supplier_id_str = str(supplier_id)
    if supplier_id_str in temp_order:
        new_items = []
        for item in temp_order[supplier_id_str]:
            if item['item_id'] != item_id:
                new_items.append(item)
        temp_order[supplier_id_str] = new_items

        if not temp_order[supplier_id_str]:
            del temp_order[supplier_id_str]
    request.session['temp_order'] = temp_order
    return redirect('make-order-page')


def submit_order(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_SUPPLIER_ORDERS,
                      Permissions.EDIT_SUPPLIER_ORDERS]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    temp_order = request.session.get('temp_order', {})
    if not temp_order:
        return redirect('make-order-page')

    new_order = Orders_From_Suppliers.objects.create()
    try:
        new_order.Created_By = logged_in_user
    except User.DoesNotExist:
        pass
    for supplier_id, items in temp_order.items():
        supplier = get_object_or_404(Suppliers, id=supplier_id)
        new_order.supplier_List.add(supplier)
        for item_data in items:
            item = get_object_or_404(Raw_Materials, id=item_data['item_id'])
            Products_In_Order.objects.create(
                OrderNum=new_order,
                Item=item,
                Quantity=item_data['quantity']
            )

    new_order.save()
    del request.session['temp_order']
    messages.success(request, 'הזמנה חדשה נוצרה')
    return redirect('Raw-Materials-Order-Page', new_order.id)


def Raw_Materials_Order_View(request, id):
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_SUPPLIER_ORDERS]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    order = get_object_or_404(Orders_From_Suppliers, pk=id)
    products = Products_In_Order.objects.filter(OrderNum=order).select_related(
        'Item', 'Item__Supplier').order_by('Item__Supplier__Name')

    supplier_products = {}
    total_sum = 0

    for product in products:
        supplier = product.Item.Supplier
        if supplier not in supplier_products:
            supplier_products[supplier] = []
        supplier_products[supplier].append(product)
        total_sum += product.Quantity * product.Item.Price

    context = {
        'order': order,
        'supplier_products': supplier_products,
        'total_sum': total_sum
    }

    return render(request, 'alexander/Raw_Materials_Order.html', context)


def AddProductToQuery(request, item_id):
    item = get_object_or_404(Raw_Materials, id=item_id)
    if request.method == 'POST':
        form = UpdateQuantityForm(request.POST, instance=item)
        Amount = form.cleaned_data['Quantity']
        if form.is_valid():

            return redirect('stock-page')
    else:
        form = UpdateQuantityForm(instance=item)
    return render(request, 'alexander/stock.html', {'form': form, 'item': item})


# views for control page]


# Add Supplier View
def Add_Supplier(request):
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    if request.method == "POST":
        form = CreateSuppliersForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'הספק נוסף בהצלחה')
            return redirect('control-page')
    else:
        form = CreateSuppliersForm()
    return render(request, 'alexander/add_supplier.html', {'form': form})


# Supplierד View
def Suppliers_Page(request):
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    suppliers = Suppliers.objects.all()
    return render(request, 'alexander/Suppliers_Page.html', {'suppliers': suppliers})

# Update Supplier View


def Update_Supplier(request, id):
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    supplier = get_object_or_404(Suppliers, id=id)
    last_order = supplier.Supplier_Orders.last()
    if request.method == "POST":
        form = CreateSuppliersForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'הספק עודכן בהצלחה')
            return redirect('edit-supplier-page', id=id)
    form = CreateSuppliersForm(instance=supplier)
    return render(request, 'alexander/update_supplier.html', {'supplier': supplier, 'form': form, 'last_order': last_order})

# Add Employee View


def Add_Employee(request):
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    if request.method == 'POST':
        employee_form = EmployeeForm(request.POST)
        user_form = UserForm(request.POST)

        if employee_form.is_valid() and user_form.is_valid():
            employee = employee_form.save()
            user = user_form.save(commit=False)
            user.Employee = employee
            user.save()
            assign_permissions(user)
            if user.Type == User.CASHIER:
                assign_preferences(user)
            messages.success(request, 'עובד נוסף בהצלחה והרשאות ניתנו')
            return redirect('Employees-Page')
    else:
        employee_form = EmployeeForm()
        user_form = UserForm()

    context = {
        'employee_form': employee_form,
        'user_form': user_form,
    }
    return render(request, 'alexander/add_employee.html', context)


def assign_preferences(user):
    shift_types = Shift_Types.objects.all()
    for shift_type in shift_types:
        preference = Shift_Preferences.objects.create(
            User=user,
            Shift_Type=shift_type,
            Is_Prefered=True
        )


def assign_permissions(user):
    permissions = {}

    if user.Type == User.ADMIN:
        permissions = {
            Permissions.VIEW_ORDERS: True,
            Permissions.EDIT_ORDERS: True,
            Permissions.VIEW_STOCK: True,
            Permissions.EDIT_STOCK: True,
            Permissions.VIEW_SUPPLIER_ORDERS: True,
            Permissions.EDIT_SUPPLIER_ORDERS: True,
            Permissions.VIEW_SCHEDULE: True,
            Permissions.EDIT_SCHEDULE: True,
            Permissions.VIEW_REPORTS: True,
            Permissions.EDIT_REPORTS: True,
            Permissions.VIEW_CONTROL: True,
            Permissions.EDIT_CONTROL: True,
        }
    elif user.Type == User.BAKER:
        permissions = {
            Permissions.VIEW_ORDERS: True,
            Permissions.EDIT_ORDERS: False,
            Permissions.VIEW_STOCK: True,
            Permissions.EDIT_STOCK: True,
            Permissions.VIEW_SUPPLIER_ORDERS: True,
            Permissions.EDIT_SUPPLIER_ORDERS: False,
            Permissions.VIEW_SCHEDULE: True,
            Permissions.EDIT_SCHEDULE: False,
            Permissions.VIEW_REPORTS: True,
            Permissions.EDIT_REPORTS: False,
            Permissions.VIEW_CONTROL: False,
            Permissions.EDIT_CONTROL: False,
        }
    elif user.Type == User.CASHIER:
        permissions = {
            Permissions.VIEW_ORDERS: True,
            Permissions.EDIT_ORDERS: True,
            Permissions.VIEW_STOCK: True,
            Permissions.EDIT_STOCK: False,
            Permissions.VIEW_SUPPLIER_ORDERS: False,
            Permissions.EDIT_SUPPLIER_ORDERS: False,
            Permissions.VIEW_SCHEDULE: True,
            Permissions.EDIT_SCHEDULE: True,
            Permissions.VIEW_REPORTS: True,
            Permissions.EDIT_REPORTS: False,
            Permissions.VIEW_CONTROL: False,
            Permissions.EDIT_CONTROL: False,
        }

    for perm, granted in permissions.items():
        permission_obj = Permissions.objects.get(permission=perm)
        User_Permissions.objects.create(
            User=user, Permission_Name=permission_obj, Is_Granted=granted)

# Employee View


def Employees_Page(request):
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic

    employees = Employee.objects.all()
    return render(request, 'alexander/employees.html', {'employees': employees})


# Update Employee View

def Update_Employee(request, employee_id):
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    employee = get_object_or_404(Employee, Employee_ID=employee_id)
    user = get_object_or_404(User, Employee=employee)
    is_active = user.Is_Active
    user_permissions = User_Permissions.objects.filter(User=user)
    try:
        user_last_log_in = UserLoginRecord.objects.filter(
            user=user).latest('login_time')
    except UserLoginRecord.DoesNotExist:
        user_last_log_in = None

    if request.method == "POST":
        employee_form = UpdateEmployeeForm(request.POST, instance=employee)
        user_form = UpdateUserForm(request.POST, instance=user)

        if employee_form.is_valid():
            employee_form.save()
            messages.success(request, 'העובד עודכן בהצלחה')
            return redirect('Update-Employee-Page', employee_id=employee_id)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'המשתמש עודכן בהצלחה')
            return redirect('Update-Employee-Page', employee_id=employee_id)

    else:
        employee_form = UpdateEmployeeForm(instance=employee)
        user_form = UpdateUserForm(instance=user)
    permission_forms = [(perm, UserPermissionsForm(
        instance=perm, prefix=f'perm_{perm.id}')) for perm in user_permissions]
    permissions_by_category = {
        'הזמנות': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_ORDERS, Permissions.EDIT_ORDERS]),
        'מלאי': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_STOCK, Permissions.EDIT_STOCK]),
        'הזמנות מספקים': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_SUPPLIER_ORDERS, Permissions.EDIT_SUPPLIER_ORDERS]),
        'סידור משמרות': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_SCHEDULE, Permissions.EDIT_SCHEDULE]),
        'דוחות': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_REPORTS, Permissions.EDIT_REPORTS]),
        'בקרה': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]),
    }
    context = {
        'employee': employee,
        'employee_form': employee_form,
        'user_form': user_form,
        'permission_forms': permission_forms,
        'permissions_by_category': permissions_by_category,
        'user_last_log_in': user_last_log_in,
        'is_active': is_active
    }
    return render(request, 'alexander/update_employee.html', context)


def Update_Employee_Permissions(request, employee_id):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    employee = get_object_or_404(Employee, Employee_ID=employee_id)
    user = get_object_or_404(User, Employee=employee)
    user_permissions = User_Permissions.objects.filter(User=user)
    employee_form = UpdateEmployeeForm(instance=employee)
    user_form = UpdateUserForm(instance=user)
    if request.method == "POST":
        for perm in user_permissions:
            perm_form = UserPermissionsForm(
                request.POST, instance=perm, prefix=f'perm_{perm.id}')
            if perm_form.is_valid():
                perm_form.save()
        messages.success(request, 'ההרשאות עודכנו בהצלחה')
        return redirect('Update-Employee-Page', employee_id=employee_id)
    permission_forms = [(perm, UserPermissionsForm(
        instance=perm, prefix=f'perm_{perm.id}')) for perm in user_permissions]
    permissions_by_category = {
        'הזמנות': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_ORDERS, Permissions.EDIT_ORDERS]),
        'מלאי': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_STOCK, Permissions.EDIT_STOCK]),
        'הזמנות מספקים': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_SUPPLIER_ORDERS, Permissions.EDIT_SUPPLIER_ORDERS]),
        'סידור משמרות': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_SCHEDULE, Permissions.EDIT_SCHEDULE]),
        'דוחות': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_REPORTS, Permissions.EDIT_REPORTS]),
        'בקרה': user_permissions.filter(Permission_Name__permission__in=[Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]),
    }
    context = {
        'employee': employee,
        'permission_forms': permission_forms,
        'permissions_by_category': permissions_by_category,
        'employee_form': employee_form,
        'user_form': user_form,


    }
    return render(request, 'alexander/update_employee.html', context)


def disable_user(request, employee_id):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    employee = get_object_or_404(Employee, Employee_ID=employee_id)
    user = get_object_or_404(User, Employee=employee)
    if user.Is_Active:
        user.Is_Active = False
        user.save()
    else:
        user.Is_Active = True
        user.save()
    messages.success(request, 'המשתמש עודכן בהצלחה')
    return redirect('Employees-Page')


# Add Raw Material View


def Add_Raw_Material(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic

    if request.method == "POST":
        form = CreateRawMaterialsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'חומר גלם נוסף בהצלחה')
            return redirect('control-page')
    else:
        form = CreateRawMaterialsForm()
    return render(request, 'alexander/add_raw_material.html', {'form': form})

# Add Highlight View


def Add_Highlight(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    form = AddHighlightForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            New_Highlight = form.save(commit=False)
            due_date = form.cleaned_data.get('Due_Date')
            today = timezone.now().date()
            if (due_date < today):
                messages.error(request, 'תאריך תפוגה  לא יכול להיות תאריך שחלף')
                return redirect('add-highlight-page')
            request.user = User.objects.get(id=request.session.get('user_id'))
            New_Highlight.Submitted_By = request.user
            New_Highlight.save()
        messages.success(request, 'הודעת מנהל נוספה בהצלחה')
        return redirect('highlights-page')
    return render(request, 'alexander/add_highlight.html', {'form': form})

# Update Highlight View


def Update_Highlight(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    highlights = Admin_Highlights.objects.all()
    return render(request, 'alexander/highlights.html', {'highlights': highlights})

# Remove Highlight View


def Remove_Highlight(request, id):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_CONTROL, Permissions.EDIT_CONTROL]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    if request.method == "POST":
        highlight = get_object_or_404(Admin_Highlights, id=id)
        highlight.delete()
        messages.success(request, 'הודעת מנהל נמחקה בהצלחה')
        return redirect('highlights-page')
    return render(request, 'alexander/highlights.html')


# reports

def reports(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_REPORTS, Permissions.EDIT_REPORTS]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    form2 = generate_sales_form()
    form3 = generate_Products_In_OrderForm()
    form4 = generate_shifts_report_form()
    return render(request, 'alexander/reports.html', {'form2': form2, 'form3': form3, 'form4': form4})


def sales_report(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_REPORTS, Permissions.EDIT_REPORTS]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    if request.method == 'POST':
        form2 = generate_sales_form(request.POST)
        total_desk_orders_sum = 0
        total_online_orders_sum = 0
        distinct_orders_count = 0
        if form2.is_valid():
            start_date = form2.cleaned_data.get('Start_Date')
            end_date = form2.cleaned_data.get('End_Date')
            Order_Type = form2.cleaned_data.get('Order_Type')
            Order_Dict = Generate_Order_Dictionarty(
                start_date, end_date, Order_Type)
            Report_Type = form2.cleaned_data.get('Report_Type')
            products = Products_In_Cashier_Orders.objects.all()
            products = products.filter(
                order__Order_Date__range=(start_date, end_date))
            desk_products = products.filter(
                order__Order_Type=Cashier_Orders.DESK_ORDER)
            online_products = products.filter(
                order__Order_Type=Cashier_Orders.ONLINE_ORDER)
            distinct_online_orders_count = online_products.values(
                'order').distinct().count()
            distinct_desk_orders_count = desk_products.values(
                'order').distinct().count()
            distinct_orders_count = distinct_online_orders_count + distinct_desk_orders_count
            total_desk_orders_sum = sum(
                [product.product.Price * product.quantity for product in desk_products])
            total_online_orders_sum = sum(
                [product.product.Price * product.quantity for product in online_products])
            products_quantity_dict = {}
            desk_products_quantity_dict = {}
            online_products_quantity_dict = {}
            for product in products:
                if product.product.Product_Name not in products_quantity_dict:
                    products_quantity_dict[product.product.Product_Name] = 0
                products_quantity_dict[product.product.Product_Name] += product.quantity
            for product in desk_products:
                if product.product.Product_Name not in desk_products_quantity_dict:
                    desk_products_quantity_dict[product.product.Product_Name] = 0
                desk_products_quantity_dict[product.product.Product_Name] += product.quantity
            for product in online_products:
                if product.product.Product_Name not in online_products_quantity_dict:
                    online_products_quantity_dict[product.product.Product_Name] = 0
                online_products_quantity_dict[product.product.Product_Name] += product.quantity
            

            return render(request, 'alexander/sales_report.html', {
                'products': products,
                'desk_products': desk_products,
                'online_products': online_products,
                'Report_Type': Report_Type,
                'start_date': start_date,
                'end_date': end_date,
                'Order_Type': Order_Type,
                'total_desk_orders_sum': total_desk_orders_sum,
                'total_online_orders_sum': total_online_orders_sum,
                'distinct_orders_count': distinct_orders_count,
                'distinct_desk_orders_count': distinct_desk_orders_count,
                'distinct_online_orders_count': distinct_online_orders_count,
                'products_quantity_dict': products_quantity_dict,
                'desk_products_quantity_dict': desk_products_quantity_dict,
                'online_products_quantity_dict': online_products_quantity_dict,
                'Order_Dict': Order_Dict


            })
        else:
            return redirect('reports-page')
    else:
        return redirect('reports-page')


def stock_report(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_REPORTS, Permissions.EDIT_REPORTS]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    stock = Raw_Materials.objects.all()
    current_date = timezone.now().date()
    Total_Stock_Value = 0
    for item in stock:
        Total_Stock_Value += item.Price * item.Quantity
    return render(request, 'alexander/stock_report.html', {'stock': stock, 'current_date': current_date, 'Total_Stock_Value': Total_Stock_Value})


def product_in_orders_report(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_REPORTS, Permissions.EDIT_REPORTS]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    if request.method == 'POST':
        form3 = generate_Products_In_OrderForm(request.POST)
        if form3.is_valid():
            start_date = form3.cleaned_data.get('Start_Date')
            end_date = form3.cleaned_data.get('End_Date')
            products = Products_In_Cashier_Orders.objects.filter(
                order__Order_Date__range=(start_date, end_date))
            products_quantity_dict = {}
            for product in products:
                if product.product.Product_Name not in products_quantity_dict:
                    products_quantity_dict[product.product.Product_Name] = 0
                products_quantity_dict[product.product.Product_Name] += product.quantity
            product_category_dict = {}
            for product in products:
                if product.product.Category not in product_category_dict:
                    product_category_dict[product.product.Category] = 0
                product_category_dict[product.product.Category] += product.quantity
            return render(request, 'alexander/product_in_orders_report.html', {
                'products': products,
                'products_quantity_dict': products_quantity_dict,
                'product_category_dict': product_category_dict,
                'start_date': start_date,
                'end_date': end_date
            })
        else:
            return redirect('reports-page')
    else:
        form3 = generate_Products_In_OrderForm()
        return render(request, 'alexander/reports.html', {'form3': form3})


def shifts_report(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_REPORTS, Permissions.EDIT_REPORTS]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    if request.method == 'POST':
        form4 = generate_shifts_report_form(request.POST)
        if form4.is_valid():
            start_date = form4.cleaned_data.get('Start_Date')
            end_date = form4.cleaned_data.get('End_Date')
            user_in_shifts_dict = build_user_in_shifts_dict(
                start_date, end_date)
            all_friday_shifts_count = Shifts.objects.filter(Date__range=(
                start_date, end_date), Shift_Type__Shift_Name='fm').count()
            total_shifts_count = Shifts.objects.filter(
                Date__range=(start_date, end_date)).count()
            current_date = timezone.now().date()

            labels = [f"{user.Employee.First_Name}{user.Employee.Last_Name}" for user, _, _, _, _ in user_in_shifts_dict]
            shift_counts = [shifts_count for _,
                            shifts_count, _, _, _ in user_in_shifts_dict]

            return render(request, 'alexander/shifts_report.html', {
                'user_in_shifts_dict': user_in_shifts_dict,
                'start_date': start_date,
                'end_date': end_date,
                'all_friday_shifts_count': all_friday_shifts_count,
                'total_shifts_count': total_shifts_count,
                'current_date': current_date,
                'chart_labels': json.dumps(labels),
                'chart_data': json.dumps(shift_counts)
            })
        else:
            return redirect('reports-page')
    else:
        form4 = generate_shifts_report_form()
        return render(request, 'alexander/reports.html', {'form4': form4})

# help functions for reports


def Generate_Order_Dictionarty(start_date, end_date, Order_Type):
    Order_Dict = {}
    if Order_Type == '1':
        orders = Cashier_Orders.objects.filter(
            Order_Date__range=(start_date, end_date))
        total_sum = 0
        for order in orders:
            products = Products_In_Cashier_Orders.objects.filter(order=order)
            total_sum = sum(
                [product.product.Price * product.quantity for product in products])
            Order_Dict[order] = total_sum
    elif Order_Type == '2':
        orders = Cashier_Orders.objects.filter(Order_Date__range=(
            start_date, end_date), Order_Type=Cashier_Orders.ONLINE_ORDER)
        total_sum = 0
        for order in orders:
            products = Products_In_Cashier_Orders.objects.filter(order=order)
            total_sum = sum(
                [product.product.Price * product.quantity for product in products])
            Order_Dict[order] = total_sum

    else:
        orders = Cashier_Orders.objects.filter(Order_Date__range=(
            start_date, end_date), Order_Type=Cashier_Orders.DESK_ORDER)
        total_sum = 0
        for order in orders:
            products = Products_In_Cashier_Orders.objects.filter(order=order)
            total_sum = sum(
                [product.product.Price * product.quantity for product in products])
            Order_Dict[order] = total_sum

    return Order_Dict


def build_user_in_shifts_dict(start_date, end_date):
    user_in_shifts_list = []
    total_shifts_count = Shifts.objects.filter(
        Date__range=(start_date, end_date)).count()
    all_friday_shifts_count = Shifts.objects.filter(Date__range=(
        start_date, end_date), Shift_Type__Shift_Name='fm').count()
    if total_shifts_count == 0:
        return []
    for user in User.objects.filter(Type=User.CASHIER):
        shifts = Users_in_Shifts.objects.filter(
            User=user, Shift__Date__range=(start_date, end_date))
        shifts_count = shifts.count()
        my_friday_shifts_count = shifts.filter(
            Shift__Shift_Type__Shift_Name='fm').count()
        shift_percentage = (shifts_count / total_shifts_count) * \
            100 if total_shifts_count > 0 else 0
        friday_percentage = (my_friday_shifts_count / all_friday_shifts_count) * \
            100 if all_friday_shifts_count > 0 else 0
        user_in_shifts_list.append(
            (user, shifts_count, my_friday_shifts_count, shift_percentage, friday_percentage))
    user_in_shifts_list.sort(key=lambda x: x[3], reverse=True)
    return user_in_shifts_list

# work schedual and shifts views and functions


def workschedual(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_SCHEDULE]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    next_week_shifts = get_next_week_shifts_table()
    this_week_shifts = get_this_week_shifts_table()
    next_week_dates = get_next_week_dates()
    this_week_dates = get_this_week_dates()
    if logged_in_user.Type == User.CASHIER:
        preferences_table = get_preferences_table(logged_in_user)
        forms_by_preference = {}
        for time_of_day, days in preferences_table.items():
            for day, preferences in days.items():
                forms_by_preference[(time_of_day, day)] = [
                    (preference, ShiftPreferenceForm(
                        instance=preference, prefix=f'preference_{preference.id}'))
                    for preference in preferences
                ]
        if request.method == 'POST':
            # check if user has permissions
            permission_lst = [Permissions.EDIT_SCHEDULE]
            permission_check = check_user_permissions(
                request, logged_in_user, permission_lst)
            if isinstance(permission_check, HttpResponseRedirect):
                return permission_check
            # view logic
            for time_of_day, days in forms_by_preference.items():
                for preference, form in days:
                    form = ShiftPreferenceForm(
                        request.POST, instance=preference, prefix=f'preference_{preference.id}')
                    if form.is_valid():
                        form.save()
            messages.success(request, 'העדפות נשמרו בהצלחה')
            return redirect('schedual-page')

        context = {
            'logged_in_user': logged_in_user,
            'preferences_table': preferences_table,
            'forms_by_preference': forms_by_preference,
            'next_week_dates': next_week_dates,
            'next_week_shifts': next_week_shifts,
            'this_week_dates': this_week_dates,
            'this_week_shifts': this_week_shifts,

        }

        return render(request, "alexander/workschedual.html", context)

    elif logged_in_user.Type == User.ADMIN:
        cashier_users = User.objects.filter(Type=User.CASHIER, Is_Active=True)
        Preferences_by_time_and_users = build_preferences_by_time_and_user(
            cashier_users)
        days = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי']
        next_sunday = get_next_sunday()
        context = {
            'logged_in_user': logged_in_user,
            'cashier_users': cashier_users,
            'preferences_by_time_and_user': Preferences_by_time_and_users,
            'day_lst': days,
            'next_sunday': next_sunday,
            'next_week_dates': next_week_dates,
            'next_week_shifts': next_week_shifts,
            'this_week_dates': this_week_dates,
            'this_week_shifts': this_week_shifts,

        }

        return render(request, "alexander/workschedual.html", context)


# prefernces views and functions

def get_preferences_table(user):
    shift_preferences = user.my_preferences.all()
    preferences_by_time = {
        'בוקר': {
            'ראשון': shift_preferences.filter(Shift_Type__Shift_Name='sm'),
            'שני': shift_preferences.filter(Shift_Type__Shift_Name='mm'),
            'שלישי': shift_preferences.filter(Shift_Type__Shift_Name='tm'),
            'רביעי': shift_preferences.filter(Shift_Type__Shift_Name='wm'),
            'חמישי': shift_preferences.filter(Shift_Type__Shift_Name='thm'),
            'שישי': shift_preferences.filter(Shift_Type__Shift_Name='fm'),
        },
        'ערב': {
            'ראשון': shift_preferences.filter(Shift_Type__Shift_Name='se'),
            'שני': shift_preferences.filter(Shift_Type__Shift_Name='me'),
            'שלישי': shift_preferences.filter(Shift_Type__Shift_Name='te'),
            'רביעי': shift_preferences.filter(Shift_Type__Shift_Name='we'),
            'חמישי': shift_preferences.filter(Shift_Type__Shift_Name='the'),
        }
    }
    return preferences_by_time


def get_Prefered_preferences_table(user):
    shift_preferences = user.my_preferences.filter(Is_Prefered=True)
    preferences_by_time = {
        'בוקר': {
            'ראשון': shift_preferences.filter(Shift_Type__Shift_Name='sm'),
            'שני': shift_preferences.filter(Shift_Type__Shift_Name='mm'),
            'שלישי': shift_preferences.filter(Shift_Type__Shift_Name='tm'),
            'רביעי': shift_preferences.filter(Shift_Type__Shift_Name='wm'),
            'חמישי': shift_preferences.filter(Shift_Type__Shift_Name='thm'),
            'שישי': shift_preferences.filter(Shift_Type__Shift_Name='fm'),
        },
        'ערב': {
            'ראשון': shift_preferences.filter(Shift_Type__Shift_Name='se'),
            'שני': shift_preferences.filter(Shift_Type__Shift_Name='me'),
            'שלישי': shift_preferences.filter(Shift_Type__Shift_Name='te'),
            'רביעי': shift_preferences.filter(Shift_Type__Shift_Name='we'),
            'חמישי': shift_preferences.filter(Shift_Type__Shift_Name='the'),
        }
    }
    return preferences_by_time


def build_preferences_by_time_and_user(users):
    preferences_by_time_and_user = {
        'בוקר': {
            'ראשון': [],
            'שני': [],
            'שלישי': [],
            'רביעי': [],
            'חמישי': [],
            'שישי': [],
        },
        'ערב': {
            'ראשון': [],
            'שני': [],
            'שלישי': [],
            'רביעי': [],
            'חמישי': [],
        }
    }

    for user in users:
        preferences_table = get_Prefered_preferences_table(user)
        for time_of_day, days in preferences_table.items():
            for day, preferences in days.items():
                if preferences.exists():
                    preferences_by_time_and_user[time_of_day][day].append(
                        user.Employee.First_Name + ' ' + user.Employee.Last_Name)

    return preferences_by_time_and_user


def reset_preferences(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.EDIT_SCHEDULE]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    preferences = Shift_Preferences.objects.all()
    for preference in preferences:
        preference.Is_Prefered = True
        preference.save()
    messages.success(request, 'ההעדפות נמחקו בהצלחה', 'success')
    return redirect('schedual-page')


# shift builder views and functions

def shift_builder(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.EDIT_SCHEDULE, Permissions.VIEW_SCHEDULE]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    # del request.session['shifts_dict']
    if 'shifts_dict' not in request.session:
        request.session['shifts_dict'] = initialize_shifts_dict()
    shifts_dict = request.session['shifts_dict']
    days_lst = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי']
    next_sunday = get_next_sunday()
    next_week_dates = {
        'ראשון': (next_sunday),
        'שני': (next_sunday + timezone.timedelta(days=1)),
        'שלישי': (next_sunday + timezone.timedelta(days=2)),
        'רביעי': (next_sunday + timezone.timedelta(days=3)),
        'חמישי': (next_sunday + timezone.timedelta(days=4)),
        'שישי': (next_sunday + timezone.timedelta(days=5)),
    }
    if request.method == 'POST':
        print(request.POST)
        for time_of_day, shifts in shifts_dict.items():
            for day, shift_data in shifts.items():
                form = CashierEmployeeChoiceForm(
                    request.POST, prefix=shift_data["form_prefix"])
                if form.is_valid():
                    selected_employees = form.cleaned_data['cashiers']
                    print(selected_employees)
                    for selected_employee in selected_employees:
                        if shift_data['shift_id'] != Shift_Types.objects.get(Shift_Name='fm').id:
                            if selected_employee.id not in shift_data['employees'] and len(shift_data['employees']) <= 1:
                                shift_data['employees'].append(
                                    selected_employee.id)
                        else:
                            if selected_employee.id not in shift_data['employees'] and len(shift_data['employees']) <= 2:
                                shift_data['employees'].append(
                                    selected_employee.id)
                else:
                    print("Form Errors:", form.errors)
                    print("Submitted Data:", request.POST)
                    print("Available IDs in Queryset:", [
                          e.id for e in form.fields['cashiers'].queryset])

        request.session['shifts_dict'] = shifts_dict
        return redirect('shift-builder-tool-page')

    context_shifts_dict = {}
    for time_of_day, shifts in shifts_dict.items():
        context_shifts_dict[time_of_day] = {}
        for day, shift_data in shifts.items():
            form_prefix = shift_data['form_prefix']
            queryset = Employee.objects.filter(
                Q(user__Type=User.CASHIER) &
                Q(user__Is_Active=True) &
                Q(user__my_preferences__Is_Prefered=True) &
                Q(user__my_preferences__Shift_Type__Shift_Name=form_prefix)
            )
            form = CashierEmployeeChoiceForm(prefix=form_prefix)
            form.fields['cashiers'].queryset = queryset
            shift = Shift_Types.objects.get(id=shift_data['shift_id'])
            employees = [Employee.objects.get(
                id=emp_id) for emp_id in shift_data['employees']]
            context_shifts_dict[time_of_day][day] = {
                'date': next_week_dates[day],
                'shift': shift,
                'form': form,
                'employees': employees,
                'form_prefix': form_prefix,
            }
    return render(request, 'alexander/shift_builder.html', {'shifts_dict': context_shifts_dict, 'days_lst': days_lst,
                                                            'next_week_dates': next_week_dates, })


def remove_employee(request, employee_id, shift_id):
    shifts_dict = request.session['shifts_dict']
    for time_of_day, shifts in shifts_dict.items():
        for day, shift_data in shifts.items():
            if shift_data['shift_id'] == shift_id and employee_id in shift_data['employees']:
                shift_data['employees'].remove(employee_id)
    request.session['shifts_dict'] = shifts_dict
    return redirect('shift-builder-tool-page')


def reset_builder_table(request):
    if 'shifts_dict' in request.session:
        del request.session['shifts_dict']
    return redirect('shift-builder-tool-page')


def submit_builder_table(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.EDIT_SCHEDULE, Permissions.VIEW_SCHEDULE]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    shifts_dict = request.session['shifts_dict']
    for time_of_day, shifts in shifts_dict.items():
        for day, shift_data in shifts.items():
            shift = Shift_Types.objects.get(id=shift_data['shift_id'])
            date = get_shift_date(day)
            # check if shift already exists
            if Shifts.objects.filter(Shift_Type=shift, Date=date).exists():
                existing_shift = Shifts.objects.get(
                    Shift_Type=shift, Date=date)
                existing_users = Users_in_Shifts.objects.filter(
                    Shift=existing_shift)
                for user in existing_users:
                    user.delete()
                existing_shift.delete()
            new_shift = Shifts.objects.create(
                Shift_Type=shift,
                Date=date
            )
            new_shift.save()
            if shift_data['employees']:
                for emp_id in shift_data['employees']:
                    employee = Employee.objects.get(id=emp_id)
                    user = User.objects.get(Employee=employee)
                    Users_in_Shifts.objects.create(
                        Shift=new_shift,
                        User=user
                    )
    del request.session['shifts_dict']
    messages.success(request, 'המשמרות נוצרו בהצלחה')
    return redirect('schedual-page')

# all shifts views and functions


def all_shifts(request):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_SCHEDULE]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    shifts = Shifts.objects.order_by('Date').all()
    form = ShiftSearchForm()
    if request.method == 'POST':
        form = ShiftSearchForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            user_id = form.cleaned_data.get('employee')
            try:
                user = User.objects.get(id=user_id)
            except ValueError:
                user = None
            if start_date and end_date and start_date < end_date and not user:
                shifts = shifts.filter(Date__range=(start_date, end_date))
            elif start_date and end_date and start_date < end_date and user:
                shifts = shifts.filter(Date__range=(
                    start_date, end_date), users_in_shifts__User=user)
            elif user:
                shifts = shifts.filter(users_in_shifts__User=user)

    return render(request, 'alexander/all_shifts.html', {'shifts': shifts, 'form': form})


def reset_all_shifts(request):
    form = ShiftSearchForm()
    shifts = Shifts.objects.order_by('Date').all()
    return render(request, 'alexander/all_shifts.html', {'shifts': shifts, 'form': form})
# specific shift details view and functions


def shift_detail(request, shift_id):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_SCHEDULE]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    shift = get_object_or_404(Shifts, id=shift_id)
    users_in_shift = Users_in_Shifts.objects.filter(Shift=shift)
    form = AddEmployeeToShiftForm()
    today = timezone.now().date()
    Is_Not_Passed_Yet = shift.Date > today

    if request.method == 'POST':
        # check if user has permissions
        permission_lst = [Permissions.EDIT_SCHEDULE]
        permission_check = check_user_permissions(
            request, logged_in_user, permission_lst)
        if isinstance(permission_check, HttpResponseRedirect):
            return permission_check
        # view logic
        form = AddEmployeeToShiftForm(request.POST)
        if form.is_valid() and Is_Not_Passed_Yet:
            user = form.cleaned_data['User']
            if Users_in_Shifts.objects.filter(Shift=shift, User=user).exists():
                messages.error(request, 'העובד כבר קיים במשמרת')
                return redirect('shift-detail', shift_id=shift.id)
            # check if it's a friday morning shift
            if shift.Shift_Type.Shift_Name == 'fm':
                if Users_in_Shifts.objects.filter(Shift=shift).count() >= 3:
                    messages.error(request, 'המשמרת מלאה')
                    return redirect('shift-detail', shift_id=shift.id)
            else:
                if Users_in_Shifts.objects.filter(Shift=shift).count() >= 2:
                    messages.error(request, 'המשמרת מלאה')
                    return redirect('shift-detail', shift_id=shift.id)
            user_in_shift = form.save(commit=False)
            user_in_shift.Shift = shift
            user_in_shift.save()
            messages.success(request, 'עובד נוסף למשמרת בהצלחה')
            return redirect('shift-detail', shift_id=shift.id)

    context = {
        'shift': shift,
        'users_in_shift': users_in_shift,
        'form': form,
        'Is_Not_Passed_Yet': Is_Not_Passed_Yet

    }
    return render(request, 'alexander/shift_detail.html', context)


def remove_employee_from_shift(request, shift_id, user_id):
    # check if user is logged in
    logged_in_user = check_if_user_is_logged_in(request)
    if isinstance(logged_in_user, HttpResponseRedirect):
        return logged_in_user
    # check if user has permissions
    permission_lst = [Permissions.VIEW_SCHEDULE, Permissions.EDIT_SCHEDULE]
    permission_check = check_user_permissions(
        request, logged_in_user, permission_lst)
    if isinstance(permission_check, HttpResponseRedirect):
        return permission_check
    # view logic
    shift = get_object_or_404(Shifts, id=shift_id)
    user = get_object_or_404(User, id=user_id)
    user_in_shift = Users_in_Shifts.objects.get(Shift=shift, User=user)
    user_in_shift.delete()
    messages.success(request, 'עובד הוסר מהמשמרת בהצלחה')
    return redirect('shift-detail', shift_id=shift_id)

# helper functions for the shift tables in the main work schedual page


def get_next_week_shifts_table():
    next_week_dates = get_next_week_dates()
    next_week_shifts = Shifts.objects.filter(Date__in=next_week_dates.values())
    # check the length of the queryset
    if next_week_shifts.count() != 11:
        return None
    next_week_shifts_table = {
        'בוקר': {
            'ראשון': {'shift': next_week_shifts.get(Shift_Type__Shift_Name='sm'), 'employees': list(Users_in_Shifts.objects.filter(Shift=next_week_shifts.get(Shift_Type__Shift_Name='sm')))},
            'שני': {'shift': next_week_shifts.get(Shift_Type__Shift_Name='mm'), 'employees': list(Users_in_Shifts.objects.filter(Shift=next_week_shifts.get(Shift_Type__Shift_Name='mm')))},
            'שלישי': {'shift': next_week_shifts.get(Shift_Type__Shift_Name='tm'), 'employees': list(Users_in_Shifts.objects.filter(Shift=next_week_shifts.get(Shift_Type__Shift_Name='tm')))},
            'רביעי': {'shift': next_week_shifts.get(Shift_Type__Shift_Name='wm'), 'employees': list(Users_in_Shifts.objects.filter(Shift=next_week_shifts.get(Shift_Type__Shift_Name='wm')))},
            'חמישי': {'shift': next_week_shifts.get(Shift_Type__Shift_Name='thm'), 'employees': list(Users_in_Shifts.objects.filter(Shift=next_week_shifts.get(Shift_Type__Shift_Name='thm')))},
            'שישי': {'shift': next_week_shifts.get(Shift_Type__Shift_Name='fm'), 'employees': list(Users_in_Shifts.objects.filter(Shift=next_week_shifts.get(Shift_Type__Shift_Name='fm')))},
        },
        'ערב': {
            'ראשון': {'shift': next_week_shifts.get(Shift_Type__Shift_Name='se'), 'employees': list(Users_in_Shifts.objects.filter(Shift=next_week_shifts.get(Shift_Type__Shift_Name='se')))},
            'שני': {'shift': next_week_shifts.get(Shift_Type__Shift_Name='me'), 'employees': list(Users_in_Shifts.objects.filter(Shift=next_week_shifts.get(Shift_Type__Shift_Name='me')))},
            'שלישי': {'shift': next_week_shifts.get(Shift_Type__Shift_Name='te'), 'employees': list(Users_in_Shifts.objects.filter(Shift=next_week_shifts.get(Shift_Type__Shift_Name='te')))},
            'רביעי': {'shift': next_week_shifts.get(Shift_Type__Shift_Name='we'), 'employees': list(Users_in_Shifts.objects.filter(Shift=next_week_shifts.get(Shift_Type__Shift_Name='we')))},
            'חמישי': {'shift': next_week_shifts.get(Shift_Type__Shift_Name='the'), 'employees': list(Users_in_Shifts.objects.filter(Shift=next_week_shifts.get(Shift_Type__Shift_Name='the')))},
        }
    }
    return next_week_shifts_table


def get_this_week_shifts_table():
    this_week_dates = get_this_week_dates()
    this_week_shifts = Shifts.objects.filter(Date__in=this_week_dates.values())
    if this_week_shifts.count() != 11:
        return None

    this_week_shifts_table = {
        'בוקר': {
            'ראשון': {'shift': this_week_shifts.get(Shift_Type__Shift_Name='sm'), 'employees': list(Users_in_Shifts.objects.filter(Shift=this_week_shifts.get(Shift_Type__Shift_Name='sm')))},
            'שני': {'shift': this_week_shifts.get(Shift_Type__Shift_Name='mm'), 'employees': list(Users_in_Shifts.objects.filter(Shift=this_week_shifts.get(Shift_Type__Shift_Name='mm')))},
            'שלישי': {'shift': this_week_shifts.get(Shift_Type__Shift_Name='tm'), 'employees': list(Users_in_Shifts.objects.filter(Shift=this_week_shifts.get(Shift_Type__Shift_Name='tm')))},
            'רביעי': {'shift': this_week_shifts.get(Shift_Type__Shift_Name='wm'), 'employees': list(Users_in_Shifts.objects.filter(Shift=this_week_shifts.get(Shift_Type__Shift_Name='wm')))},
            'חמישי': {'shift': this_week_shifts.get(Shift_Type__Shift_Name='thm'), 'employees': list(Users_in_Shifts.objects.filter(Shift=this_week_shifts.get(Shift_Type__Shift_Name='thm')))},
            'שישי': {'shift': this_week_shifts.get(Shift_Type__Shift_Name='fm'), 'employees': list(Users_in_Shifts.objects.filter(Shift=this_week_shifts.get(Shift_Type__Shift_Name='fm')))},
        },
        'ערב': {
            'ראשון': {'shift': this_week_shifts.get(Shift_Type__Shift_Name='se'), 'employees': list(Users_in_Shifts.objects.filter(Shift=this_week_shifts.get(Shift_Type__Shift_Name='se')))},
            'שני': {'shift': this_week_shifts.get(Shift_Type__Shift_Name='me'), 'employees': list(Users_in_Shifts.objects.filter(Shift=this_week_shifts.get(Shift_Type__Shift_Name='me')))},
            'שלישי': {'shift': this_week_shifts.get(Shift_Type__Shift_Name='te'), 'employees': list(Users_in_Shifts.objects.filter(Shift=this_week_shifts.get(Shift_Type__Shift_Name='te')))},
            'רביעי': {'shift': this_week_shifts.get(Shift_Type__Shift_Name='we'), 'employees': list(Users_in_Shifts.objects.filter(Shift=this_week_shifts.get(Shift_Type__Shift_Name='we')))},
            'חמישי': {'shift': this_week_shifts.get(Shift_Type__Shift_Name='the'), 'employees': list(Users_in_Shifts.objects.filter(Shift=this_week_shifts.get(Shift_Type__Shift_Name='the')))},
        }
    }
    return this_week_shifts_table


# helper functions for the shift builder tool

def initialize_shifts_dict():
    return {
        'בוקר': {
            'ראשון': {'shift_id': Shift_Types.objects.get(Shift_Name='sm').id, 'form_prefix': 'sm', 'employees': []},
            'שני': {'shift_id': Shift_Types.objects.get(Shift_Name='mm').id, 'form_prefix': 'mm', 'employees': []},
            'שלישי': {'shift_id': Shift_Types.objects.get(Shift_Name='tm').id, 'form_prefix': 'tm', 'employees': []},
            'רביעי': {'shift_id': Shift_Types.objects.get(Shift_Name='wm').id, 'form_prefix': 'wm', 'employees': []},
            'חמישי': {'shift_id': Shift_Types.objects.get(Shift_Name='thm').id, 'form_prefix': 'thm', 'employees': []},
            'שישי': {'shift_id': Shift_Types.objects.get(Shift_Name='fm').id, 'form_prefix': 'fm', 'employees': []},
        },
        'ערב': {
            'ראשון': {'shift_id': Shift_Types.objects.get(Shift_Name='se').id, 'form_prefix': 'se', 'employees': []},
            'שני': {'shift_id': Shift_Types.objects.get(Shift_Name='me').id, 'form_prefix': 'me', 'employees': []},
            'שלישי': {'shift_id': Shift_Types.objects.get(Shift_Name='te').id, 'form_prefix': 'te', 'employees': []},
            'רביעי': {'shift_id': Shift_Types.objects.get(Shift_Name='we').id, 'form_prefix': 'we', 'employees': []},
            'חמישי': {'shift_id': Shift_Types.objects.get(Shift_Name='the').id, 'form_prefix': 'the', 'employees': []},
        }
    }


def get_next_sunday():
    today = timezone.now().date()
    days_ahead = 6 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_sunday = today + timezone.timedelta(days=days_ahead)
    return next_sunday


def get_next_week_dates():
    next_sunday = get_next_sunday()
    next_week_dates = {
        'ראשון': (next_sunday),
        'שני': (next_sunday + timezone.timedelta(days=1)),
        'שלישי': (next_sunday + timezone.timedelta(days=2)),
        'רביעי': (next_sunday + timezone.timedelta(days=3)),
        'חמישי': (next_sunday + timezone.timedelta(days=4)),
        'שישי': (next_sunday + timezone.timedelta(days=5)),
    }
    return next_week_dates


def get_this_week_dates():
    next_sunday = get_next_sunday()
    this_week_dates = {
        'ראשון': (next_sunday - timezone.timedelta(days=7)),
        'שני': (next_sunday - timezone.timedelta(days=6)),
        'שלישי': (next_sunday - timezone.timedelta(days=5)),
        'רביעי': (next_sunday - timezone.timedelta(days=4)),
        'חמישי': (next_sunday - timezone.timedelta(days=3)),
        'שישי': (next_sunday - timezone.timedelta(days=2)),
    }
    return this_week_dates


def get_shift_date(day):
    next_week_dates = get_next_week_dates()
    return next_week_dates[day]


# end of shift builder tool functions
