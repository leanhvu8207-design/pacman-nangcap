"""
Bộ duyệt và xem trước toàn cảnh bản đồ (Map Browser & Overview Preview)
Phong cách Vintage Arcade - Dự án: Pacman AI Search - Nhóm 07
"""

import os
import pygame
from src.utils.map_loader import load_map
from src.utils.map_info import get_map_info
from ui.theme import (
    get_font,
    draw_arcade_panel,
    BG_MAIN,
    BG_PANEL,
    BG_PANEL_ALT,
    BORDER_COLOR,
    BORDER_HIGHLIGHT,
    COLOR_PACMAN,
    TEXT_TITLE,
    TEXT_HEADER,
    TEXT_BODY,
    TEXT_MUTED,
    TEXT_OLD_PAPER,
    WALL_FILL,
    WALL_BORDER,
    WALL_INNER,
    FOOD_PELLET,
    GOAL_POINT,
    GOAL_BORDER,
    GHOST_COLORS,
    BTN_NORMAL,
    BTN_HOVER,
    BTN_ACTIVE,
)

MAP_METADATA = {
    "single_goal_small_open.txt": {
        "title": "Bản đồ nhỏ không gian mở (Small Open)",
        "tag": "ĐƠN MỤC TIÊU",
        "tag_color": (56, 189, 248),
        "desc": "Map ít vật cản, kiểm tra tính tối ưu của BFS, UCS, A* (cùng tìm ra 16 bước) so với DFS (24 bước) trên đường thẳng.",
    },
    "single_goal_dense_maze.txt": {
        "title": "Mê cung vật cản dày đặc (Dense Maze)",
        "tag": "ĐƠN MỤC TIÊU",
        "tag_color": (56, 189, 248),
        "desc": "Vật cản chằng chịt, kiểm tra khả năng luồn lách của A* heuristic Manhattan so với BFS qua nhiều ngã rẽ phức tạp.",
    },
    "cycles_and_loops.txt": {
        "title": "Mê cung nhiều chu trình (Cycles & Loops)",
        "tag": "CHU TRÌNH",
        "tag_color": (168, 85, 247),
        "desc": "Nhiều vòng lặp khép kín, kiểm tra cơ chế tập visited (Graph Search) tránh bị rơi vào vòng lặp vô hạn.",
    },
    "deep_dead_ends.txt": {
        "title": "Mê cung ngõ cụt sâu (Deep Dead-Ends)",
        "tag": "NGÕ CỤT",
        "tag_color": (234, 179, 8),
        "desc": "Chứa các ngõ cụt dài, kiểm tra DFS dễ bị dẫn dụ đi sâu lãng phí (81 nodes) trong khi A* (43 nodes) định hướng tốt nhờ heuristic.",
    },
    "multi_food_four_corners.txt": {
        "title": "Bài toán 4 góc kinh điển (Four Corners)",
        "tag": "MULTI-FOOD",
        "tag_color": (251, 191, 36),
        "desc": "4 viên thức ăn ở 4 góc đối xứng, Pacman ở tâm. Kiểm tra thuật toán Multi-Goal A* Heuristic MST gom thức ăn tối ưu (40 bước).",
    },
    "multi_food_and_final_goal.txt": {
        "title": "Ăn thức ăn rồi về Goal (Food + Goal)",
        "tag": "FOOD + GOAL",
        "tag_color": (52, 211, 153),
        "desc": "Gom sạch 6 viên thức ăn rải rác trong mê cung rồi chạy về đích Goal (G) ở góc thoát hiểm (A* tìm đúng 72 bước tối ưu).",
    },
    "multi_goal_sparse.txt": {
        "title": "Nhiều điểm Goal phân tán (Sparse Goals)",
        "tag": "MULTI-GOAL",
        "tag_color": (52, 211, 153),
        "desc": "Có 5 điểm Goal G phân tán trên bản đồ, kiểm tra thuật toán MultiGoal duyệt qua tất cả các điểm chốt.",
    },
    "multi_goal_test.txt": {
        "title": "Kiểm thử 4 Goal tiêu chuẩn",
        "tag": "MULTI-GOAL",
        "tag_color": (52, 211, 153),
        "desc": "Map tiêu chuẩn kiểm thử bài toán nhiều mục tiêu của đồ án, 4 vị trí Goal (G).",
    },
    "map_test.txt": {
        "title": "Bản đồ lớn 43 thức ăn (43 Foods)",
        "tag": "MULTI-FOOD",
        "tag_color": (251, 191, 36),
        "desc": "Map có 43 thức ăn rải khắp mê cung, kiểm tra thuật toán xấp xỉ Nearest-Neighbor tour không bị nghẽn.",
    },
    "adversarial_single_ghost_corridor.txt": {
        "title": "Hành lang 1 Ghost đối đầu",
        "tag": "ĐỐI KHÁNG 1 MA",
        "tag_color": (239, 68, 68),
        "desc": "Hành lang có các hốc né, kiểm tra Minimax/Alpha-Beta có biết rẽ vào hốc để tránh Ghost đối đầu rồi đi tiếp tới Goal.",
    },
    "adversarial_two_ghosts_pincer.txt": {
        "title": "Gọng kìm 2 Ghost (Pincer Trap)",
        "tag": "ĐỐI KHÁNG 2 MA",
        "tag_color": (239, 68, 68),
        "desc": "2 Ghost dồn từ 2 phía, kiểm tra Alpha-Beta cắt tỉa mạnh (68.2% ở depth 3) và tìm hướng thoát thân khả thi.",
    },
    "adversarial_dead_end_trap.txt": {
        "title": "Bẫy ngõ cụt khi có Ghost áp sát",
        "tag": "BẪY NGÕ CỤT",
        "tag_color": (244, 63, 94),
        "desc": "Pacman đứng ở ngã ba gần ngõ cụt, Ghost tiến tới từ hành lang chính. Kiểm tra hàm đánh giá né bẫy ngõ cụt.",
    },
    "adversarial_small.txt": {
        "title": "Bản đồ đối kháng nhỏ (Small Adv)",
        "tag": "ĐỐI KHÁNG 1 MA",
        "tag_color": (239, 68, 68),
        "desc": "Bản đồ đối kháng nhỏ chuẩn 11x21 gồm 1 Ghost, 2 Food và 1 Goal. Kiểm chứng Alpha-Beta thắng game.",
    },
    "terrain_cost_map.txt": {
        "title": "Bản đồ Chi phí không đồng nhất (Terrain Cost)",
        "tag": "CHI PHÍ KHÁC NHAU",
        "tag_color": (34, 197, 94),
        "desc": "Có Nước '~' (cost=2) và Bùn 'S' (cost=3). BFS chọn đường ngắn 14 bước nhưng tốn 36 chi phí; UCS & A* đi vòng 22 bước nhưng tối ưu chỉ 22 chi phí.",
    },
    "test_map.txt": {
        "title": "Bản đồ tiêu chuẩn 2 Ghost",
        "tag": "ĐỐI KHÁNG 2 MA",
        "tag_color": (239, 68, 68),
        "desc": "Map tiêu chuẩn của đề bài kích thước 9x15 có 2 Ghost và 1 Goal.",
    },
    "large_map.txt": {
        "title": "Bản đồ lớn 3 Ghost (Large 22x19)",
        "tag": "MAP LỚN 3 MA",
        "tag_color": (249, 115, 22),
        "desc": "Map lớn 22x19 với 3 Ghost, kiểm tra Alpha-Beta cắt tỉa 82.0% số trạng thái (từ 6684 xuống 1200 nodes).",
    },
    "map_2.txt": {
        "title": "Bản đồ lớn mở rộng (Map 2)",
        "tag": "MAP LỚN",
        "tag_color": (249, 115, 22),
        "desc": "Map 22x19 tương đương large_map dùng cho kiểm tra độ ổn định.",
    },
    "dead_end_maze.txt": {
        "title": "Mê cung ngõ cụt và chu trình",
        "tag": "NGÕ CỤT",
        "tag_color": (234, 179, 8),
        "desc": "Map có ngõ cụt và vòng lặp, kiểm tra khả năng thoát bẫy.",
    },
    "unsolvable_walled_goal.txt": {
        "title": "Vô nghiệm: Goal bị tường bao kín",
        "tag": "VÔ NGHIỆM",
        "tag_color": (148, 163, 184),
        "desc": "Goal bị tường bịt kín 4 phía, kiểm tra thuật toán trả về None an toàn (không tìm thấy đường, không crash).",
    },
    "unsolvable_walled_pacman.txt": {
        "title": "Vô nghiệm: Pacman bị nhốt",
        "tag": "VÔ NGHIỆM",
        "tag_color": (148, 163, 184),
        "desc": "Pacman bị nhốt trong phòng kín, kiểm tra phát hiện không có lời giải ngay lập tức sau 1 node.",
    },
    "no_solution_map.txt": {
        "title": "Bản đồ không có đường tới đích",
        "tag": "VÔ NGHIỆM",
        "tag_color": (148, 163, 184),
        "desc": "Tường ngăn cách giữa Pacman và Goal, kiểm tra tính năng xử lý vô nghiệm.",
    },
}

class MapBrowserModal:
    """Cửa sổ Modal tương tác duyệt và xem trước toàn cảnh bản đồ (Overview & Mini-Map Preview)"""

    def __init__(self, screen_w, screen_h=None, map_files=None, current_map=None, on_select=None, on_select_callback=None):
        if isinstance(screen_w, (tuple, list)):
            w, h = screen_w
            maps = screen_h
            cur = map_files
            cb = on_select or on_select_callback
        else:
            w, h = screen_w, screen_h
            maps = map_files
            cur = current_map
            cb = on_select or on_select_callback

        self.screen_w = w
        self.screen_h = h
        self.map_files = [m for m in (maps or []) if "bad_map" not in m]
        self.on_select = cb

        modal_w = 1040
        modal_h = 630
        self.rect = pygame.Rect(
            (self.screen_w - modal_w) // 2,
            (self.screen_h - modal_h) // 2,
            modal_w,
            modal_h
        )

        self.selected_map = cur if cur in self.map_files else (self.map_files[0] if self.map_files else None)
        self.cached_map_data = {}
        self.scroll_y = 0
        self.item_height = 46

        self.close_btn_rect = pygame.Rect(self.rect.right - 42, self.rect.y + 14, 28, 28)

        self.confirm_btn_rect = pygame.Rect(self.rect.right - 260, self.rect.bottom - 48, 236, 36)

        if self.selected_map:
            self._load_map_details(self.selected_map)

    def _load_map_details(self, map_path):
        """Nạp dữ liệu bản đồ để render preview và trích xuất thông số"""
        if map_path in self.cached_map_data:
            return self.cached_map_data[map_path]

        gmap = load_map(map_path)
        if not gmap:
            data = None
        else:
            spawn, goals, ghosts, foods = get_map_info(gmap, return_foods=True)
            filename = map_path.split("/")[-1].split("\\")[-1]
            meta = MAP_METADATA.get(filename, {
                "title": filename,
                "tag": "BẢN ĐỒ TÙY CHỌN",
                "tag_color": (56, 189, 248),
                "desc": f"Bản đồ lưới kích thước {len(gmap)}x{len(gmap[0])}."
            })
            data = {
                "game_map": gmap,
                "rows": len(gmap),
                "cols": len(gmap[0]) if len(gmap) > 0 else 0,
                "spawn": spawn,
                "goals": goals,
                "ghosts": ghosts,
                "foods": foods,
                "filename": filename,
                "meta": meta,
            }

        self.cached_map_data[map_path] = data
        return data

    def handle_event(self, event):
        """Xử lý sự kiện bàn phím và chuột trong modal"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "CLOSE"
            elif event.key == pygame.K_RETURN:
                if self.selected_map:
                    if self.on_select:
                        self.on_select(self.selected_map)
                    return "SELECT"

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if self.close_btn_rect.collidepoint(mx, my):
                return "CLOSE"

            if not self.rect.collidepoint(mx, my):
                return "CLOSE"

            if self.confirm_btn_rect.collidepoint(mx, my):
                if self.selected_map:
                    if self.on_select:
                        self.on_select(self.selected_map)
                    return "SELECT"

            list_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 60, 420, self.rect.height - 80)
            if list_rect.collidepoint(mx, my):
                if event.button == 4:
                    self.scroll_y = max(0, self.scroll_y - 28)
                    return True
                elif event.button == 5:
                    max_scroll = max(0, len(self.map_files) * self.item_height - (list_rect.height - 20))
                    self.scroll_y = min(max_scroll, self.scroll_y + 28)
                    return True

                rel_y = my - (self.rect.y + 68) + self.scroll_y
                if rel_y >= 0:
                    clicked_idx = rel_y // self.item_height
                    if 0 <= clicked_idx < len(self.map_files):
                        self.selected_map = self.map_files[clicked_idx]
                        self._load_map_details(self.selected_map)
                        return True

        return True

    def draw(self, surface):
        """Vẽ toàn bộ Modal: Nền làm mờ, Danh sách bên trái, Mini-Map Preview bên phải"""
        dim_surf = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        dim_surf.fill((8, 10, 18, 210))
        surface.blit(dim_surf, (0, 0))

        draw_arcade_panel(surface, self.rect, bg_color=(15, 20, 32), corner_radius=8)

        pygame.draw.rect(surface, (56, 189, 248), self.rect, width=2, border_radius=8)

        font_title = get_font("header")
        hdr_txt = font_title.render("🗺 BỘ DUYỆT & XEM TRƯỚC BẢN ĐỒ (MAP BROWSER & OVERVIEW)", True, (251, 191, 36))
        surface.blit(hdr_txt, (self.rect.x + 24, self.rect.y + 18))

        pygame.draw.rect(surface, (35, 41, 66), self.close_btn_rect, border_radius=4)
        pygame.draw.rect(surface, BORDER_COLOR, self.close_btn_rect, width=1, border_radius=4)
        font_btn = get_font("badge")
        x_surf = font_btn.render("X", True, (244, 63, 94))
        surface.blit(x_surf, x_surf.get_rect(center=self.close_btn_rect.center))

        self._draw_map_list(surface)
        self._draw_preview_panel(surface)

    def _draw_map_list(self, surface):
        """Vẽ danh sách các file bản đồ có thanh cuộn và nhãn phân loại"""
        list_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 58, 420, self.rect.height - 78)
        pygame.draw.rect(surface, (12, 15, 25), list_rect, border_radius=6)
        pygame.draw.rect(surface, BORDER_COLOR, list_rect, width=1, border_radius=6)

        prev_clip = surface.get_clip()
        surface.set_clip(list_rect.inflate(-4, -4))

        start_y = self.rect.y + 64 - self.scroll_y
        font_name = get_font("body")
        font_tag = get_font("small")

        for idx, mpath in enumerate(self.map_files):
            item_y = start_y + idx * self.item_height
            if item_y + self.item_height < list_rect.y or item_y > list_rect.bottom:
                continue

            item_rect = pygame.Rect(list_rect.x + 6, item_y, list_rect.width - 12, self.item_height - 4)
            is_selected = (mpath == self.selected_map)

            if is_selected:
                pygame.draw.rect(surface, (30, 41, 69), item_rect, border_radius=4)
                pygame.draw.rect(surface, (56, 189, 248), item_rect, width=2, border_radius=4)
            else:
                pygame.draw.rect(surface, (18, 23, 38), item_rect, border_radius=4)
                pygame.draw.rect(surface, (30, 36, 56), item_rect, width=1, border_radius=4)

            fname = mpath.split("/")[-1].split("\\")[-1]
            meta = MAP_METADATA.get(fname, {"title": fname, "tag": "MAP", "tag_color": (148, 163, 184)})

            name_color = (255, 214, 10) if is_selected else (241, 245, 249)
            name_surf = font_name.render(fname, True, name_color)
            surface.blit(name_surf, (item_rect.x + 10, item_rect.y + 6))

            tag_text = meta.get("tag", "MAP")
            tag_color = meta.get("tag_color", (56, 189, 248))
            tag_surf = font_tag.render(tag_text, True, tag_color)
            surface.blit(tag_surf, (item_rect.x + 10, item_rect.y + 24))

        surface.set_clip(prev_clip)

    def _draw_preview_panel(self, surface):
        """Vẽ Vùng xem trước Mini-Map Canvas và Thông số chi tiết"""
        preview_x = self.rect.x + 456
        preview_w = self.rect.width - 476
        prev_rect = pygame.Rect(preview_x, self.rect.y + 58, preview_w, self.rect.height - 78)

        pygame.draw.rect(surface, (12, 15, 25), prev_rect, border_radius=6)
        pygame.draw.rect(surface, BORDER_COLOR, prev_rect, width=1, border_radius=6)

        data = self._load_map_details(self.selected_map) if self.selected_map else None
        if not data or not data["game_map"]:
            font_sm = get_font("header")
            msg = font_sm.render("[ KHÔNG THỂ XEM TRƯỚC BẢN ĐỒ NÀY ]", True, (244, 63, 94))
            surface.blit(msg, msg.get_rect(center=prev_rect.center))
            return

        gmap = data["game_map"]
        rows = data["rows"]
        cols = data["cols"]
        meta = data["meta"]

        font_t = get_font("header")
        t_surf = font_t.render(meta.get("title", data["filename"]), True, (254, 240, 138))
        surface.blit(t_surf, (preview_x + 14, self.rect.y + 70))

        font_b = get_font("body")
        desc_lines = self._wrap_text(meta.get("desc", ""), font_b, preview_w - 28)
        cur_dy = self.rect.y + 96
        for line in desc_lines:
            d_surf = font_b.render(line, True, (203, 213, 225))
            surface.blit(d_surf, (preview_x + 14, cur_dy))
            cur_dy += 18

        canvas_y = cur_dy + 8
        canvas_h = self.rect.bottom - canvas_y - 64
        canvas_w = preview_w - 28
        canvas_rect = pygame.Rect(preview_x + 14, canvas_y, canvas_w, canvas_h)

        pygame.draw.rect(surface, (8, 10, 18), canvas_rect, border_radius=4)
        pygame.draw.rect(surface, (35, 41, 66), canvas_rect, width=1, border_radius=4)

        tile_w = (canvas_w - 16) // max(1, cols)
        tile_h = (canvas_h - 16) // max(1, rows)
        tile_size = max(4, min(24, min(tile_w, tile_h)))

        maze_px_w = cols * tile_size
        maze_px_h = rows * tile_size
        offset_x = canvas_rect.x + (canvas_w - maze_px_w) // 2
        offset_y = canvas_rect.y + (canvas_h - maze_px_h) // 2

        for r in range(rows):
            for c in range(cols):
                char = gmap[r][c]
                rx = offset_x + c * tile_size
                ry = offset_y + r * tile_size
                t_rect = pygame.Rect(rx, ry, tile_size, tile_size)

                if char == "#":
                    pygame.draw.rect(surface, WALL_FILL, t_rect)
                    pygame.draw.rect(surface, WALL_BORDER, t_rect, width=1)
                elif char == "~":
                    pygame.draw.rect(surface, (20, 52, 92), t_rect)
                    pygame.draw.rect(surface, (38, 88, 145), t_rect, width=1)
                elif char == "S":
                    pygame.draw.rect(surface, (62, 42, 22), t_rect)
                    pygame.draw.rect(surface, (105, 75, 42), t_rect, width=1)
                else:
                    pygame.draw.rect(surface, (14, 17, 28), t_rect)

                    if char == ".":
                        cx = rx + tile_size // 2
                        cy = ry + tile_size // 2
                        pygame.draw.circle(surface, FOOD_PELLET, (cx, cy), max(1, tile_size // 4))

                    elif char == "G":
                        cx = rx + tile_size // 2
                        cy = ry + tile_size // 2
                        rad = max(2, tile_size // 3)
                        pts = [(cx, cy - rad), (cx + rad, cy), (cx, cy + rad), (cx - rad, cy)]
                        pygame.draw.polygon(surface, GOAL_POINT, pts)

                    elif char == "@":
                        cx = rx + tile_size // 2
                        cy = ry + tile_size // 2
                        pygame.draw.circle(surface, (239, 68, 68), (cx, cy), max(2, int(tile_size * 0.38)))

                    elif char == "P":
                        cx = rx + tile_size // 2
                        cy = ry + tile_size // 2
                        pygame.draw.circle(surface, COLOR_PACMAN, (cx, cy), max(3, int(tile_size * 0.42)))

        info_y = self.rect.bottom - 48
        font_info = get_font("body")
        specs_str = f"Lưới: {rows}x{cols}  |  P: {data['spawn']}  |  Food: {len(data['foods'])}  |  Goal: {len(data['goals'])}  |  Ghost: {len(data['ghosts'])}"
        specs_surf = font_info.render(specs_str, True, (148, 163, 184))
        surface.blit(specs_surf, (preview_x + 14, info_y + 8))

        pygame.draw.rect(surface, (16, 185, 129), self.confirm_btn_rect, border_radius=4)
        pygame.draw.rect(surface, (110, 231, 183), self.confirm_btn_rect, width=1, border_radius=4)
        font_btn = get_font("badge")
        btn_txt = font_btn.render("CHỌN VÀO GAME", True, (15, 23, 42))
        surface.blit(btn_txt, btn_txt.get_rect(center=self.confirm_btn_rect.center))

    def _wrap_text(self, text, font, max_width):
        """Hàm bẻ dòng văn bản mô tả theo chiều rộng"""
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)
        return lines
