from django import template
from alexander.models import Suppliers



register = template.Library()

@register.filter
def get_supplier_name(suppliers, supplier_id):
    if supplier_id == 'None':
        return 'ספק לא מוגדר'
    supplier = suppliers.filter(id=supplier_id).first()
    return supplier.Name if supplier else 'Unknown'




@register.filter
def get_form_for_perm(permission_forms, perm):
    for permission, form in permission_forms:
        if permission == perm:
            return form.as_p()
    return ""


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, {})


@register.filter
def multiply(value, arg):
    return value * arg



@register.filter
def is_user_in_shift(employees, user):
    return any(employee.User == user for employee in employees)