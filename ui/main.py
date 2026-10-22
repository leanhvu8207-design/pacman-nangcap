"""
Giao diện đồ họa Vintage Arcade cho dự án Pacman AI Search - Nhóm 07
Hỗ trợ chuyển đổi mượt mà giữa Chế độ Máy chơi (AI) và Chế độ Người chơi (WASD / Phím mũi tên / Nút D-Pad)
"""

import sys
import os
import math
import asyncio
import pygame

# Đảm bảo đường dẫn import hoạt động tốt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui.theme import (
    init_fonts,
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
    STATUS_COLORS,
    BTN_ACTIVE,
    BTN_TEXT_ACTIVE,
    BTN_NORMAL,
    BTN_HOVER,
)
from ui.components import (
    Button,
    ButtonGroup,
    NumberStepper,
    MapSelector,
    ScrollableLogBox,
    DirectionalPad,
)
from ui.map_browser import MapBrowserModal
from ui.renderer import MazeRenderer
from ui.controller import GameController


class PacmanVintageUI:
    """Ứng dụng giao diện Retro Arcade hoàn chỉnh hỗ trợ cả AI và Người chơi"""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("PACMAN AI SEARCH - NHOM 07 [VINTAGE ARCADE]")

        self.width = 1260
        self.height = 780
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.is_running = True

        init_fonts()

        # Khởi tạo log box trước để nhận log từ controller
        self.log_box = ScrollableLogBox(pygame.Rect(812, 564, 420, 194))

        # Khởi tạo Game Controller
        self.controller = GameController(log_callback=self.on_log_received)

        # Khởi tạo Renderer cho vùng Mê cung
        self.maze_viewport = pygame.Rect(16, 74, 768, 690)
        self.maze_renderer = MazeRenderer(self.maze_viewport)
        self.maze_renderer.compute_layout(self.controller.game_map)

        # Tọa độ nội suy mượt 60 FPS cho Pacman và Ghost
        self.visual_pacman_pos = list(self.controller.pacman_pos) if self.controller.pacman_pos else None
        self.visual_ghost_positions = [list(gp) for gp in self.controller.ghost_positions]

        # Khởi tạo Modal duyệt và xem trước toàn cảnh bản đồ
        self.map_browser = MapBrowserModal(
            (self.width, self.height),
            self.controller.map_files,
            self.controller.current_map_file,
            on_select=self.on_map_browser_select
        )
        self.show_map_browser = False

        # Khởi tạo các thành phần giao diện tương tác
        self._init_ui_components()

    def on_log_received(self, text, color):
        self.log_box.add_log(text, color)

    def _init_ui_components(self):
        # 1. Map Selector
        self.map_selector = MapSelector(
            pygame.Rect(812, 100, 420, 26),
            self.controller.map_files,
            initial_idx=self.controller.map_files.index(self.controller.current_map_file) if self.controller.current_map_file in self.controller.map_files else 0,
            on_change=self.on_map_changed,
            on_open_browser=self.open_map_browser
        )

        # 2. Ô chọn Chế độ chơi: MÁY CHƠI (AI) vs NGƯỜI CHƠI (WASD / Mũi tên)
        self.mode_group = ButtonGroup(
            [pygame.Rect(812, 132, 206, 26), pygame.Rect(1026, 132, 206, 26)],
            ["MÁY CHƠI (AI)", "NGƯỜI CHƠI (WASD)"],
            ["AI", "PLAYER"],
            initial_val=self.controller.play_mode,
            on_change=self.on_play_mode_changed,
            font_key="subtitle"
        )

        # 3. Cụm điều khiển D-Pad dành riêng cho chế độ Người chơi
        self.dpad = DirectionalPad(
            pygame.Rect(812, 164, 420, 81),
            on_direction=self.controller.trigger_player_direction
        )

        # 4. Algorithm Tabs (Hiển thị khi ở chế độ MÁY CHƠI - AI)
        # Hàng 1: Thuật toán cổ điển 5 nút
        classic_algos = ["DFS", "BFS", "UCS", "GREEDY", "A*"]
        btn_w_classic = 78
        rects_classic = [
            pygame.Rect(812 + i * (btn_w_classic + 7), 164, btn_w_classic, 24)
            for i in range(len(classic_algos))
        ]
        self.classic_group = ButtonGroup(
            rects_classic,
            classic_algos,
            classic_algos,
            initial_val="A*",
            on_change=self.on_algorithm_changed,
            font_key="subtitle",
            allow_none=True
        )

        # Hàng 2: Thuật toán đối kháng 3 nút (Minimax, Alpha-Beta, Expectimax)
        adv_algos = ["MINIMAX", "ALPHA-BETA", "EXPECTIMAX"]
        btn_w_adv = 135
        rects_adv = [
            pygame.Rect(812 + i * (btn_w_adv + 7), 192, btn_w_adv if i < 2 else 136, 24)
            for i in range(len(adv_algos))
        ]
        self.adv_group = ButtonGroup(
            rects_adv,
            ["MINIMAX", "ALPHA-BETA", "EXPECTIMAX (MỚI)"],
            adv_algos,
            initial_val=None,
            on_change=self.on_algorithm_changed,
            font_key="subtitle",
            allow_none=True
        )

        # Đồng bộ đảm bảo chỉ duy nhất thuật toán A* sáng, Minimax/Alpha-Beta tắt hoàn toàn
        self.on_algorithm_changed(self.controller.algorithm)

        # 5. Contextual Controls (Depth & Adversarial Mode)
        self.depth_stepper = NumberStepper(
            pygame.Rect(812, 220, 190, 25),
            label="Depth",
            min_val=1,
            max_val=6,
            initial_val=self.controller.depth,
            on_change=self.on_depth_changed
        )

        self.adv_mode_group = ButtonGroup(
            [pygame.Rect(1010, 220, 110, 25), pygame.Rect(1126, 220, 106, 25)],
            ["Mô phỏng", "1 Bước"],
            ["MATCH", "STEP"],
            initial_val=self.controller.adv_mode,
            on_change=self.on_adv_mode_changed,
            font_key="subtitle"
        )

        # 6. Action Buttons (Start, Pause, Step, Reset)
        act_y = 252
        act_w = 100
        act_gap = 7
        self.btn_start = Button(
            pygame.Rect(812 + 0 * (act_w + act_gap), act_y, act_w, 30),
            "▶ START",
            on_click=self.controller.start,
            variant="start",
            font_key="header"
        )
        self.btn_pause = Button(
            pygame.Rect(812 + 1 * (act_w + act_gap), act_y, act_w, 30),
            "⏸ PAUSE",
            on_click=self.toggle_pause,
            variant="pause",
            font_key="header"
        )
        self.btn_step = Button(
            pygame.Rect(812 + 2 * (act_w + act_gap), act_y, act_w, 30),
            "⏭ STEP",
            on_click=self.controller.step_forward,
            variant="default",
            font_key="header"
        )
        self.btn_reset = Button(
            pygame.Rect(812 + 3 * (act_w + act_gap), act_y, act_w, 30),
            "↺ RESET",
            on_click=self.on_reset_clicked,
            variant="stop",
            font_key="header"
        )

        # 7. Speed Buttons (0.5x, 1x, 2x, 4x, Max)
        speeds = [0.5, 1.0, 2.0, 4.0, 10.0]
        speed_labels = ["0.5x", "1.0x", "2.0x", "4.0x", "Max"]
        sp_w = 66
        sp_rects = [
            pygame.Rect(878 + i * (sp_w + 5), 290, sp_w, 22)
            for i in range(len(speeds))
        ]
        self.speed_group = ButtonGroup(
            sp_rects,
            speed_labels,
            speeds,
            initial_val=1.0,
            on_change=self.controller.set_speed,
            font_key="small"
        )

    def _snap_visual_positions(self):
        """Đồng bộ tức thì tọa độ hiển thị với tọa độ lưới khi đổi map hoặc Reset"""
        self.visual_pacman_pos = list(self.controller.pacman_pos) if self.controller.pacman_pos else None
        self.visual_ghost_positions = [list(gp) for gp in self.controller.ghost_positions]

    def _update_smooth_positions(self):
        """Nội suy mượt tọa độ Pacman và Ghost ở tần số 60 FPS"""
        lerp_speed = min(0.65, 0.28 * max(0.5, min(3.5, self.controller.speed)))

        # 1. Nội suy vị trí Pacman
        target_pm = self.controller.pacman_pos
        if target_pm is None:
            self.visual_pacman_pos = None
        elif self.visual_pacman_pos is None:
            self.visual_pacman_pos = [float(target_pm[0]), float(target_pm[1])]
        else:
            dr = target_pm[0] - self.visual_pacman_pos[0]
            dc = target_pm[1] - self.visual_pacman_pos[1]
            dist = math.hypot(dr, dc)
            if dist > 1.6 or dist < 0.01:
                self.visual_pacman_pos[0] = float(target_pm[0])
                self.visual_pacman_pos[1] = float(target_pm[1])
            else:
                self.visual_pacman_pos[0] += dr * lerp_speed
                self.visual_pacman_pos[1] += dc * lerp_speed

        # 2. Nội suy vị trí các Ghost
        target_ghosts = self.controller.ghost_positions
        if len(self.visual_ghost_positions) != len(target_ghosts):
            self.visual_ghost_positions = [[float(gp[0]), float(gp[1])] for gp in target_ghosts]
        else:
            for i, gp in enumerate(target_ghosts):
                dr = gp[0] - self.visual_ghost_positions[i][0]
                dc = gp[1] - self.visual_ghost_positions[i][1]
                dist = math.hypot(dr, dc)
                if dist > 1.6 or dist < 0.01:
                    self.visual_ghost_positions[i][0] = float(gp[0])
                    self.visual_ghost_positions[i][1] = float(gp[1])
                else:
                    self.visual_ghost_positions[i][0] += dr * lerp_speed
                    self.visual_ghost_positions[i][1] += dc * lerp_speed

    def on_reset_clicked(self):
        self.controller.reset_state()
        self._snap_visual_positions()

    def toggle_pause(self):
        if self.controller.status == "RUNNING":
            self.controller.pause()
        elif self.controller.status == "PAUSED":
            self.controller.resume()

    def open_map_browser(self):
        """Mở modal xem trước và duyệt bản đồ toàn cảnh"""
        self.show_map_browser = True
        if self.controller.current_map_file:
            self.map_browser.selected_map = self.controller.current_map_file
            self.map_browser._load_map_details(self.controller.current_map_file)

    def close_map_browser(self):
        """Đóng modal xem trước bản đồ"""
        self.show_map_browser = False

    def on_map_browser_select(self, new_map_path):
        """Khi người dùng xác nhận chọn bản đồ trong modal"""
        self.map_selector.set_map(new_map_path)
        self.on_map_changed(new_map_path)
        self.show_map_browser = False

    def on_map_changed(self, new_map_path):
        self.controller.set_map_file(new_map_path)
        self.maze_renderer.compute_layout(self.controller.game_map)
        self._snap_visual_positions()
        if hasattr(self, "map_browser"):
            self.map_browser.selected_map = new_map_path

    def on_play_mode_changed(self, new_mode):
        """Khi người dùng chuyển đổi giữa Chế độ Máy chơi (AI) và Người chơi (PLAYER)"""
        self.controller.set_play_mode(new_mode)
        self.mode_group.selected_value = new_mode
        self.mode_group._update_states()
        self._snap_visual_positions()

    def on_algorithm_changed(self, algo_name):
        self.controller.set_algorithm(algo_name)
        if algo_name in ["DFS", "BFS", "UCS", "GREEDY", "A*"]:
            self.classic_group.selected_value = algo_name
            self.classic_group._update_states()
            self.adv_group.selected_value = None
            self.adv_group._update_states()
        else:
            self.adv_group.selected_value = algo_name
            self.adv_group._update_states()
            self.classic_group.selected_value = None
            self.classic_group._update_states()

    def on_depth_changed(self, new_depth):
        self.controller.set_depth(new_depth)

    def on_adv_mode_changed(self, new_mode):
        self.controller.set_adv_mode(new_mode)

    # ==========================================================================
    # VÒNG LẶP XỬ LÝ SỰ KIỆN CHUỘT VÀ PHÍM
    # ==========================================================================
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                self.controller.stop_execution()
                return

            # Nếu Modal Map Browser đang mở, chuyển tiếp sự kiện và chặn tương tác phía dưới
            if self.show_map_browser:
                res = self.map_browser.handle_event(event)
                if res in ["CLOSE", "SELECT"]:
                    self.close_map_browser()
                continue

            # Sự kiện nhả phím (cập nhật bộ đệm điều khiển Người chơi)
            if event.type == pygame.KEYUP:
                self.controller.handle_player_key_up(event.key)

            # Phím tắt bàn phím & Điều khiển Pacman
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                    self.controller.stop_execution()
                    return
                elif event.key == pygame.K_TAB:
                    next_mode = "PLAYER" if self.controller.play_mode == "AI" else "AI"
                    self.on_play_mode_changed(next_mode)
                    continue
                elif event.key == pygame.K_m:
                    self.open_map_browser()
                    continue
                elif event.key == pygame.K_SPACE:
                    self.toggle_pause()
                    continue
                elif event.key == pygame.K_r:
                    self.on_reset_clicked()
                    continue
                elif event.key == pygame.K_RETURN:
                    self.controller.start()
                    continue

                # Nếu đang ở chế độ NGƯỜI CHƠI: ưu tiên xử lý WASD và các phím mũi tên ↑ ↓ ← →
                if self.controller.play_mode == "PLAYER":
                    if self.controller.handle_player_key_down(event.key):
                        continue
                else:
                    # Ở chế độ AI: phím S dùng để đi từng bước (Step)
                    if event.key == pygame.K_s:
                        self.controller.step_forward()
                        continue

            # Tương tác chuột với các thành phần giao diện
            self.map_selector.handle_event(event)
            self.mode_group.handle_event(event)

            if self.controller.play_mode == "PLAYER":
                self.dpad.handle_event(event)
            else:
                self.classic_group.handle_event(event)
                self.adv_group.handle_event(event)
                if self.controller.algorithm in ["MINIMAX", "ALPHA-BETA", "EXPECTIMAX"]:
                    self.depth_stepper.handle_event(event)
                    self.adv_mode_group.handle_event(event)

            self.btn_start.handle_event(event)
            self.btn_pause.handle_event(event)
            self.btn_step.handle_event(event)
            self.btn_reset.handle_event(event)
            self.speed_group.handle_event(event)
            self.log_box.handle_event(event)

    # ==========================================================================
    # VẼ TOÀN BỘ GIAO DIỆN
    # ==========================================================================
    def render(self):
        # Cập nhật vòng lặp di chuyển của Người chơi (nếu đang ở chế độ PLAYER) hoặc AI Web (Pygbag)
        if self.controller.play_mode == "PLAYER":
            held_mouse_dir = self.dpad.get_held_mouse_action()
            self.controller.update_player_loop(held_mouse_action=held_mouse_dir)
            self.dpad.sync_active_directions(self.controller.input_buffer.get_active_directions())
        else:
            self.controller.update_web_ai()

        # Nội suy mượt vị trí hiển thị 60 FPS
        self._update_smooth_positions()

        # 1. Nền tổng thể
        self.screen.fill(BG_MAIN)

        # 2. Header
        self._draw_header()

        # 3. Khu vực mê cung
        self.maze_renderer.update_animation()
        self.maze_renderer.draw_maze(
            self.screen,
            self.controller.game_map,
            remaining_food=self.controller.remaining_foods,
            goals=self.controller.remaining_goals,
            path_trail=self.controller.path_trail,
            is_win=(self.controller.status == "WIN")
        )

        # Vẽ Pacman với tọa độ nội suy mượt
        pm_draw_pos = self.visual_pacman_pos if self.visual_pacman_pos is not None else self.controller.pacman_pos
        if pm_draw_pos:
            self.maze_renderer.draw_pacman(
                self.screen,
                pm_draw_pos[0],
                pm_draw_pos[1],
                direction=self.controller.facing_dir
            )

        # Vẽ các Ghost với tọa độ nội suy mượt và hướng mắt thực tế
        ghost_draw_list = self.visual_ghost_positions if len(self.visual_ghost_positions) == len(self.controller.ghost_positions) else self.controller.ghost_positions
        for g_idx, g_pos in enumerate(ghost_draw_list):
            g_dir = self.controller.ghost_facing_dirs[g_idx] if g_idx < len(self.controller.ghost_facing_dirs) else "DOWN"
            self.maze_renderer.draw_ghost(
                self.screen,
                g_idx,
                g_pos[0],
                g_pos[1],
                facing_dir=g_dir
            )

        # 4. Khu vực Sidebar bên phải
        self._draw_control_panel()
        self._draw_metrics_panel()
        self._draw_activity_log_panel()

        # 5. Modal Bộ duyệt và xem trước toàn cảnh bản đồ (nếu đang mở)
        if self.show_map_browser:
            self.map_browser.draw(self.screen)

        pygame.display.flip()

    def _draw_header(self):
        """Vẽ thanh tiêu đề Header phong cách bảng điều khiển Arcade cổ điển"""
        header_rect = pygame.Rect(16, 12, self.width - 32, 50)
        draw_arcade_panel(self.screen, header_rect, bg_color=BG_PANEL, corner_radius=6)

        # Tên game: PACMAN AI SEARCH
        font_title = get_font("title")
        title_surf = font_title.render("PACMAN AI SEARCH", True, TEXT_TITLE)
        self.screen.blit(title_surf, (34, 22))

        # Nhãn đồ án: GROUP 07
        font_badge = get_font("badge")
        grp_badge_rect = pygame.Rect(310, 24, 92, 26)
        pygame.draw.rect(self.screen, (40, 48, 75), grp_badge_rect, border_radius=4)
        pygame.draw.rect(self.screen, (251, 191, 36), grp_badge_rect, width=1, border_radius=4)
        grp_surf = font_badge.render("GROUP 07", True, (251, 191, 36))
        self.screen.blit(grp_surf, grp_surf.get_rect(center=grp_badge_rect.center))

        # Nhãn chế độ hiện tại (AI MODE / PLAYER MODE)
        is_player = (self.controller.play_mode == "PLAYER")
        mode_text = "NGƯỜI CHƠI" if is_player else "MÁY CHƠI (AI)"
        mode_col = (52, 211, 153) if is_player else (56, 189, 248)
        mode_badge_rect = pygame.Rect(410, 24, 124, 26)
        pygame.draw.rect(self.screen, (25, 30, 48), mode_badge_rect, border_radius=4)
        pygame.draw.rect(self.screen, mode_col, mode_badge_rect, width=1, border_radius=4)
        mode_surf = font_badge.render(mode_text, True, mode_col)
        self.screen.blit(mode_surf, mode_surf.get_rect(center=mode_badge_rect.center))

        # Trạng thái game (Ready, Running, Win, Lose, Paused)
        st_text = self.controller.status
        st_color = STATUS_COLORS.get(st_text, STATUS_COLORS["READY"])
        st_badge_rect = pygame.Rect(542, 24, 106, 26)
        pygame.draw.rect(self.screen, (25, 30, 48), st_badge_rect, border_radius=4)
        pygame.draw.rect(self.screen, st_color, st_badge_rect, width=2, border_radius=4)
        st_surf = font_badge.render(f"● {st_text}", True, st_color)
        self.screen.blit(st_surf, st_surf.get_rect(center=st_badge_rect.center))

        # Phím tắt gợi ý phía góc phải
        font_hint = get_font("small")
        if is_player:
            hint_str = "[WASD / ↑↓←→: Di chuyển  |  Tab: Đổi AI/Người  |  Space: Pause  |  R: Reset]"
        else:
            hint_str = "[Tab: Đổi AI/Người  |  M: Maps  |  Enter: Start  |  Space: Pause  |  R: Reset]"
        hint_surf = font_hint.render(hint_str, True, (130, 145, 175))
        self.screen.blit(hint_surf, (self.width - hint_surf.get_width() - 28, 29))

    def _draw_control_panel(self):
        """Vẽ Bảng điều khiển chế độ chơi, thuật toán, bản đồ và nút tác vụ"""
        panel_rect = pygame.Rect(800, 74, 444, 254)
        draw_arcade_panel(self.screen, panel_rect, bg_color=BG_PANEL, corner_radius=6)

        # Tiêu đề panel
        font_hdr = get_font("header")
        hdr_surf = font_hdr.render("■ BẢNG ĐIỀU KHIỂN (CONTROLS)", True, (241, 245, 249))
        self.screen.blit(hdr_surf, (814, 80))

        # 1. Vẽ bộ chọn bản đồ
        self.map_selector.draw(self.screen)

        # 2. Vẽ ô chọn chế độ chơi (MÁY CHƠI AI vs NGƯỜI CHƠI WASD)
        self.mode_group.draw(self.screen)

        # 3. Nội dung tùy thuộc chế độ chơi
        if self.controller.play_mode == "PLAYER":
            # Hiển thị bàn phím điều hướng D-Pad và hướng dẫn WASD / Mũi tên
            self.dpad.draw(self.screen, current_dir=self.controller.facing_dir)
        else:
            # Hiển thị các nút chọn thuật toán AI
            self.classic_group.draw(self.screen)
            self.adv_group.draw(self.screen)

            if self.controller.algorithm in ["MINIMAX", "ALPHA-BETA", "EXPECTIMAX"]:
                self.depth_stepper.draw(self.screen)
                self.adv_mode_group.draw(self.screen)
            else:
                info_rect = pygame.Rect(812, 220, 420, 25)
                pygame.draw.rect(self.screen, BG_PANEL_ALT, info_rect, border_radius=4)
                pygame.draw.rect(self.screen, BORDER_COLOR, info_rect, width=1, border_radius=4)
                mode_desc = "Chế độ: Đơn mục tiêu (Single-Goal)" if len(self.controller.foods) == 0 and len(self.controller.goals) <= 1 else f"Chế độ: Đa mục tiêu (Multi-Goal: {len(self.controller.foods)} Foods)"
                font_sub = get_font("subtitle")
                desc_surf = font_sub.render(mode_desc, True, TEXT_OLD_PAPER)
                self.screen.blit(desc_surf, desc_surf.get_rect(center=info_rect.center))

        # Cập nhật trạng thái nút Pause
        if self.controller.status == "PAUSED":
            self.btn_pause.text = "▶ RESUME"
            self.btn_pause.variant = "start"
        else:
            self.btn_pause.text = "⏸ PAUSE"
            self.btn_pause.variant = "pause"

        # Vẽ các nút tác vụ
        self.btn_start.draw(self.screen)
        self.btn_pause.draw(self.screen)
        self.btn_step.draw(self.screen)
        self.btn_reset.draw(self.screen)

        # Tốc độ mô phỏng / di chuyển
        font_sm = get_font("small")
        sp_lbl = font_sm.render("Tốc độ:", True, TEXT_MUTED)
        self.screen.blit(sp_lbl, (814, 294))
        self.speed_group.draw(self.screen)

    def _draw_metrics_panel(self):
        """Vẽ Bảng thống kê kết quả thực tế (Hỗ trợ cả chế độ AI và chế độ Người chơi)"""
        panel_rect = pygame.Rect(800, 336, 444, 198)
        draw_arcade_panel(self.screen, panel_rect, bg_color=BG_PANEL, corner_radius=6)

        font_hdr = get_font("header")
        is_player = (self.controller.play_mode == "PLAYER")
        panel_title = "■ THỐNG KÊ NGƯỜI CHƠI (PLAYER)" if is_player else "■ THỐNG KÊ AI (METRICS)"
        hdr_surf = font_hdr.render(panel_title, True, (241, 245, 249))
        self.screen.blit(hdr_surf, (814, 342))

        algo_name = "NGƯỜI CHƠI (WASD)" if is_player else self.controller.algorithm
        if is_player:
            metric_3_lbl = "Hướng di chuyển"
            metric_3_val = self.controller.facing_dir
        else:
            metric_3_lbl = "Node đã mở"
            metric_3_val = str(self.controller.expanded_count) if self.controller.expanded_count is not None else "--"

        time_str = f"{round(self.controller.time_used, 2 if is_player else 5)}s" if self.controller.time_used is not None else "--"
        eval_str = str(self.controller.last_value) if self.controller.last_value is not None else "--"
        steps_str = str(self.controller.steps_taken)

        if len(self.controller.initial_foods) > 0:
            target_lbl = "Food còn lại"
            target_str = f"{len(self.controller.remaining_foods)} / {len(self.controller.initial_foods)}"
            target_col = (254, 240, 138)
        else:
            target_lbl = "Goal còn lại"
            target_str = f"{len(self.controller.remaining_goals)} / {len(self.controller.goals)}"
            target_col = (52, 211, 153)

        cost_str = str(self.controller.path_cost) if self.controller.path_cost is not None else "--"
        score_str = str(self.controller.score)

        if not is_player and self.controller.algorithm in ["MINIMAX", "ALPHA-BETA", "EXPECTIMAX"]:
            metric_5_lbl = "Đánh giá (Eval)"
            metric_5_val = eval_str
            metric_5_col = (245, 197, 66)
        else:
            metric_5_lbl = "Tổng chi phí"
            metric_5_val = cost_str
            metric_5_col = (52, 211, 153)

        metrics = [
            ("Chế độ / TT", algo_name, (255, 214, 10)),
            ("Trạng thái", self.controller.status, STATUS_COLORS.get(self.controller.status, TEXT_BODY)),
            (metric_3_lbl, metric_3_val, (56, 189, 248)),
            ("Thời gian", time_str, (56, 189, 248)),
            (metric_5_lbl, metric_5_val, metric_5_col),
            ("Số bước di chuyển", steps_str, TEXT_HEADER),
            (target_lbl, target_str, target_col),
            ("Điểm số (Score)", score_str, (52, 211, 153)),
        ]

        font_lbl = get_font("small")
        font_val = get_font("subtitle")

        col_w = 205
        row_h = 34
        start_x = 812
        start_y = 366

        for idx, (lbl, val, val_col) in enumerate(metrics):
            r = idx // 2
            c = idx % 2
            bx = start_x + c * (col_w + 10)
            by = start_y + r * (row_h + 4)
            b_rect = pygame.Rect(bx, by, col_w, row_h)

            pygame.draw.rect(self.screen, BG_PANEL_ALT, b_rect, border_radius=4)
            pygame.draw.rect(self.screen, BORDER_COLOR, b_rect, width=1, border_radius=4)

            l_surf = font_lbl.render(lbl, True, TEXT_MUTED)
            self.screen.blit(l_surf, (bx + 8, by + 2))

            v_surf = font_val.render(val, True, val_col)
            self.screen.blit(v_surf, (bx + 8, by + 16))

    def _draw_activity_log_panel(self):
        """Vẽ Bảng nhật ký hoạt động có thể cuộn"""
        panel_rect = pygame.Rect(800, 542, 444, 222)
        draw_arcade_panel(self.screen, panel_rect, bg_color=BG_PANEL, corner_radius=6)

        font_hdr = get_font("header")
        hdr_surf = font_hdr.render("■ NHẬT KÝ HOẠT ĐỘNG (LOG)", True, (241, 245, 249))
        self.screen.blit(hdr_surf, (814, 546))

        font_sm = get_font("small")
        clear_rect = pygame.Rect(1178, 546, 54, 16)
        pygame.draw.rect(self.screen, (35, 41, 66), clear_rect, border_radius=3)
        pygame.draw.rect(self.screen, BORDER_COLOR, clear_rect, width=1, border_radius=3)
        c_surf = font_sm.render("Clear", True, TEXT_MUTED)
        self.screen.blit(c_surf, c_surf.get_rect(center=clear_rect.center))

        if pygame.mouse.get_pressed()[0] and clear_rect.collidepoint(pygame.mouse.get_pos()):
            self.log_box.clear()

        self.log_box.draw(self.screen)

    def run(self):
        """Vòng lặp chính của ứng dụng trên Desktop"""
        while self.is_running:
            self.handle_events()
            self.render()
            self.clock.tick(60)

        pygame.quit()

    async def run_async(self):
        """Vòng lặp chính bất đồng bộ tương thích với Pygbag / WebAssembly trên trình duyệt"""
        while self.is_running:
            self.handle_events()
            self.render()
            self.clock.tick(60)
            await asyncio.sleep(0)

        pygame.quit()


def run_ui():
    """Hàm khởi chạy giao diện từ main.py hoặc dòng lệnh"""
    app = PacmanVintageUI()
    app.run()


async def run_ui_async():
    """Hàm khởi chạy giao diện bất đồng bộ cho Pygbag WebAssembly"""
    app = PacmanVintageUI()
    await app.run_async()


if __name__ == "__main__":
    run_ui()
