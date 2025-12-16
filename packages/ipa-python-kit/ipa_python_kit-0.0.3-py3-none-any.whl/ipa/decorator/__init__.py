__doc__ = """
装饰器模块
"""

from .exception import *

try:
    # 3.13+才有
    from warnings import deprecated
except:
    from deprecated import deprecated
