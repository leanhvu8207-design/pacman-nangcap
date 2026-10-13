"""
Bảng màu, typography và hằng số phong cách Vintage Arcade / Retro Pixel Game
Dự án: Pacman AI Search - Nhóm 07
"""

import pygame

BG_MAIN = (17, 19, 31)
BG_PANEL = (24, 27, 44)
BG_PANEL_ALT = (31, 35, 56)
BG_BEZEL = (41, 47, 74)
BORDER_COLOR = (54, 63, 98)
BORDER_HIGHLIGHT = (82, 95, 142)

COLOR_PACMAN = (255, 214, 10)
COLOR_PACMAN_MOUTH = (17, 19, 31)

GHOST_COLORS = [
    (235, 68, 68),
    (38, 198, 218),
    (240, 98, 146),
    (255, 112, 67),
    (171, 71, 188),
    (77, 182, 172),
]
GHOST_EYE_WHITE = (248, 250, 252)
GHOST_PUPIL_BLUE = (30, 58, 138)

WALL_FILL = (18, 38, 82)
WALL_BORDER = (45, 95, 185)
WALL_INNER = (28, 56, 120)
FOOD_PELLET = (254, 240, 138)
FOOD_GLOW = (250, 204, 21)
GOAL_POINT = (52, 211, 153)
GOAL_BORDER = (16, 185, 129)

TEXT_TITLE = (255, 214, 10)
TEXT_HEADER = (241, 245, 249)
TEXT_BODY = (203, 213, 225)
TEXT_MUTED = (148, 163, 184)
TEXT_OLD_PAPER = (226, 212, 183)

STATUS_COLORS = {
    "READY": (148, 163, 184),
    "RUNNING": (56, 189, 248),
    "WIN": (52, 211, 153),
    "LOSE": (248, 113, 113),
    "PAUSED": (251, 191, 36),
    "ERROR": (239, 68, 68),
}

BTN_NORMAL = (35, 41, 66)
BTN_HOVER = (48, 56, 90)
BTN_ACTIVE = (255, 214, 10)
BTN_TEXT_ACTIVE = (17, 19, 31)
BTN_ACTION_START = (16, 149, 106)
BTN_ACTION_START_H = (22, 180, 128)
BTN_ACTION_STOP = (185, 45, 45)
BTN_ACTION_STOP_H = (220, 55, 55)
BTN_ACTION_PAUSE = (180, 130, 25)
BTN_ACTION_PAUSE_H = (215, 155, 30)

_fonts = {}

def init_fonts():
    """Khởi tạo font chữ hệ thống monospaced retro: Consolas / Courier New / Fallback"""
    if not pygame.font.get_init():
        pygame.font.init()

    candidate_fonts = ["consolas", "lucidaconsole", "couriernew", "dejavusansmono"]
    chosen_font_name = None

    for name in candidate_fonts:
        if pygame.font.match_font(name):
            chosen_font_name = name
            break

    sizes = {
        "title": 26,
        "header": 18,
        "subtitle": 15,
        "body": 13,
        "small": 11,
        "log": 12,
        "badge": 14,
    }

    for key, size in sizes.items():
        try:
            if chosen_font_name:
                _fonts[key] = pygame.font.SysFont(chosen_font_name, size, bold=(key in ["title", "header", "badge"]))
            else:
                _fonts[key] = pygame.font.Font(None, size)
        except Exception:
            _fonts[key] = pygame.font.Font(None, size)

_fallback_font = None

def get_font(key):
    """Lấy font chữ theo kích cỡ (được cache 100%, không cấp phát lại trong render loop)"""
    global _fallback_font
    if not _fonts:
        init_fonts()
    font = _fonts.get(key)
    if font is not None:
        return font
    if _fallback_font is None:
        _fallback_font = pygame.font.Font(None, 14)
    return _fallback_font

def draw_arcade_panel(surface, rect, bg_color=BG_PANEL, border_color=BORDER_COLOR, corner_radius=6):
    """Vẽ panel phong cách arcade có bo góc nhẹ và viền đổ bóng nổi"""
    pygame.draw.rect(surface, bg_color, rect, border_radius=corner_radius)
    pygame.draw.rect(surface, border_color, rect, width=2, border_radius=corner_radius)
    top_highlight = pygame.Rect(rect.x + 2, rect.y + 1, rect.width - 4, 1)
    pygame.draw.rect(surface, BORDER_HIGHLIGHT, top_highlight)
