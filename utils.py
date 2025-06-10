"""
وظائف مساعدة لبرنامج رواتب الموظفين
"""
from datetime import datetime, date
from typing import Union
import re


def validate_email(email: str) -> bool:
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """التحقق من صحة رقم الهاتف"""
    # إزالة المسافات والرموز
    clean_phone = re.sub(r'[^\d+]', '', phone)
    # التحقق من أن الرقم يحتوي على أرقام فقط (مع إمكانية وجود + في البداية)
    pattern = r'^\+?[0-9]{8,15}$'
    return re.match(pattern, clean_phone) is not None


def format_currency(amount: float, currency: str = "ريال") -> str:
    """تنسيق المبلغ المالي"""
    return f"{amount:,.2f} {currency}"


def parse_date(date_str: str) -> datetime:
    """تحويل النص إلى تاريخ"""
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"تنسيق التاريخ غير صحيح: {date_str}")


def format_date(date_obj: Union[datetime, date], format_str: str = '%Y-%m-%d') -> str:
    """تنسيق التاريخ"""
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_str)
    elif isinstance(date_obj, date):
        return date_obj.strftime(format_str)
    else:
        return str(date_obj)


def validate_employee_id(employee_id: str) -> bool:
    """التحقق من صحة رقم الموظف"""
    # يجب أن يكون رقم الموظف من 3-10 أحرف/أرقام
    pattern = r'^[A-Za-z0-9]{3,10}$'
    return re.match(pattern, employee_id) is not None


def calculate_age(birth_date: datetime) -> int:
    """حساب العمر"""
    today = datetime.now()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age


def get_month_name(month_number: int) -> str:
    """الحصول على اسم الشهر بالعربية"""
    months = {
        1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
        5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
        9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
    }
    return months.get(month_number, "غير معروف")


def validate_amount(amount: str) -> bool:
    """التحقق من صحة المبلغ المالي"""
    try:
        float_amount = float(amount)
        return float_amount >= 0
    except ValueError:
        return False


def clean_text(text: str) -> str:
    """تنظيف النص من المسافات الزائدة"""
    if not text:
        return ""
    return text.strip()


def generate_reference_number() -> str:
    """إنتاج رقم مرجع فريد"""
    from datetime import datetime
    import random
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_num = random.randint(1000, 9999)
    return f"REF{timestamp}{random_num}"


class ValidationError(Exception):
    """خطأ في التحقق من البيانات"""
    pass


def validate_employee_data(name: str, employee_id: str, email: str = None, 
                         phone: str = None, base_salary: str = None) -> list:
    """التحقق من صحة بيانات الموظف"""
    errors = []
    
    # التحقق من الاسم
    if not name or len(clean_text(name)) < 2:
        errors.append("اسم الموظف مطلوب ويجب أن يكون أكثر من حرفين")
    
    # التحقق من رقم الموظف
    if not employee_id or not validate_employee_id(employee_id):
        errors.append("رقم الموظف مطلوب ويجب أن يكون من 3-10 أحرف أو أرقام")
    
    # التحقق من البريد الإلكتروني
    if email and not validate_email(email):
        errors.append("البريد الإلكتروني غير صحيح")
    
    # التحقق من رقم الهاتف
    if phone and not validate_phone(phone):
        errors.append("رقم الهاتف غير صحيح")
    
    # التحقق من الراتب الأساسي
    if base_salary and not validate_amount(base_salary):
        errors.append("الراتب الأساسي يجب أن يكون رقماً موجباً")
    
    return errors


def validate_financial_entry(amount: str, date_str: str = None) -> list:
    """التحقق من صحة الإدخال المالي"""
    errors = []
    
    # التحقق من المبلغ
    if not amount or not validate_amount(amount):
        errors.append("المبلغ مطلوب ويجب أن يكون رقماً موجباً")
    
    # التحقق من التاريخ
    if date_str:
        try:
            parse_date(date_str)
        except ValueError:
            errors.append("تنسيق التاريخ غير صحيح")
    
    return errors
