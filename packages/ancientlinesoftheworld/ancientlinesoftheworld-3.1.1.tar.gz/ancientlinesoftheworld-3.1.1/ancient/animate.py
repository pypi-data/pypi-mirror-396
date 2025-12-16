import time
import sys
from typing import Callable, Optional
from .core import AncientScripts


class AncientAnimator:
    def __init__(self, delay: float = 0.14):
        """
delay: Delay between each character (in seconds)
delay: تأخیر بین هر کاراکتر (بر حسب ثانیه)
"""

        self.delay = delay
        self.conv = AncientScripts()
        self.script_methods = {
            "pahlavi": self.conv.pahlavi,
            "cuneiform": self.conv.cuneiform,
            "manichaean": self.conv.manichaean,
            "hieroglyph": self.conv.hieroglyph,
            "Hebrew": self.conv.hebrew,
            "linear_b_optimized": self.conv.linear_b,
            "akkadian": self.conv.akkadian,
            "oracle_bone": self.conv.oracle_bone,
            "avestan": self.conv.avestan,
            "brahmi": self.conv.brahmi
        }


    def convert(self, text: str, script: str) -> str:
        if script not in self.script_methods:
            raise ValueError(f"خط '{script}' پشتیبانی نمی‌شود.")
        return self.script_methods[script](text)

    def animate_chars(
        self,
        converted_text: str,
        output_func: Optional[Callable[[str], None]] = None
    ):
        """
output_func: A callback function to receive streamed / chunked strings,
             for example it can be used in GUI or web applications.
             If None, the output will be printed to the terminal.

output_func: تابع callback برای دریافت رشته‌ها به‌صورت تکه‌تکه،
             مثلاً برای استفاده در GUI یا وب.
             اگر مقدار آن None باشد، خروجی در ترمینال چاپ می‌شود.
"""


        out = ""
        for ch in converted_text:
            out += ch
            if output_func:
                output_func(out)
            else:
                sys.stdout.write("\r" + out)
                sys.stdout.flush()
            time.sleep(self.delay)
        if not output_func:
            print()


    def run(
        self,
        text: str,
        script: str,
        output_func: Optional[Callable[[str], None]] = None
    ):
        """
text: Input text
text: متن ورودی

script: Ancient script
script: خط باستانی

output_func: Callback function for each animation step
output_func: تابع callback برای هر مرحله از انیمیشن
"""

        converted = self.convert(text, script)
        if output_func is None:
            print("\n--- شروع نوشتن باستانی ---\n")
        self.animate_chars(converted, output_func)
        if output_func is None:
            print("\n--- تمام شد ---\n")