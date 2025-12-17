# rubmix/converters.py
from rubpy.bot.models import Keypad, KeypadRow, Button 
from typing import Dict, Any

def rubmix_to_keypad(rubmix_keypad_dict: Dict[str, Any]) -> Keypad:
    """
    دیکشنری خروجی rubmix (rubka) را به شیء Keypad از rubpy تبدیل می‌کند.
    """
    keypad_rows = []
    
    for row_dict in rubmix_keypad_dict.get("rows", []):
        buttons_list = []
        
        for button_dict in row_dict.get("buttons", []):
            # اگر چه rubpy Button dataclass است، اما constructor آن دیکشنری را می‌پذیرد.
            button_object = Button(**button_dict)
            buttons_list.append(button_object)

        keypad_row_object = KeypadRow(buttons=buttons_list)
        keypad_rows.append(keypad_row_object)

    # گرفتن پارامترهای اضافی (برای ChatKeypad)
    final_keypad = Keypad(
        rows=keypad_rows,
        resize_keyboard=rubmix_keypad_dict.get("resize_keyboard"),
        on_time_keyboard=rubmix_keypad_dict.get("on_time_keyboard")
    )
    
    return final_keypad