"""
Bộ vẽ đồ họa Mê cung, Nhân vật Pacman và Ghost phong cách Vintage Arcade
Dự án: Pacman AI Search - Nhóm 07
"""

import math
import pygame
from ui.theme import (
    COLOR_PACMAN,
    COLOR_PACMAN_MOUTH,
    GHOST_COLORS,
    GHOST_EYE_WHITE,
    GHOST_PUPIL_BLUE,
    WALL_FILL,
    WALL_BORDER,
    WALL_INNER,
    WATER_FILL,
    WATER_BORDER,
    SWAMP_FILL,
    SWAMP_BORDER,
    FOOD_PELLET,
    FOOD_GLOW,
    GOAL_POINT,
    GOAL_BORDER,
    BG_BEZEL,
    BORDER_COLOR,
    BORDER_HIGHLIGHT,
    get_font,
)


class MazeRenderer:
    """Renderer chuyên biệt cho bản đồ Pacman và các thực thể"""

    def __init__(self, viewport_rect):
        self.viewport_rect = pygame.Rect(viewport_rect)
        self.tile_size = 32
        self.origin_x = self.viewport_rect.x
        self.origin_y = self.viewport_rect.y
        self.rows = 0
        self.cols = 0
        self.mouth_angle = 35
        self.mouth_closing = True
        self.animation_tick = 0

    def compute_layout(self, game_map):
        """Tính toán kích thước tile và vị trí căn giữa viewport"""
        if not game_map:
            return
        self.rows = len(game_map)
        self.cols = max(len(row) for row in game_map) if self.rows > 0 else 0

        if self.rows == 0 or self.cols == 0:
            return

        avail_w = self.viewport_rect.width - 24
        avail_h = self.viewport_rect.height - 24

        max_tile_w = avail_w // self.cols
        max_tile_h = avail_h // self.rows

        # Giới hạn kích thước ô từ 16px đến 48px
        self.tile_size = max(16, min(48, min(max_tile_w, max_tile_h)))

        maze_w = self.cols * self.tile_size
        maze_h = self.rows * self.tile_size

        self.origin_x = self.viewport_rect.x + (self.viewport_rect.width - maze_w) // 2
        self.origin_y = self.viewport_rect.y + (self.viewport_rect.height - maze_h) // 2

    def update_animation(self):
        """Cập nhật chuyển động há mồm của Pacman và chân ma"""
        self.animation_tick += 1
        if self.mouth_closing:
            self.mouth_angle -= 3
            if self.mouth_angle <= 5:
                self.mouth_closing = False
        else:
            self.mouth_angle += 3
            if self.mouth_angle >= 42:
                self.mouth_closing = True

    def grid_to_screen(self, row, col):
        """Chuyển tọa độ lưới (row, col) sang tọa độ màn hình (x, y) trung tâm ô"""
        cx = self.origin_x + int(col * self.tile_size + self.tile_size / 2)
        cy = self.origin_y + int(row * self.tile_size + self.tile_size / 2)
        return cx, cy

    def draw_maze(self, surface, game_map, remaining_food=None, goals=None, path_trail=None, is_win=False):
        """Vẽ khung viền arcade, mê cung tường, thức ăn, điểm đích và đường đi mờ / nét nối"""
        # 1. Vẽ khung arcade màn hình CRT / Bezel
        pygame.draw.rect(surface, (12, 14, 22), self.viewport_rect, border_radius=8)
        pygame.draw.rect(surface, BORDER_COLOR, self.viewport_rect, width=2, border_radius=8)
        top_bevel = pygame.Rect(self.viewport_rect.x + 2, self.viewport_rect.y + 1, self.viewport_rect.width - 4, 1)
        pygame.draw.rect(surface, BORDER_HIGHLIGHT, top_bevel)

        if not game_map:
            # Thông báo nếu chưa có bản đồ
            font = get_font("header")
            msg = font.render("[ NO MAP LOADED ]", True, (120, 130, 160))
            surface.blit(msg, msg.get_rect(center=self.viewport_rect.center))
            return

        ts = self.tile_size

        # 2. Vẽ tường và nền mê cung
        for r in range(len(game_map)):
            for c in range(len(game_map[r])):
                char = game_map[r][c]
                rx = self.origin_x + c * ts
                ry = self.origin_y + r * ts
                tile_rect = pygame.Rect(rx, ry, ts, ts)

                if char == "#":
                    # Khối tường Arcade: lớp ngoài xanh navy đậm, viền xanh sáng
                    pygame.draw.rect(surface, WALL_FILL, tile_rect)
                    pygame.draw.rect(surface, WALL_BORDER, tile_rect, width=1)
                    # Lớp lõi bên trong tạo khối nổi retro
                    if ts >= 20:
                        inner_rect = tile_rect.inflate(-4, -4)
                        pygame.draw.rect(surface, WALL_INNER, inner_rect, width=1)
                elif char == "~":
                    # Ô Nước (Chi phí 2)
                    pygame.draw.rect(surface, WATER_FILL, tile_rect)
                    pygame.draw.rect(surface, WATER_BORDER, tile_rect, width=1)
                elif char == "S":
                     # Ô Đầm lầy (Chi phí 3)
                    pygame.draw.rect(surface, SWAMP_FILL, tile_rect)
                    pygame.draw.rect(surface, SWAMP_BORDER, tile_rect, width=1)
                else:
                    # Đường đi trống (nền tối mờ retro)
                    pygame.draw.rect(surface, (15, 17, 27), tile_rect)

        # 3. Vẽ vệt đường mờ mờ đã đi và đường kẻ kết nối lộ trình (Path trail)
        if path_trail and len(path_trail) > 0:
            self.draw_path_trail(surface, path_trail, is_win=is_win)

        # 4. Vẽ Thức ăn Food (.)
        food_set = remaining_food if remaining_food is not None else set()
        for r in range(len(game_map)):
            for c in range(len(game_map[r])):
                pos = (r, c)
                char = game_map[r][c]
                # Nếu có remaining_food thì vẽ theo set, ngược lại vẽ theo ký tự gốc
                is_food = (pos in food_set) if remaining_food is not None else (char == ".")

                if is_food:
                    cx, cy = self.grid_to_screen(r, c)
                    dot_radius = max(2, int(ts * 0.16))
                    # Quầng sáng dịu nhẹ
                    if ts >= 24:
                        pygame.draw.circle(surface, FOOD_GLOW, (cx, cy), dot_radius + 2, width=1)
                    # Chấm ngà vàng nhạt
                    pygame.draw.circle(surface, FOOD_PELLET, (cx, cy), dot_radius)

        # 5. Vẽ Điểm đích Goal (G)
        goal_list = goals if goals is not None else []
        for gr, gc in goal_list:
            cx, cy = self.grid_to_screen(gr, gc)
            radius = max(4, int(ts * 0.36))

            # Vòng hào quang xanh mint
            pygame.draw.circle(surface, GOAL_BORDER, (cx, cy), radius + 2, width=2)
            # Biểu tượng hình thoi / ngôi sao retro cho Goal
            points = [
                (cx, cy - radius),
                (cx + radius, cy),
                (cx, cy + radius),
                (cx - radius, cy),
            ]
            pygame.draw.polygon(surface, GOAL_POINT, points)
            if ts >= 26:
                # Chữ 'G' nhỏ ở tâm
                font_g = get_font("small")
                g_txt = font_g.render("G", True, (15, 23, 42))
                surface.blit(g_txt, g_txt.get_rect(center=(cx, cy)))

    def draw_path_trail(self, surface, path_trail, is_win=False):
        """
        Vẽ vệt mờ mờ các ô đã đi và đường kẻ phát sáng nối liền các đoạn lộ trình.
        - Các ô đã đi qua: phủ một lớp màu mờ (translucent footprint), kèm chấm tâm waypoint.
        - Đường kẻ: đường line neon kép nối từ điểm xuất phát tới đích, có mũi tên chỉ hướng.
        - Khi tới Goal (is_win=True): đổi sang màu xanh mint / ánh vàng rực rỡ, vòng aura tại Goal.
        """
        if not path_trail or len(path_trail) == 0:
            return

        ts = self.tile_size
        vw = self.viewport_rect.width
        vh = self.viewport_rect.height

        # Tạo surface trong suốt để vẽ vệt mờ và đường kẻ neon
        trail_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)

        # 1. Vẽ các ô mờ mờ đã đi qua (Faded visited tiles)
        tile_alpha = 70 if is_win else 45
        dot_alpha = 190 if is_win else 140

        tile_color = (52, 211, 153, tile_alpha) if is_win else (38, 198, 218, tile_alpha)
        dot_color = (52, 211, 153, dot_alpha) if is_win else (38, 198, 218, dot_alpha)

        # Tránh vẽ đè ô trùng nhiều lần nếu Pacman đi qua lại
        visited_set = set(path_trail)
        for r, c in visited_set:
            cx, cy = self.grid_to_screen(r, c)
            lx = cx - self.viewport_rect.x
            ly = cy - self.viewport_rect.y

            # Vẽ ô nền mờ mờ bo góc
            box_margin = max(1, ts // 10)
            local_rect = pygame.Rect(
                self.origin_x + c * ts - self.viewport_rect.x + box_margin,
                self.origin_y + r * ts - self.viewport_rect.y + box_margin,
                ts - 2 * box_margin,
                ts - 2 * box_margin
            )
            pygame.draw.rect(trail_surf, tile_color, local_rect, border_radius=4)
            # Chấm tâm mờ
            pygame.draw.circle(trail_surf, dot_color, (lx, ly), max(2, ts // 8))

        # 2. Vẽ đường kẻ kết nối các đoạn đã đi (Connecting path line)
        if len(path_trail) > 1:
            glow_col = (16, 185, 129, 140) if is_win else (6, 182, 212, 110)
            core_col = (254, 240, 138, 240) if is_win else (165, 243, 252, 230)
            arrow_col = (255, 214, 10, 230) if is_win else (103, 232, 249, 210)

            glow_w = max(4, int(ts * 0.28))
            core_w = max(2, int(ts * 0.10))

            for i in range(len(path_trail) - 1):
                p1_grid = path_trail[i]
                p2_grid = path_trail[i + 1]
                if p1_grid == p2_grid:
                    continue

                cx1, cy1 = self.grid_to_screen(p1_grid[0], p1_grid[1])
                cx2, cy2 = self.grid_to_screen(p2_grid[0], p2_grid[1])
                p1 = (cx1 - self.viewport_rect.x, cy1 - self.viewport_rect.y)
                p2 = (cx2 - self.viewport_rect.x, cy2 - self.viewport_rect.y)

                # Vẽ nét phát sáng neon ngoài
                pygame.draw.line(trail_surf, glow_col, p1, p2, width=glow_w)
                # Vẽ nét sáng rõ bên trong
                pygame.draw.line(trail_surf, core_col, p1, p2, width=core_w)

                # Điểm chốt góc / khớp nối (joint bead)
                pygame.draw.circle(trail_surf, core_col, p1, max(2, int(ts * 0.10)))
                pygame.draw.circle(trail_surf, core_col, p2, max(2, int(ts * 0.10)))

                # Mũi tên chỉ hướng nhỏ ở giữa đoạn kẻ
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                dist = math.hypot(dx, dy)
                if dist >= ts * 0.6:
                    ux = dx / dist
                    uy = dy / dist
                    px = -uy
                    py = ux
                    mid_x = (p1[0] + p2[0]) / 2
                    mid_y = (p1[1] + p2[1]) / 2

                    ar_size = max(3, int(ts * 0.14))
                    tip = (mid_x + ux * ar_size, mid_y + uy * ar_size)
                    left_w = (mid_x - ux * ar_size * 0.8 + px * ar_size * 0.8,
                              mid_y - uy * ar_size * 0.8 + py * ar_size * 0.8)
                    right_w = (mid_x - ux * ar_size * 0.8 - px * ar_size * 0.8,
                               mid_y - uy * ar_size * 0.8 - py * ar_size * 0.8)
                    pygame.draw.polygon(trail_surf, arrow_col, [tip, left_w, right_w])

        # 3. Điểm bắt đầu (Spawn) và Điểm kết thúc / Goal
        p_start_c = self.grid_to_screen(path_trail[0][0], path_trail[0][1])
        ls_start = (p_start_c[0] - self.viewport_rect.x, p_start_c[1] - self.viewport_rect.y)
        pygame.draw.circle(trail_surf, (245, 197, 66, 200), ls_start, max(4, int(ts * 0.26)), width=2)

        if is_win and len(path_trail) > 1:
            p_end_c = self.grid_to_screen(path_trail[-1][0], path_trail[-1][1])
            ls_end = (p_end_c[0] - self.viewport_rect.x, p_end_c[1] - self.viewport_rect.y)
            # Vòng hào quang chiến thắng tại điểm tới đích
            pygame.draw.circle(trail_surf, (52, 211, 153, 190), ls_end, max(6, int(ts * 0.38)), width=2)
            pygame.draw.circle(trail_surf, (255, 214, 10, 160), ls_end, max(9, int(ts * 0.52)), width=1)

        # Blit toàn bộ surface trong suốt lên surface chính
        surface.blit(trail_surf, (self.viewport_rect.x, self.viewport_rect.y))

    def draw_pacman(self, surface, pos_row, pos_col, direction="RIGHT"):
        """Vẽ Pacman vàng cổ điển với hình tròn và miệng mở theo hướng"""
        cx, cy = self.grid_to_screen(pos_row, pos_col)
        radius = max(5, int(self.tile_size * 0.44))

        # Xác định góc xoay theo hướng di chuyển
        angle_offsets = {
            "RIGHT": 0,
            "DOWN": 90,
            "LEFT": 180,
            "UP": 270,
        }
        base_angle = angle_offsets.get(direction, 0)
        mouth_deg = max(4, self.mouth_angle)

        # Góc há miệng trái và phải
        start_angle = math.radians(base_angle + mouth_deg)
        end_angle = math.radians(base_angle + 360 - mouth_deg)

        # Vẽ hình quạt Pacman vàng
        points = [(cx, cy)]
        steps = 28
        for i in range(steps + 1):
            theta = start_angle + (end_angle - start_angle) * (i / steps)
            px = cx + radius * math.cos(theta)
            py = cy + radius * math.sin(theta)
            points.append((px, py))

        # Thân vàng Pacman
        pygame.draw.polygon(surface, COLOR_PACMAN, points)
        # Viền sắc nét retro
        pygame.draw.polygon(surface, (218, 165, 32), points, width=1)

        # Mắt nhỏ cổ điển của Pacman khi miệng mở
        if radius >= 8:
            eye_angle = math.radians(base_angle - 70)
            ex = cx + int(radius * 0.55 * math.cos(eye_angle))
            ey = cy + int(radius * 0.55 * math.sin(eye_angle))
            pygame.draw.circle(surface, (20, 20, 20), (ex, ey), max(1, radius // 7))

    def draw_ghost(self, surface, ghost_index, pos_row, pos_col, facing_dir="DOWN"):
        """Vẽ Ghost cổ điển với các màu khác biệt (TUYỆT ĐỐI KHÔNG CÓ MÀU VÀNG)"""
        cx, cy = self.grid_to_screen(pos_row, pos_col)
        r = max(5, int(self.tile_size * 0.42))

        # Chọn màu riêng cho từng con ghost
        ghost_color = GHOST_COLORS[ghost_index % len(GHOST_COLORS)]

        # Tọa độ đỉnh vòm
        top_y = cy - r
        bot_y = cy + r - max(1, r // 4)

        # 1. Vẽ thân ma hình vòm phía trên và lượn sóng phía dưới
        points = []

        # Nửa cung tròn đỉnh đầu ma
        for deg in range(180, 361, 15):
            rad = math.radians(deg)
            px = cx + r * math.cos(rad)
            py = (cy - int(r * 0.2)) + r * 0.8 * math.sin(rad)
            points.append((px, py))

        # Chân ma lượn sóng (3 xúc tu arcade chân ma)
        wave_shift = (self.animation_tick // 6) % 2 * 2  # Nhún nhảy retro
        tentacles = 3
        w_step = (2 * r) / tentacles
        for i in range(tentacles):
            x_start = cx + r - i * w_step
            x_mid = x_start - w_step / 2
            x_end = x_start - w_step
            y_base = cy + r
            y_dip = cy + r - max(2, r // 3) + wave_shift
            points.append((x_start, y_dip))
            points.append((x_mid, y_base))
            points.append((x_end, y_dip))

        # Tô màu thân ma
        pygame.draw.polygon(surface, ghost_color, points)
        # Viền sắc nét
        pygame.draw.polygon(surface, (30, 35, 50), points, width=1)

        # 2. Hai mắt tròn trắng to retro
        eye_radius_x = max(2, int(r * 0.32))
        eye_radius_y = max(3, int(r * 0.40))
        pupil_radius = max(1, int(r * 0.16))

        eye_dx = int(r * 0.38)
        eye_dy = int(r * 0.15)

        # Hướng nhìn của con ngươi
        p_off_x, p_off_y = 0, 0
        if facing_dir == "LEFT":
            p_off_x = -max(1, eye_radius_x // 2)
        elif facing_dir == "RIGHT":
            p_off_x = max(1, eye_radius_x // 2)
        elif facing_dir == "UP":
            p_off_y = -max(1, eye_radius_y // 2)
        elif facing_dir == "DOWN":
            p_off_y = max(1, eye_radius_y // 2)

        left_eye_center = (cx - eye_dx, cy - eye_dy)
        right_eye_center = (cx + eye_dx, cy - eye_dy)

        # Vẽ tròng mắt trắng
        pygame.draw.ellipse(surface, GHOST_EYE_WHITE,
                            pygame.Rect(left_eye_center[0] - eye_radius_x, left_eye_center[1] - eye_radius_y,
                                         eye_radius_x * 2, eye_radius_y * 2))
        pygame.draw.ellipse(surface, GHOST_EYE_WHITE,
                            pygame.Rect(right_eye_center[0] - eye_radius_x, right_eye_center[1] - eye_radius_y,
                                         eye_radius_x * 2, eye_radius_y * 2))

        # Vẽ con ngươi màu xanh đậm nhìn theo hướng
        pygame.draw.circle(surface, GHOST_PUPIL_BLUE,
                           (left_eye_center[0] + p_off_x, left_eye_center[1] + p_off_y), pupil_radius)
        pygame.draw.circle(surface, GHOST_PUPIL_BLUE,
                           (right_eye_center[0] + p_off_x, right_eye_center[1] + p_off_y), pupil_radius)
