import gettext
from pathlib import Path


本地化目录 = Path(__file__).parent

翻译对象: gettext.GNUTranslations = gettext.translation('xmpy_ctastrategy', localedir=本地化目录, fallback=True)

_ = 翻译对象.gettext
