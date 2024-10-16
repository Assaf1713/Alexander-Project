import csv
import os
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from alexander.models import Raw_Materials, Suppliers

class Command(BaseCommand):
    help = 'Populates the Raw_Materials model with data from a CSV file.'

    def handle(self, *args, **kwargs):
        data_file_path = os.path.join(os.path.dirname(__file__), '../../..', 'stock1.csv')

        if not os.path.exists(data_file_path):
            self.stdout.write(self.style.ERROR(f"CSV file not found: {data_file_path}"))
            return 

        # Print headers
        with open(data_file_path, newline='', encoding='utf-8-sig') as csvfile: 
            reader = csv.DictReader(csvfile)
            headers = [header.strip('\ufeff') for header in reader.fieldnames]  # Remove BOM character
            self.stdout.write(f"CSV headers: {headers}")


            for row in reader:
                try:
                    Raw_Materials.objects.create(
                        Material_Name=row['product'],  
                        Lower_Barrier=int(row['barrier']),  
                        Unit=row['unit'],  
                        Price=int(row['price']),  
                        Supplier=None
                        
                    )

                except KeyError as e:
                    self.stdout.write(self.style.ERROR(f"KeyError: {e}"))
                    self.stdout.write(self.style.ERROR(f"Row content causing error: {row}"))
                    continue

        self.stdout.write(self.style.SUCCESS('Successfully populated Raw_Materials model.'))



# import csv
# import os
# from django.core.management.base import BaseCommand
# from django.core.exceptions import ObjectDoesNotExist
# from alexander.models import Raw_Materials, Suppliers


# class Command(BaseCommand):
    
#     def handle(self, *args, **kwargs):
#         data = [{"Material_Name": "כוס 12", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 280, "Supplier_id": 1},
#             {"Material_Name": "כוס 8", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 170, "Supplier_id": 1},
#             {"Material_Name": "פולי קפה", "Lower_Barrier": 1,
#                 "Unit": "KG", "Price": 70, "Supplier_id": 5},
#             {"Material_Name": "סוכר חום לקפה", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 50, "Supplier_id": 1},
#             {"Material_Name": "סוכר לבן לקפה", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 45, "Supplier_id": 1},
#             {"Material_Name": "מחית וניל פשוט", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 205, "Supplier_id": 2},
#             {"Material_Name": "מחית פיסטוק", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 195, "Supplier_id": 3},
#             {"Material_Name": "מחית אוכמניות", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 65, "Supplier_id": 3},
#             {"Material_Name": "מחית מנגו", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 54, "Supplier_id": 3},
#             {"Material_Name": "מחית פטל", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 54, "Supplier_id": 3},
#             {"Material_Name": "מחית פסיפלורה", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 50, "Supplier_id": 3},
#             {"Material_Name": "מחית ליים", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 47, "Supplier_id": 3},
#             {"Material_Name": "מחית תות", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 44, "Supplier_id": 3},
#             {"Material_Name": "פטל שלם קפוא", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 34, "Supplier_id": 3},
#             {"Material_Name": "ארגז טורט", "Lower_Barrier": 3,
#                 "Unit": "ארגז", "Price": 330, "Supplier_id": 2},
#             {"Material_Name": "מארז פרפר", "Lower_Barrier": 3,
#                 "Unit": "ארגז", "Price": 225, "Supplier_id": 2},
#             {"Material_Name": "שקית מאפה אישי", "Lower_Barrier": 3,
#                 "Unit": "ארגז", "Price": 210, "Supplier_id": 2},
#             {"Material_Name": "שקית לחם", "Lower_Barrier": 3,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": 2},
#             {"Material_Name": "שמן זית", "Lower_Barrier": 4,
#                 "Unit": "KG", "Price": 50, "Supplier_id": 5},
#             {"Material_Name": "שמן זרעי ענבים", "Lower_Barrier": 4,
#                 "Unit": "KG", "Price": 29, "Supplier_id": 5},
#             {"Material_Name": "זיתים קלמטה", "Lower_Barrier": 4,
#                 "Unit": "KG", "Price": 19, "Supplier_id": 5},
#             {"Material_Name": "חלב שיבולת", "Lower_Barrier": 4,
#                 "Unit": "KG", "Price": 9, "Supplier_id": 12},
#             {"Material_Name": "חלב אורז", "Lower_Barrier": 4,
#                 "Unit": "KG", "Price": 8, "Supplier_id": 5},
#             {"Material_Name": "חלב סויה", "Lower_Barrier": 4,
#                 "Unit": "KG", "Price": 8, "Supplier_id": 5},
#             {"Material_Name": "קרים ציז", "Lower_Barrier": 5,
#                 "Unit": "KG", "Price": 32, "Supplier_id": 5},
#             {"Material_Name": "סוכר חום חבשוש", "Lower_Barrier": 6,
#                 "Unit": "KG", "Price": 10, "Supplier_id": 5},
#             {"Material_Name": "קמח אורז", "Lower_Barrier": 6,
#                 "Unit": "KG", "Price": 12, "Supplier_id": 5},
#             {"Material_Name": "חמאה לקיפולים כפר תבור", "Lower_Barrier": 7,
#                 "Unit": "KG", "Price": 35, "Supplier_id": 5},
#             {"Material_Name": "שמנת מתוקה 42", "Lower_Barrier": 7,
#                 "Unit": "KG", "Price": 19, "Supplier_id": 5},
#             {"Material_Name": "שמנת לבישול 20", "Lower_Barrier": 7,
#                 "Unit": "KG", "Price": 17, "Supplier_id": 5},
#             {"Material_Name": "חלב", "Lower_Barrier": 7,
#                 "Unit": "KG", "Price": 4, "Supplier_id": 5},
#             {"Material_Name": "מסקרפונה", "Lower_Barrier": 8,
#                 "Unit": "KG", "Price": 49, "Supplier_id": 5},
#             {"Material_Name": "חלמון", "Lower_Barrier": 9,
#                 "Unit": "KG", "Price": 24, "Supplier_id": 5},
#             {"Material_Name": "ביצים", "Lower_Barrier": 9,
#                 "Unit": "KG", "Price": 20, "Supplier_id": 5},
#             {"Material_Name": "חלבון", "Lower_Barrier": 9,
#                 "Unit": "KG", "Price": 19, "Supplier_id": 5},
#             {"Material_Name": "נוזל ביצים", "Lower_Barrier": 9,
#                 "Unit": "KG", "Price": 16, "Supplier_id": 5},
#             {"Material_Name": "פטל מיובש", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 516, "Supplier_id": 3},
#             {"Material_Name": "פקטין", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 312, "Supplier_id": 3},
#             {"Material_Name": "אלבומין", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 195, "Supplier_id": 3},
#             {"Material_Name": "קסנטן גם", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 195, "Supplier_id": 3},
#             {"Material_Name": "קרם טרטר", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 145, "Supplier_id": 3},
#             {"Material_Name": "ניילון גיטרה", "Lower_Barrier": 10,
#                 "Unit": "חבילה", "Price": 98, "Supplier_id": 1},
#             {"Material_Name": "ג'לטין", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 78, "Supplier_id": 2},
#             {"Material_Name": "שק זילוף", "Lower_Barrier": 10,
#                 "Unit": "חבילה", "Price": 65, "Supplier_id": 2},
#             {"Material_Name": "שוקולד ג'נדויה בארי", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 56, "Supplier_id": 5},
#             {"Material_Name": "מי זהר", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 49, "Supplier_id": 1},
#             {"Material_Name": "שוקולד מריר 70 saint domingue בארי",
#                 "Lower_Barrier": 10, "Unit": "KG", "Price": 49, "Supplier_id": 5},
#             {"Material_Name": "שוקולד מריר 70 ocoa בארי", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 49, "Supplier_id": 5},
#             {"Material_Name": "שוקולד מריר 64 בארי", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 49, "Supplier_id": 5},
#             {"Material_Name": "שקד פרוס", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 48, "Supplier_id": 3},
#             {"Material_Name": "אבקת קקאו בארי", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 46, "Supplier_id": 3},
#             {"Material_Name": "שוקולד חלב 38 בארי", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 43, "Supplier_id": 3},
#             {"Material_Name": "אבקת חלב", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 36, "Supplier_id": 3},
#             {"Material_Name": "תרסיס שמן", "Lower_Barrier": 10,
#                 "Unit": "יחידה", "Price": 36, "Supplier_id": 5},
#             {"Material_Name": "אבקת שקדים", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 29, "Supplier_id": 5},
#             {"Material_Name": "סוכר אינוורטי", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 28, "Supplier_id": 5},
#             {"Material_Name": "סוכר גבישי", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 18, "Supplier_id": 3},
#             {"Material_Name": "גלוקוז", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 15, "Supplier_id": 5},
#             {"Material_Name": "פונדנט", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 10, "Supplier_id": 5},
#             {"Material_Name": "אבקת סוכר", "Lower_Barrier": 10,
#                 "Unit": "KG", "Price": 6, "Supplier_id": 5},
#             {"Material_Name": "מחית וניל יקרה", "Lower_Barrier": 11,
#                 "Unit": "KG", "Price": 570, "Supplier_id": 5},
#             {"Material_Name": "קמח t55", "Lower_Barrier": 12,
#                 "Unit": "KG", "Price": 8, "Supplier_id": 25},
#             {"Material_Name": "קמח מסורתי", "Lower_Barrier": 12,
#                 "Unit": "KG", "Price": 6, "Supplier_id": 25},
#             {"Material_Name": "קמח t65", "Lower_Barrier": 12,
#                 "Unit": "KG", "Price": 6, "Supplier_id": 25},
#             {"Material_Name": "קמח לחם t550", "Lower_Barrier": 12,
#                 "Unit": "KG", "Price": 6, "Supplier_id": 25},
#             {"Material_Name": "קמח שיפון t1370", "Lower_Barrier": 12,
#                 "Unit": "KG", "Price": 6, "Supplier_id": 25},
#             {"Material_Name": "קמח מלא", "Lower_Barrier": 12,
#                 "Unit": "KG", "Price": 5, "Supplier_id": 25},
#             {"Material_Name": "קולה", "Lower_Barrier": 13,
#                 "Unit": "ארגז", "Price": 110, "Supplier_id": 3},
#             {"Material_Name": "פקאן שימורי איכות", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 69, "Supplier_id": 5},
#             {"Material_Name": "מגבת חוגלה", "Lower_Barrier": 13,
#                 "Unit": "חבילה", "Price": 65, "Supplier_id": 5},
#             {"Material_Name": "סודה", "Lower_Barrier": 13,
#                 "Unit": "ארגז", "Price": 55, "Supplier_id": 1},
#             {"Material_Name": "שקד", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 49, "Supplier_id": 5},
#             {"Material_Name": "אגוז לוז", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 49, "Supplier_id": 5},
#             {"Material_Name": "מים מינרלים קטן", "Lower_Barrier": 13,
#                 "Unit": "ארגז", "Price": 46, "Supplier_id": 1},
#             {"Material_Name": "צימוק אוזבקי", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 35, "Supplier_id": 3},
#             {"Material_Name": "אגוז מלך", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 33, "Supplier_id": 3},
#             {"Material_Name": "גרעיני דלעת", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 27, "Supplier_id": 3},
#             {"Material_Name": "ניילון נצמד", "Lower_Barrier": 13,
#                 "Unit": "חבילה", "Price": 26, "Supplier_id": 3},
#             {"Material_Name": "שומשום", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 17, "Supplier_id": 3},
#             {"Material_Name": "נייר הפרדה", "Lower_Barrier": 13,
#                 "Unit": "חבילה", "Price": 14, "Supplier_id": 2},
#             {"Material_Name": "מלח אטלנטי", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 14, "Supplier_id": 3},
#             {"Material_Name": "מים מינרלים גדול", "Lower_Barrier": 13,
#                 "Unit": "ארגז", "Price": 13, "Supplier_id": 2},
#             {"Material_Name": "גרעיני חמניה", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 13, "Supplier_id": 3},
#             {"Material_Name": "חלב שיבולת אוטלי", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 12, "Supplier_id": 6},
#             {"Material_Name": "אבקת אפיה", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 12, "Supplier_id": 5},
#             {"Material_Name": "מיקרו פייבר גדול", "Lower_Barrier": 13,
#                 "Unit": "חבילה", "Price": 10, "Supplier_id": 6},
#             {"Material_Name": "סוכר חום דמררה", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 9, "Supplier_id": 5},
#             {"Material_Name": "מיקרו פייבר קטן", "Lower_Barrier": 13,
#                 "Unit": "חבילה", "Price": 7, "Supplier_id": 6},
#             {"Material_Name": "קווקר", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 7, "Supplier_id": 5},
#             {"Material_Name": "זרעי פשתן", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 6, "Supplier_id": 5},
#             {"Material_Name": "קורנפלור", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 6, "Supplier_id": 5},
#             {"Material_Name": "סוכר לבן", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 5, "Supplier_id": 10},
#             {"Material_Name": "מלח", "Lower_Barrier": 13,
#                 "Unit": "KG", "Price": 2, "Supplier_id": 10},
#             {"Material_Name": "מפיות קוקטייל", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 185, "Supplier_id": None},
#             {"Material_Name": "רום", "Lower_Barrier": 1,
#                 "Unit": "יחידה", "Price": 179, "Supplier_id": None},
#             {"Material_Name": "נייר אפיה", "Lower_Barrier": 3,
#                 "Unit": "ארגז", "Price": 165, "Supplier_id": None},
#             {"Material_Name": "מחית אפרסק סגול", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 60, "Supplier_id": None},
#             {"Material_Name": "מחית ליצי", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 60, "Supplier_id": None},
#             {"Material_Name": "מחית רוברוב", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 60, "Supplier_id": None},
#             {"Material_Name": "מחית ברגמוט", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 60, "Supplier_id": None},
#             {"Material_Name": "מחית קסיס", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 60, "Supplier_id": None},
#             {"Material_Name": "מחית בננה", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 60, "Supplier_id": None},
#             {"Material_Name": "מחית דובדבן", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 60, "Supplier_id": None},
#             {"Material_Name": "מחית משמש", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 60, "Supplier_id": None},
#             {"Material_Name": "אוכמניות קפואות", "Lower_Barrier": 2,
#                 "Unit": "יחידה", "Price": 36, "Supplier_id": None},
#             {"Material_Name": "פלפל קלוי", "Lower_Barrier": 2,
#                 "Unit": "יחידה", "Price": 14, "Supplier_id": None},
#             {"Material_Name": "תות קפא", "Lower_Barrier": 2,
#                 "Unit": "יחידה", "Price": 12, "Supplier_id": None},
#             {"Material_Name": "חלב מרוכז", "Lower_Barrier": 6,
#                 "Unit": "יחידה", "Price": 8, "Supplier_id": None},
#             {"Material_Name": "קמח פיצה", "Lower_Barrier": 10,
#                 "Unit": "יחידה", "Price": 8, "Supplier_id": None},
#             {"Material_Name": "סכין עץ", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "מכסה כוס 8", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "נייר לקופה", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "נייר לקופה קטנה", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "כובע שיער חדפ", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "ליקר פרנגליקו", "Lower_Barrier": 1,
#                 "Unit": "יחידה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "אגר אגר", "Lower_Barrier": 1,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "צלחת מלבן", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "מזלג עץ", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "מנשא לקפה", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "ארטישוק משומר", "Lower_Barrier": 2,
#                 "Unit": "חבילה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "תה ronnefeldt תפזורת", "Lower_Barrier": 2,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "קרם ערמונים", "Lower_Barrier": 3,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "חמאת קקאו", "Lower_Barrier": 3,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "שקיות שקופות", "Lower_Barrier": 2,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "מלח מלדון", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "מי ורדים", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "מייפל", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "סודה לשתייה", "Lower_Barrier": 3,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "מדבקה גדול", "Lower_Barrier": 2,
#                 "Unit": "גליל", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "מדבקה קטן", "Lower_Barrier": 2,
#                 "Unit": "גליל", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "חומץ", "Lower_Barrier": 5,
#                 "Unit": "ליטר", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "זית מעורב", "Lower_Barrier": 3,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "שוקולד מריר 65 בארי", "Lower_Barrier": 3,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "נייר אלומיניום", "Lower_Barrier": 2,
#                 "Unit": "גליל", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "משחת ערמונים", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "טחינה", "Lower_Barrier": 3,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None}
#             {"Material_Name": "שוקולד ולרונה גוואנג'ה 70", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "שוקולד ולרונה ג'יווארה 38", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "צלחת ריבוע", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "שוקולד מריר 50 טיפות בארי", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "יחידה גז", "Lower_Barrier": 5,
#                 "Unit": "יחידה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "דבש פתורה", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "ארגז גדול", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "עגבניות משומרות", "Lower_Barrier": 2,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "שערות חלווה", "Lower_Barrier": 2,
#                 "Unit": "יחידה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "תחתיות לעוגה 24", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "שוקולד ולרונה גוואנג'ה 80", "Lower_Barrier": 3,
#                 "Unit": "KG", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "תה קוסמי", "Lower_Barrier": 2,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "המתססה משוקר", "Lower_Barrier": 12,
#                 "Unit": "יחידה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "תחתית לעוגה 18", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "המתססה סיידר", "Lower_Barrier": 12,
#                 "Unit": "יחידה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "תה ronnefeldt שקיות", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "המתססה תפוח", "Lower_Barrier": 12,
#                 "Unit": "יחידה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "קמח בגטלה", "Lower_Barrier": 25,
#                 "Unit": "יחידה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "המתססה כשות", "Lower_Barrier": 12,
#                 "Unit": "יחידה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "ריבת favols", "Lower_Barrier": 6,
#                 "Unit": "יחידה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "מיץ טבעי", "Lower_Barrier": 12,
#                 "Unit": "יחידה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "משולש לעוגה", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "המתססה אגס", "Lower_Barrier": 12,
#                 "Unit": "יחידה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "שמן חמניות", "Lower_Barrier": 5,
#                 "Unit": "ליטר", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "מיץ real", "Lower_Barrier": 12,
#                 "Unit": "יחידה", "Price": 10, "Supplier_id": None},
#             {"Material_Name": "תחתית לעוגה פס", "Lower_Barrier": 1,
#                 "Unit": "ארגז", "Price": 10, "Supplier_id": None}]
#         for item in data:
#             if item["Supplier_id"] is None:
#                 supplier=None
#             else:
#              supplier = Suppliers.objects.get(pk=item["Supplier_id"])

#             Raw_Materials.objects.create(
#                 Material_Name=item["Material_Name"],
#                  Lower_Barrier=item["Lower_Barrier"],
#                  Unit=item["Unit"],
#                  Price=item["Price"],
#                  Supplier=supplier,
#                  Quantity=0  
#                 )
#         self.stdout.write(self.style.SUCCESS('Successfully populated Raw_Materials model.'))

