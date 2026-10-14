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
    "single_small_few_solvable.txt": {
        "title": "Bản đồ nhỏ, ít vật cản (9x15)",
        "tag": "ĐƠN MỤC TIÊU - MỞ",
        "tag_color": (56, 189, 248),
        "desc": "Map nhỏ 9x15 không gian thoáng, 1 Goal; làm cơ sở đối sánh tính tối ưu và số node mở rộng của BFS, DFS, UCS và A*.",
    },
    "test_map.txt": {
        "title": "Mê cung tiêu chuẩn 2 Ghost (9x15)",
        "tag": "ĐỐI KHÁNG 2 MA",
        "tag_color": (239, 68, 68),
        "desc": "Bản đồ nhỏ 9x15 nhiều vật cản (mê cung tiêu chuẩn), gồm 2 Ghost và 1 Goal; kiểm thử tìm đường và đối kháng cơ bản.",
    },
    "single_large_many_solvable.txt": {
        "title": "Mê cung lớn dày đặc vật cản (31x41)",
        "tag": "MAP LỚN - MÊ CUNG",
        "tag_color": (14, 165, 233),
        "desc": "Bản đồ lớn 31x41 nhiều tường chắn và nhánh rẽ phức tạp, 1 Goal; đo hiệu năng của A* heuristic Manhattan so với BFS/DFS.",
    },
    "large_map.txt": {
        "title": "Bản đồ Pacman lớn 3 Ghost (22x19)",
        "tag": "MAP LỚN 3 MA",
        "tag_color": (249, 115, 22),
        "desc": "Bản đồ lớn 22x19 với buồng giam 3 Ghost ở trung tâm; đo mức bùng nổ node và hiệu quả cắt tỉa của Alpha-Beta (giảm 82% trạng thái) so với Minimax.",
    },
    "multi_goal_test.txt": {
        "title": "Bản đồ nhỏ nhiều mục tiêu (9x15)",
        "tag": "MULTI-GOAL (NHỎ)",
        "tag_color": (52, 211, 153),
        "desc": "Bản đồ 9x15 có 4 vị trí Goal (G) ở các góc khác nhau; kiểm thử bài toán gom hết mục tiêu (Multi-Goal Search).",
    },
    "multi_large_many_solvable.txt": {
        "title": "Mê cung lớn nhiều mục tiêu (31x41)",
        "tag": "MULTI-GOAL (LỚN)",
        "tag_color": (16, 185, 129),
        "desc": "Bản đồ lớn 31x41 nhiều vật cản gồm 5 điểm thức ăn (.) và 1 đích thoát hiểm (G); kiểm tra giới hạn chịu tải của A* đa mục tiêu.",
    },
    "cost_small_single.txt": {
        "title": "Chi phí không đồng nhất - Nhỏ (9x19)",
        "tag": "CHI PHÍ BÙN LẦY",
        "tag_color": (168, 85, 247),
        "desc": "Map 9x19 có vùng bùn lầy (MUD = 6) chặn khe hở giữa; kiểm tra UCS/A* tự động đi vòng khe trên (28 bước, cost 28) thay vì đi thẳng qua bùn (16 bước, cost 41).",
    },
    "cost_large_single.txt": {
        "title": "Chi phí không đồng nhất - Lớn (25x41)",
        "tag": "CHI PHÍ BÙN LẦY",
        "tag_color": (139, 92, 246),
        "desc": "Map lớn 25x41 có bãi bùn lầy (MUD = 6) ở trung tâm; đối sánh giữa đường đi thẳng ít bước (38 bước, cost 93) và đường vòng tối ưu chi phí (58 bước, cost 58).",
    },
    "adversarial_small.txt": {
        "title": "Hành lang hẹp 1 Ghost bám đuổi (11x21)",
        "tag": "ĐỐI KHÁNG 1 MA",
        "tag_color": (239, 68, 68),
        "desc": "Bản đồ 11x21 có hành lang hẹp dài, 1 Ghost bám sát sau lưng, 2 Food và 1 Goal; kiểm tra khả năng né tránh của Minimax và Alpha-Beta.",
    },
    "dead_end_maze.txt": {
        "title": "Mê cung nhiều ngõ cụt (11x17)",
        "tag": "NGÕ CỤT",
        "tag_color": (234, 179, 8),
        "desc": "Bản đồ 11x17 có nhiều ngõ cụt sâu và vòng lặp kèm 1 Ghost; kiểm tra hàm đánh giá (evaluation function) tránh bị dồn vào đường cụt.",
    },
    "no_solution_map.txt": {
        "title": "Vô nghiệm - Bản đồ nhỏ (9x9)",
        "tag": "VÔ NGHIỆM (NHỎ)",
        "tag_color": (148, 163, 184),
        "desc": "Bản đồ nhỏ 9x9 có đường tới Goal bị tường bịt kín hoàn toàn; kiểm tra thuật toán dừng đúng và trả về None an toàn.",
    },
    "single_large_many_unsolvable.txt": {
        "title": "Vô nghiệm - Mê cung lớn (31x41)",
        "tag": "VÔ NGHIỆM (LỚN)",
        "tag_color": (100, 116, 139),
        "desc": "Mê cung lớn 31x41 nhiều vật cản có Goal bị tường bao kín bốn phía; kiểm tra tốc độ vét cạn không gian trạng thái lớn khi không có lời giải.",
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
        btn_txt = font_btn.render("▶ CHỌN VÀO GAME", True, (15, 23, 42))
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
