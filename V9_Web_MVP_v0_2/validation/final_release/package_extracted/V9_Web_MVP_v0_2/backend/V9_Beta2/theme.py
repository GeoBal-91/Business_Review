"""Visual constants only; no data or rendering side effects."""
from pathlib import Path
from pptx.dml.color import RGBColor
from config import BASE_DIR, FONT

ASSETS_DIR = BASE_DIR / "assets"
LOGO_FILE = BASE_DIR / "Logo.png"
PARTNER_LOGO_FILE = BASE_DIR / "Partner Logo.png"

YELLOW = RGBColor(242, 204, 56)
GREEN = RGBColor(0, 160, 130)
RED = RGBColor(210, 70, 70)
ORANGE = RGBColor(230, 145, 50)

DARK = RGBColor(35, 35, 35)
GREY = RGBColor(110, 110, 110)
LIGHT_GREY = RGBColor(242, 242, 242)
HEADER_GREY = RGBColor(235, 235, 235)
MID_GREY = RGBColor(220, 220, 220)
WHITE = RGBColor(255, 255, 255)

MPL_YELLOW = "#F2CC38"
MPL_GREEN = "#00A082"
MPL_RED = "#D24646"
MPL_ORANGE = "#E69132"
MPL_GREY = "#8A8A8A"
MPL_DARK = "#232323"
MPL_LIGHT_GREY = "#F2F2F2"


