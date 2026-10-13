"""
Giao diện đồ họa Vintage Arcade cho dự án Pacman AI Search - Nhóm 07
Tương tác chuột 100%, render mê cung và nhân vật cổ điển, tích hợp thuật toán AI
"""

import sys
import os
import pygame

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
)
from ui.map_browser import MapBrowserModal
from ui.renderer import MazeRenderer
from ui.controller import GameController

class PacmanVintageUI:
    """Ứng dụng giao diện Retro Arcade hoàn chỉnh"""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("PACMAN AI SEARCH - NHOM 07 [VINTAGE ARCADE]")

        self.width = 1260
        self.height = 780
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.is_running = True

        init_fonts()

        self.log_box = ScrollableLogBox(pygame.Rect(812, 546, 420, 208))

        self.controller = GameController(log_callback=self.on_log_received)

        self.maze_viewport = pygame.Rect(16, 74, 768, 690)
        self.maze_renderer = MazeRenderer(self.maze_viewport)
        self.maze_renderer.compute_layout(self.controller.game_map)

        self.map_browser = MapBrowserModal(
            (self.width, self.height),
            self.controller.map_files,
            self.controller.current_map_file,
            on_select=self.on_map_browser_select
        )
        self.show_map_browser = False

        self._init_ui_components()

    def on_log_received(self, text, color):
        self.log_box.add_log(text, color)

    def _init_ui_components(self):
        self.map_selector = MapSelector(
            pygame.Rect(812, 98, 420, 28),
            self.controller.map_files,
            initial_idx=self.controller.map_files.index(self.controller.current_map_file) if self.controller.current_map_file in self.controller.map_files else 0,
            on_change=self.on_map_changed,
            on_open_browser=self.open_map_browser
        )

        classic_algos = ["DFS", "BFS", "UCS", "GREEDY", "A*"]
        btn_w_classic = 78
        rects_classic = [
            pygame.Rect(812 + i * (btn_w_classic + 7), 136, btn_w_classic, 25)
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

        adv_algos = ["MINIMAX", "ALPHA-BETA"]
        btn_w_adv = 206
        rects_adv = [
            pygame.Rect(812 + i * (btn_w_adv + 8), 166, btn_w_adv, 25)
            for i in range(len(adv_algos))
        ]
        self.adv_group = ButtonGroup(
            rects_adv,
            ["MINIMAX (ĐỐI KHÁNG)", "ALPHA-BETA (CẮT TỈA)"],
            adv_algos,
            initial_val=None,
            on_change=self.on_algorithm_changed,
            font_key="subtitle",
            allow_none=True
        )

        self.on_algorithm_changed(self.controller.algorithm)

        self.depth_stepper = NumberStepper(
            pygame.Rect(812, 197, 190, 26),
            label="Depth",
            min_val=1,
            max_val=6,
            initial_val=self.controller.depth,
            on_change=self.on_depth_changed
        )

        self.adv_mode_group = ButtonGroup(
            [pygame.Rect(1010, 197, 110, 26), pygame.Rect(1126, 197, 106, 26)],
            ["Mô phỏng", "1 Bước"],
            ["MATCH", "STEP"],
            initial_val=self.controller.adv_mode,
            on_change=self.on_adv_mode_changed,
            font_key="subtitle"
        )

        act_y = 230
        act_w = 100
        act_gap = 7
        self.btn_start = Button(
            pygame.Rect(812 + 0 * (act_w + act_gap), act_y, act_w, 32),
            "▶ START",
            on_click=self.controller.start,
            variant="start",
            font_key="header"
        )
        self.btn_pause = Button(
            pygame.Rect(812 + 1 * (act_w + act_gap), act_y, act_w, 32),
            "⏸ PAUSE",
            on_click=self.toggle_pause,
            variant="pause",
            font_key="header"
        )
        self.btn_step = Button(
            pygame.Rect(812 + 2 * (act_w + act_gap), act_y, act_w, 32),
            "⏭ STEP",
            on_click=self.controller.step_forward,
            variant="default",
            font_key="header"
        )
        self.btn_reset = Button(
            pygame.Rect(812 + 3 * (act_w + act_gap), act_y, act_w, 32),
            "↺ RESET",
            on_click=self.controller.reset_state,
            variant="stop",
            font_key="header"
        )

        speeds = [0.5, 1.0, 2.0, 4.0, 10.0]
        speed_labels = ["0.5x", "1.0x", "2.0x", "4.0x", "Max"]
        sp_w = 66
        sp_rects = [
            pygame.Rect(878 + i * (sp_w + 5), 268, sp_w, 22)
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
        if hasattr(self, "map_browser"):
            self.map_browser.selected_map = new_map_path

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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                self.controller.stop_execution()
                return

            if self.show_map_browser:
                res = self.map_browser.handle_event(event)
                if res in ["CLOSE", "SELECT"]:
                    self.close_map_browser()
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.open_map_browser()
                elif event.key == pygame.K_SPACE:
                    self.toggle_pause()
                elif event.key == pygame.K_r:
                    self.controller.reset_state()
                elif event.key == pygame.K_s:
                    self.controller.step_forward()
                elif event.key == pygame.K_RETURN:
                    self.controller.start()
                elif event.key == pygame.K_ESCAPE:
                    self.is_running = False
                    self.controller.stop_execution()
                    return

            self.map_selector.handle_event(event)
            self.classic_group.handle_event(event)
            self.adv_group.handle_event(event)

            if self.controller.algorithm in ["MINIMAX", "ALPHA-BETA"]:
                self.depth_stepper.handle_event(event)
                self.adv_mode_group.handle_event(event)

            self.btn_start.handle_event(event)
            self.btn_pause.handle_event(event)
            self.btn_step.handle_event(event)
            self.btn_reset.handle_event(event)
            self.speed_group.handle_event(event)
            self.log_box.handle_event(event)

    def render(self):
        self.screen.fill(BG_MAIN)

        self._draw_header()

        self.maze_renderer.update_animation()
        self.maze_renderer.draw_maze(
            self.screen,
            self.controller.game_map,
            remaining_food=self.controller.remaining_foods,
            goals=self.controller.remaining_goals,
            path_trail=self.controller.path_trail,
            is_win=(self.controller.status == "WIN")
        )

        if self.controller.pacman_pos:
            self.maze_renderer.draw_pacman(
                self.screen,
                self.controller.pacman_pos[0],
                self.controller.pacman_pos[1],
                direction=self.controller.facing_dir
            )

        for g_idx, g_pos in enumerate(self.controller.ghost_positions):
            self.maze_renderer.draw_ghost(
                self.screen,
                g_idx,
                g_pos[0],
                g_pos[1],
                facing_dir="DOWN"
            )

        self._draw_control_panel()
        self._draw_metrics_panel()
        self._draw_activity_log_panel()

        if self.show_map_browser:
            self.map_browser.draw(self.screen)

        pygame.display.flip()

    def _draw_header(self):
        """Vẽ thanh tiêu đề Header phong cách bảng điều khiển Arcade cổ điển"""
        header_rect = pygame.Rect(16, 12, self.width - 32, 50)
        draw_arcade_panel(self.screen, header_rect, bg_color=BG_PANEL, corner_radius=6)

        font_title = get_font("title")
        title_surf = font_title.render("PACMAN AI SEARCH", True, TEXT_TITLE)
        self.screen.blit(title_surf, (34, 22))

        font_badge = get_font("badge")
        grp_badge_rect = pygame.Rect(320, 24, 96, 26)
        pygame.draw.rect(self.screen, (40, 48, 75), grp_badge_rect, border_radius=4)
        pygame.draw.rect(self.screen, (251, 191, 36), grp_badge_rect, width=1, border_radius=4)
        grp_surf = font_badge.render("GROUP 07", True, (251, 191, 36))
        self.screen.blit(grp_surf, grp_surf.get_rect(center=grp_badge_rect.center))

        st_text = self.controller.status
        st_color = STATUS_COLORS.get(st_text, STATUS_COLORS["READY"])
        st_badge_rect = pygame.Rect(430, 24, 110, 26)
        pygame.draw.rect(self.screen, (25, 30, 48), st_badge_rect, border_radius=4)
        pygame.draw.rect(self.screen, st_color, st_badge_rect, width=2, border_radius=4)
        st_surf = font_badge.render(f"● {st_text}", True, st_color)
        self.screen.blit(st_surf, st_surf.get_rect(center=st_badge_rect.center))

        font_hint = get_font("small")
        hint_surf = font_hint.render("[M: Maps  |  Enter: Start  |  Space: Pause  |  S: Step  |  R: Reset]", True, (130, 145, 175))
        self.screen.blit(hint_surf, (self.width - hint_surf.get_width() - 36, 29))

    def _draw_control_panel(self):
        """Vẽ Bảng điều khiển thuật toán, bản đồ và nút tác vụ"""
        panel_rect = pygame.Rect(800, 74, 444, 226)
        draw_arcade_panel(self.screen, panel_rect, bg_color=BG_PANEL, corner_radius=6)

        font_hdr = get_font("header")
        hdr_surf = font_hdr.render("■ BẢNG ĐIỀU KHIỂN (CONTROLS)", True, (241, 245, 249))
        self.screen.blit(hdr_surf, (814, 80))

        font_sm = get_font("small")

        self.map_selector.draw(self.screen)

        self.classic_group.draw(self.screen)
        self.adv_group.draw(self.screen)

        if self.controller.algorithm in ["MINIMAX", "ALPHA-BETA"]:
            self.depth_stepper.draw(self.screen)
            self.adv_mode_group.draw(self.screen)
        else:
            info_rect = pygame.Rect(812, 197, 420, 26)
            pygame.draw.rect(self.screen, BG_PANEL_ALT, info_rect, border_radius=4)
            pygame.draw.rect(self.screen, BORDER_COLOR, info_rect, width=1, border_radius=4)
            mode_desc = "Chế độ: Đơn mục tiêu (Single-Goal)" if len(self.controller.foods) == 0 and len(self.controller.goals) <= 1 else f"Chế độ: Đa mục tiêu (Multi-Goal: {len(self.controller.foods)} Foods)"
            font_sub = get_font("subtitle")
            desc_surf = font_sub.render(mode_desc, True, TEXT_OLD_PAPER)
            self.screen.blit(desc_surf, desc_surf.get_rect(center=info_rect.center))

        if self.controller.status == "PAUSED":
            self.btn_pause.text = "▶ RESUME"
            self.btn_pause.variant = "start"
        else:
            self.btn_pause.text = "⏸ PAUSE"
            self.btn_pause.variant = "pause"

        self.btn_start.draw(self.screen)
        self.btn_pause.draw(self.screen)
        self.btn_step.draw(self.screen)
        self.btn_reset.draw(self.screen)

        sp_lbl = font_sm.render("Tốc độ:", True, TEXT_MUTED)
        self.screen.blit(sp_lbl, (814, 272))
        self.speed_group.draw(self.screen)

    def _draw_metrics_panel(self):
        """Vẽ Bảng thống kê AI từ kết quả tính toán thực tế"""
        panel_rect = pygame.Rect(800, 310, 444, 204)
        draw_arcade_panel(self.screen, panel_rect, bg_color=BG_PANEL, corner_radius=6)

        font_hdr = get_font("header")
        hdr_surf = font_hdr.render("■ THỐNG KÊ AI (METRICS)", True, (241, 245, 249))
        self.screen.blit(hdr_surf, (814, 316))

        algo_name = self.controller.algorithm
        expanded_str = str(self.controller.expanded_count) if self.controller.expanded_count is not None else "--"
        time_str = f"{round(self.controller.time_used, 5)}s" if self.controller.time_used is not None else "--"
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

        if algo_name in ["MINIMAX", "ALPHA-BETA"]:
            metric_5_lbl = "Đánh giá (Eval)"
            metric_5_val = eval_str
            metric_5_col = (245, 197, 66)
        else:
            metric_5_lbl = "Tổng chi phí"
            metric_5_val = cost_str
            metric_5_col = (52, 211, 153)

        metrics = [
            ("Thuật toán", algo_name, (255, 214, 10)),
            ("Trạng thái", self.controller.status, STATUS_COLORS.get(self.controller.status, TEXT_BODY)),
            ("Node đã mở", expanded_str, (56, 189, 248)),
            ("Thời gian chạy", time_str, (56, 189, 248)),
            (metric_5_lbl, metric_5_val, metric_5_col),
            ("Số bước di chuyển", steps_str, TEXT_HEADER),
            (target_lbl, target_str, target_col),
            ("Điểm số (Score)", score_str, (52, 211, 153)),
        ]

        font_lbl = get_font("small")
        font_val = get_font("subtitle")

        col_w = 205
        row_h = 36
        start_x = 812
        start_y = 338

        for idx, (lbl, val, val_col) in enumerate(metrics):
            r = idx // 2
            c = idx % 2
            bx = start_x + c * (col_w + 10)
            by = start_y + r * (row_h + 4)
            b_rect = pygame.Rect(bx, by, col_w, row_h)

            pygame.draw.rect(self.screen, BG_PANEL_ALT, b_rect, border_radius=4)
            pygame.draw.rect(self.screen, BORDER_COLOR, b_rect, width=1, border_radius=4)

            l_surf = font_lbl.render(lbl, True, TEXT_MUTED)
            self.screen.blit(l_surf, (bx + 8, by + 3))

            v_surf = font_val.render(val, True, val_col)
            self.screen.blit(v_surf, (bx + 8, by + 17))

    def _draw_activity_log_panel(self):
        """Vẽ Bảng nhật ký hoạt động có thể cuộn"""
        panel_rect = pygame.Rect(800, 524, 444, 240)
        draw_arcade_panel(self.screen, panel_rect, bg_color=BG_PANEL, corner_radius=6)

        font_hdr = get_font("header")
        hdr_surf = font_hdr.render("■ NHẬT KÝ HOẠT ĐỘNG (LOG)", True, (241, 245, 249))
        self.screen.blit(hdr_surf, (814, 528))

        font_sm = get_font("small")
        clear_rect = pygame.Rect(1178, 528, 54, 18)
        pygame.draw.rect(self.screen, (35, 41, 66), clear_rect, border_radius=3)
        pygame.draw.rect(self.screen, BORDER_COLOR, clear_rect, width=1, border_radius=3)
        c_surf = font_sm.render("Clear", True, TEXT_MUTED)
        self.screen.blit(c_surf, c_surf.get_rect(center=clear_rect.center))

        if pygame.mouse.get_pressed()[0] and clear_rect.collidepoint(pygame.mouse.get_pos()):
            self.log_box.clear()

        self.log_box.draw(self.screen)

    def run(self):
        """Vòng lặp chính của ứng dụng"""
        while self.is_running:
            self.handle_events()
            self.render()
            self.clock.tick(60)

        pygame.quit()

def run_ui():
    """Hàm khởi chạy giao diện từ main.py hoặc dòng lệnh"""
    app = PacmanVintageUI()
    app.run()

if __name__ == "__main__":
    run_ui()
