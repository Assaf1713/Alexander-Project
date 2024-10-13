# your_django_app/populate_products.py

from .models import Products

def populate_products():
    products_data = [
        {'Product_Name': 'עוגת גבינה באסקית', 'Price': 205},
        {'Product_Name': 'עוגת גזר', 'Price': 160},
        {'Product_Name': 'עוגת שוקולד באסקית', 'Price': 205},
        {'Product_Name': 'בגט', 'Price': 24},
        {'Product_Name': 'לחם שישה דגנים', 'Price': 22},
        {'Product_Name': 'לחם כפרי טבעי', 'Price': 24},
        {'Product_Name': 'לחם כפרי שיבול שועל', 'Price': 24},
        {'Product_Name': 'עוגה בחושה - לימון', 'Price': 45},
        {'Product_Name': 'עוגה בחושה-תבלינים', 'Price': 45},
        {'Product_Name': 'עוגה בחושה-אגוזי לוז', 'Price': 45},
        {'Product_Name': 'בגט', 'Price': 12},
        {'Product_Name': 'פוגאס', 'Price': 14},
        {'Product_Name': 'מארז עוגיות', 'Price': 43},
        {'Product_Name': 'עוגת פרג', 'Price': 60},
        {'Product_Name': 'חלה', 'Price': 18},
    ]

    for product_data in products_data:
        product = Products.objects.create(**product_data)
        print(f"Created product: {product}")

if __name__ == '__main__':
    populate_products()
