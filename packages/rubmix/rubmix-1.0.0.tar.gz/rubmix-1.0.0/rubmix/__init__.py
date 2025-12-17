# rubmix/__init__.py

# ۱. ایمپورت کلاس‌های سازنده و تعریف نام مستعار تمیز
# این کلاس‌ها از builders.py می‌آیند.
from .builders import InlineBuilder as RubmixInlineBuilder
from .builders import ChatKeypadBuilder as RubmixChatBuilder

# ۲. ایمپورت مستقیم تابع تبدیل از converters.py
# این کار تابع را مستقیماً زیر ماژول rubmix قرار می‌دهد.
from .converters import rubmix_to_keypad # <--- این خط کلید حل مشکل است!

# ۳. تعریف نسخه (اختیاری)
__version__ = "1.0.0" 

# حالا در کد کاربر، هر سه مورد زیر مستقیماً قابل دسترسی هستند:
# rubmix.RubmixInlineBuilder
# rubmix.RubmixChatBuilder
# rubmix.rubmix_to_keypad