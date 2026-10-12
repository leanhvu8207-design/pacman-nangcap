"""
Bảng màu, typography và hằng số phong cách Vintage Arcade / Retro Pixel Game
Dự án: Pacman AI Search - Nhóm 07
"""

import pygame

# ==============================================================================
# BẢNG MÀU RETRO ARCADE (VINTAGE PALETTE)
# ==============================================================================

# Background & Panels (Xanh đen trầm / Nâu sẫm arcade thập niên 80-90)
BG_MAIN = (17, 19, 31)          # Xanh đen trầm cổ điển (Cabinet background)
BG_PANEL = (24, 27, 44)         # Khối bảng điều khiển (Control panel slate)
BG_PANEL_ALT = (31, 35, 56)     # Khối phụ / Thống kê
BG_BEZEL = (41, 47, 74)         # Viền bo arcade bezel
BORDER_COLOR = (54, 63, 98)     # Viền ngăn cách giữa các khu vực
BORDER_HIGHLIGHT = (82, 95, 142)# Viền sáng nhẹ tạo chiều sâu 3D arcade

# Pacman (Vàng cổ điển - Điểm nhấn chính của giao diện)
COLOR_PACMAN = (255, 214, 10)       # Vàng chanh retro ấm
COLOR_PACMAN_MOUTH = (17, 19, 31)   # Màu miệng khi mở

# Ghost (Mỗi con một màu retro đặc trưng - TUYỆT ĐỐI KHÔNG DÙNG MÀU VÀNG)
GHOST_COLORS = [
    (235, 68, 68),    # Ghost 0: Đỏ gạch Blinky (Blinky Red)
    (38, 198, 218),   # Ghost 1: Xanh ngọc Inky (Cyan / Teal)
    (240, 98, 146),   # Ghost 2: Hồng tím Pinky (Vintage Pink)
    (255, 112, 67),   # Ghost 3: Cam gạch Clyde (Retro Orange)
    (171, 71, 188),   # Ghost 4: Tím thẫm (Retro Violet)
    (77, 182, 172),   # Ghost 5: Xanh mint sẫm (Mint Ghost)
]
GHOST_EYE_WHITE = (248, 250, 252)   # Tròng mắt trắng
GHOST_PUPIL_BLUE = (30, 58, 138)    # Con ngươi xanh đậm

# Mê cung (Maze Elements)
WALL_FILL = (18, 38, 82)            # Tường xanh navy đậm cổ điển
WALL_BORDER = (45, 95, 185)         # Viền tường sáng nét
WALL_INNER = (28, 56, 120)          # Lớp trong tường
FOOD_PELLET = (254, 240, 138)       # Thức ăn: chấm nhỏ màu kem / vàng nhạt
FOOD_GLOW = (250, 204, 21)          # Ánh sáng dịu của food
GOAL_POINT = (52, 211, 153)         # Điểm đích Goal (G): Xanh mint retro
GOAL_BORDER = (16, 185, 129)

# Màu chữ & Điểm nhấn (Typography & Accents)
TEXT_TITLE = (255, 214, 10)         # Tiêu đề vàng arcade
TEXT_HEADER = (241, 245, 249)       # Chữ trắng ngà kem
TEXT_BODY = (203, 213, 225)         # Chữ nội dung xám sáng
TEXT_MUTED = (148, 163, 184)        # Chữ mờ ghi chú
TEXT_OLD_PAPER = (226, 212, 183)    # Màu giấy cũ retro (Old paper accent)

# Trạng thái game (Badges)
STATUS_COLORS = {
    "READY": (148, 163, 184),       # Xám retro
    "RUNNING": (56, 189, 248),      # Xanh cyan đang chạy
    "WIN": (52, 211, 153),          # Xanh mint chiến thắng
    "LOSE": (248, 113, 113),        # Đỏ gạch thua cuộc
    "PAUSED": (251, 191, 36),       # Vàng hổ phách tạm dừng
    "ERROR": (239, 68, 68),         # Đỏ cảnh báo lỗi
}

# Nút bấm (Button Themes)
BTN_NORMAL = (35, 41, 66)
BTN_HOVER = (48, 56, 90)
BTN_ACTIVE = (255, 214, 10)         # Nút đang được chọn: sáng vàng
BTN_TEXT_ACTIVE = (17, 19, 31)      # Chữ màu tối trên nền active
BTN_ACTION_START = (16, 149, 106)   # Nút Start xanh retro
BTN_ACTION_START_H = (22, 180, 128)
BTN_ACTION_STOP = (185, 45, 45)     # Nút Stop/Reset đỏ gạch
BTN_ACTION_STOP_H = (220, 55, 55)
BTN_ACTION_PAUSE = (180, 130, 25)   # Nút Pause vàng hổ phách
BTN_ACTION_PAUSE_H = (215, 155, 30)


# ==============================================================================
# QUẢN LÝ FONT CHỮ RETRO (TYPOGRAPHY)
# ==============================================================================
_fonts = {}

def init_fonts():
    """Khởi tạo font chữ hệ thống monospaced retro: Consolas / Courier New / Fallback"""
    if not pygame.font.get_init():
        pygame.font.init()

    # Thử các font retro monospaced sắc nét phổ biến trên Windows
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

def get_font(key):
    """Lấy font chữ theo kích cỡ"""
    if not _fonts:
        init_fonts()
    return _fonts.get(key, pygame.font.Font(None, 14))


# ==============================================================================
# HÀM VẼ TIỆN ÍCH RETRO (BEVEL & BORDER)
# ==============================================================================
def draw_arcade_panel(surface, rect, bg_color=BG_PANEL, border_color=BORDER_COLOR, corner_radius=6):
    """Vẽ panel phong cách arcade có bo góc nhẹ và viền đổ bóng nổi"""
    # Nền panel
    pygame.draw.rect(surface, bg_color, rect, border_radius=corner_radius)
    # Viền ngoài
    pygame.draw.rect(surface, border_color, rect, width=2, border_radius=corner_radius)
    # Đường highlight trên đầu để tạo chiều sâu máy arcade cổ điển
    top_highlight = pygame.Rect(rect.x + 2, rect.y + 1, rect.width - 4, 1)
    pygame.draw.rect(surface, BORDER_HIGHLIGHT, top_highlight)
