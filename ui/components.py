"""
Các thành phần giao diện tương tác bằng chuột (Mouse-Driven Components)
Dự án: Pacman AI Search - Nhóm 07
"""

import pygame
from ui.theme import (
    get_font,
    BG_PANEL_ALT,
    BORDER_COLOR,
    BORDER_HIGHLIGHT,
    BTN_NORMAL,
    BTN_HOVER,
    BTN_ACTIVE,
    BTN_TEXT_ACTIVE,
    BTN_ACTION_START,
    BTN_ACTION_START_H,
    BTN_ACTION_STOP,
    BTN_ACTION_STOP_H,
    BTN_ACTION_PAUSE,
    BTN_ACTION_PAUSE_H,
    TEXT_HEADER,
    TEXT_BODY,
    TEXT_MUTED,
    TEXT_OLD_PAPER,
    COLOR_PACMAN,
)


class Button:
    """Nút bấm phong cách arcade cổ điển, hỗ trợ hover, active và click bằng chuột"""

    def __init__(self, rect, text, on_click=None, variant="default", font_key="subtitle", tooltip=""):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.variant = variant  # "default", "start", "stop", "pause", "tab"
        self.font_key = font_key
        self.tooltip = tooltip
        self.is_hovered = False
        self.is_active = False
        self.is_disabled = False

    def handle_event(self, event):
        if self.is_disabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface):
        # Chọn màu nền theo trạng thái
        if self.is_disabled:
            bg_col = (25, 29, 45)
            text_col = (90, 100, 125)
            border_col = (45, 52, 75)
        elif self.is_active:
            bg_col = BTN_ACTIVE
            text_col = BTN_TEXT_ACTIVE
            border_col = (210, 175, 10)
        elif self.variant == "start":
            bg_col = BTN_ACTION_START_H if self.is_hovered else BTN_ACTION_START
            text_col = (255, 255, 255)
            border_col = (52, 211, 153)
        elif self.variant == "stop":
            bg_col = BTN_ACTION_STOP_H if self.is_hovered else BTN_ACTION_STOP
            text_col = (255, 255, 255)
            border_col = (248, 113, 113)
        elif self.variant == "pause":
            bg_col = BTN_ACTION_PAUSE_H if self.is_hovered else BTN_ACTION_PAUSE
            text_col = (255, 255, 255)
            border_col = (251, 191, 36)
        else:
            bg_col = BTN_HOVER if self.is_hovered else BTN_NORMAL
            text_col = TEXT_HEADER if self.is_hovered else TEXT_BODY
            border_col = BORDER_HIGHLIGHT if self.is_hovered else BORDER_COLOR

        # Vẽ hộp nút bo góc
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=5)
        pygame.draw.rect(surface, border_col, self.rect, width=2, border_radius=5)

        # Hiệu ứng gờ sáng trên nút (Arcade button bevel)
        if not self.is_disabled and not self.is_active:
            highlight = pygame.Rect(self.rect.x + 2, self.rect.y + 1, self.rect.width - 4, 1)
            pygame.draw.rect(surface, (255, 255, 255, 40), highlight)

        # Vẽ text ở giữa
        font = get_font(self.font_key)
        rendered_text = font.render(self.text, True, text_col)
        text_rect = rendered_text.get_rect(center=self.rect.center)
        surface.blit(rendered_text, text_rect)


class ButtonGroup:
    """Nhóm các nút bấm (như chọn thuật toán hoặc chế độ) có thể chọn 1 mục"""

    def __init__(self, rects, labels, values, initial_val=None, on_change=None, font_key="subtitle", allow_none=False):
        self.buttons = []
        self.values = values
        if allow_none:
            self.selected_value = initial_val
        else:
            self.selected_value = initial_val if initial_val is not None else values[0]
        self.on_change = on_change

        for i, (r, lbl, val) in enumerate(zip(rects, labels, values)):
            btn = Button(r, lbl, variant="tab", font_key=font_key)
            self.buttons.append((btn, val))

        self._update_states()

    def _update_states(self):
        for btn, val in self.buttons:
            btn.is_active = (val == self.selected_value)

    def set_value(self, val):
        if val in self.values or val is None:
            self.selected_value = val
            self._update_states()
            if self.on_change and val is not None:
                self.on_change(val)

    def handle_event(self, event):
        for btn, val in self.buttons:
            if btn.handle_event(event):
                self.selected_value = val
                self._update_states()
                if self.on_change:
                    self.on_change(val)
                return True
        return False

    def draw(self, surface):
        for btn, _ in self.buttons:
            btn.draw(surface)


class NumberStepper:
    """Bộ điều khiển tăng giảm số nguyên (+ / -) bằng chuột, dùng cho Depth"""

    def __init__(self, rect, label, min_val=1, max_val=6, initial_val=3, on_change=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.on_change = on_change

        # Tạo nút - và +
        btn_w = 26
        btn_h = self.rect.height
        self.btn_minus = Button(
            pygame.Rect(self.rect.x, self.rect.y, btn_w, btn_h),
            "-",
            on_click=self.decrement,
            font_key="subtitle"
        )
        self.btn_plus = Button(
            pygame.Rect(self.rect.right - btn_w, self.rect.y, btn_w, btn_h),
            "+",
            on_click=self.increment,
            font_key="subtitle"
        )

    def increment(self):
        if self.value < self.max_val:
            self.value += 1
            if self.on_change:
                self.on_change(self.value)

    def decrement(self):
        if self.value > self.min_val:
            self.value -= 1
            if self.on_change:
                self.on_change(self.value)

    def handle_event(self, event):
        hit = self.btn_minus.handle_event(event) or self.btn_plus.handle_event(event)
        return hit

    def draw(self, surface):
        # Nền giữa
        mid_rect = pygame.Rect(
            self.btn_minus.rect.right + 2,
            self.rect.y,
            self.btn_plus.rect.left - self.btn_minus.rect.right - 4,
            self.rect.height
        )
        pygame.draw.rect(surface, BG_PANEL_ALT, mid_rect, border_radius=4)
        pygame.draw.rect(surface, BORDER_COLOR, mid_rect, width=1, border_radius=4)

        # Chữ hiển thị
        font = get_font("subtitle")
        display_text = f"{self.label}: {self.value}"
        rendered = font.render(display_text, True, TEXT_HEADER)
        rendered_rect = rendered.get_rect(center=mid_rect.center)
        surface.blit(rendered, rendered_rect)

        # Vẽ 2 nút
        self.btn_minus.draw(surface)
        self.btn_plus.draw(surface)


class MapSelector:
    """Bộ chọn bản đồ có mũi tên điều hướng, nút xem trước toàn cảnh (Preview) và tên file hiện tại"""

    def __init__(self, rect, map_list, initial_idx=0, on_change=None, on_open_browser=None):
        self.rect = pygame.Rect(rect)
        self.map_list = map_list
        self.current_idx = initial_idx if 0 <= initial_idx < len(map_list) else 0
        self.on_change = on_change
        self.on_open_browser = on_open_browser

        btn_w = 26
        btn_h = self.rect.height
        prev_btn_w = 84

        self.btn_prev = Button(
            pygame.Rect(self.rect.x, self.rect.y, btn_w, btn_h),
            "<",
            on_click=self.prev_map,
            font_key="header"
        )
        self.btn_next = Button(
            pygame.Rect(self.rect.right - prev_btn_w - 4 - btn_w, self.rect.y, btn_w, btn_h),
            ">",
            on_click=self.next_map,
            font_key="header"
        )
        self.btn_preview = Button(
            pygame.Rect(self.rect.right - prev_btn_w, self.rect.y, prev_btn_w, btn_h),
            "👁 XEM MAP",
            on_click=self.open_browser,
            variant="tab",
            font_key="small"
        )

        self.mid_rect = pygame.Rect(
            self.btn_prev.rect.right + 4,
            self.rect.y,
            self.btn_next.rect.left - self.btn_prev.rect.right - 8,
            self.rect.height
        )

    def open_browser(self):
        if self.on_open_browser:
            self.on_open_browser()

    def get_current_map(self):
        if not self.map_list:
            return None
        return self.map_list[self.current_idx]

    def prev_map(self):
        if self.map_list:
            self.current_idx = (self.current_idx - 1) % len(self.map_list)
            if self.on_change:
                self.on_change(self.map_list[self.current_idx])

    def next_map(self):
        if self.map_list:
            self.current_idx = (self.current_idx + 1) % len(self.map_list)
            if self.on_change:
                self.on_change(self.map_list[self.current_idx])

    def set_map(self, map_path):
        if map_path in self.map_list:
            self.current_idx = self.map_list.index(map_path)

    def handle_event(self, event):
        hit = self.btn_prev.handle_event(event) or self.btn_next.handle_event(event) or self.btn_preview.handle_event(event)
        if not hit and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.mid_rect.collidepoint(event.pos):
                self.open_browser()
                return True
        return hit

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.mid_rect.collidepoint(mouse_pos)

        # Hộp hiển thị tên file
        box_bg = (24, 30, 48) if is_hover else BG_PANEL_ALT
        box_border = BORDER_HIGHLIGHT if is_hover else BORDER_COLOR
        pygame.draw.rect(surface, box_bg, self.mid_rect, border_radius=4)
        pygame.draw.rect(surface, box_border, self.mid_rect, width=1, border_radius=4)

        cur_map = self.get_current_map()
        name_only = cur_map.split("/")[-1].split("\\")[-1] if cur_map else "No Map"

        font = get_font("subtitle")
        text_col = (255, 214, 10) if is_hover else TEXT_OLD_PAPER
        rendered = font.render(name_only, True, text_col)
        rendered_rect = rendered.get_rect(center=self.mid_rect.center)
        surface.blit(rendered, rendered_rect)

        self.btn_prev.draw(surface)
        self.btn_next.draw(surface)
        self.btn_preview.draw(surface)


class ScrollableLogBox:
    """Bảng nhật ký hoạt động có thể cuộn bằng chuột (Mouse Wheel / Nút cuộn)"""

    def __init__(self, rect, max_lines=200):
        self.rect = pygame.Rect(rect)
        self.logs = []  # List of tuples: (text, color)
        self.max_lines = max_lines
        self.scroll_offset = 0
        self.line_height = 17
        self.auto_scroll = True

        # Nút cuộn lên / xuống nhỏ
        btn_size = 18
        self.btn_up = Button(
            pygame.Rect(self.rect.right - btn_size - 2, self.rect.y + 2, btn_size, btn_size),
            "▲",
            on_click=self.scroll_up,
            font_key="small"
        )
        self.btn_down = Button(
            pygame.Rect(self.rect.right - btn_size - 2, self.rect.bottom - btn_size - 2, btn_size, btn_size),
            "▼",
            on_click=self.scroll_down,
            font_key="small"
        )

    def add_log(self, text, color=TEXT_BODY):
        self.logs.append((text, color))
        if len(self.logs) > self.max_lines:
            self.logs.pop(0)
        if self.auto_scroll:
            self.scroll_to_bottom()

    def clear(self):
        self.logs = []
        self.scroll_offset = 0

    def scroll_up(self):
        self.auto_scroll = False
        self.scroll_offset = max(0, self.scroll_offset - 2)

    def scroll_down(self):
        max_offset = max(0, len(self.logs) - self._visible_lines_count())
        self.scroll_offset = min(max_offset, self.scroll_offset + 2)
        if self.scroll_offset >= max_offset:
            self.auto_scroll = True

    def scroll_to_bottom(self):
        max_offset = max(0, len(self.logs) - self._visible_lines_count())
        self.scroll_offset = max_offset

    def _visible_lines_count(self):
        return max(1, (self.rect.height - 8) // self.line_height)

    def handle_event(self, event):
        # Cuộn bằng con lăn chuột
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                if event.y > 0:
                    self.scroll_up()
                elif event.y < 0:
                    self.scroll_down()
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_up.rect.collidepoint(event.pos):
                self.scroll_up()
                return True
            if self.btn_down.rect.collidepoint(event.pos):
                self.scroll_down()
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.btn_up.is_hovered = self.btn_up.rect.collidepoint(event.pos)
            self.btn_down.is_hovered = self.btn_down.rect.collidepoint(event.pos)
        return False

    def draw(self, surface):
        # Vẽ nền hộp log (Dark CRT terminal look)
        pygame.draw.rect(surface, (14, 16, 24), self.rect, border_radius=4)
        pygame.draw.rect(surface, BORDER_COLOR, self.rect, width=1, border_radius=4)

        # Cắt clip vùng vẽ text để không tràn ra ngoài
        clip_rect = pygame.Rect(self.rect.x + 6, self.rect.y + 4, self.rect.width - 28, self.rect.height - 8)
        prev_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        font = get_font("log")
        vis_count = self._visible_lines_count()
        start_idx = self.scroll_offset
        end_idx = min(len(self.logs), start_idx + vis_count + 1)

        y_pos = self.rect.y + 4
        for idx in range(start_idx, end_idx):
            if idx < len(self.logs):
                text, color = self.logs[idx]
                rendered = font.render(text, True, color)
                surface.blit(rendered, (self.rect.x + 8, y_pos))
                y_pos += self.line_height

        surface.set_clip(prev_clip)

        # Vẽ nút cuộn nhỏ
        self.btn_up.draw(surface)
        self.btn_down.draw(surface)

        # Vẽ thanh scrollbar nhỏ bên phải
        if len(self.logs) > vis_count:
            bar_track_h = self.rect.height - 44
            thumb_h = max(10, int(bar_track_h * (vis_count / len(self.logs))))
            max_offset = max(1, len(self.logs) - vis_count)
            thumb_y = self.rect.y + 22 + int((self.scroll_offset / max_offset) * (bar_track_h - thumb_h))
            thumb_rect = pygame.Rect(self.rect.right - 14, thumb_y, 4, thumb_h)
            pygame.draw.rect(surface, BORDER_HIGHLIGHT, thumb_rect, border_radius=2)



class DirectionalPad:
    """
    Cụm nút điều hướng D-Pad phong cách máy thùng Arcade cho chế độ Người chơi (Player Mode).
    Vừa cho phép click/nhấn giữ bằng chuột trên màn hình, vừa đồng bộ hiệu ứng sáng đèn
    khi người chơi bấm phím WASD hoặc phím mũi tên (↑ ↓ ← →) trên bàn phím.
    """

    def __init__(self, rect, on_direction=None):
        self.rect = pygame.Rect(rect)
        self.on_direction = on_direction
        self.held_mouse_action = None

        # Chia vùng: Bên trái là bảng hướng dẫn phím tắt, bên phải là cụm 4 phím điều hướng chữ T ngược (WASD)
        dpad_w = 186
        self.info_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width - dpad_w - 8, self.rect.height)
        dpad_x = self.rect.right - dpad_w

        btn_w = 58
        btn_h = (self.rect.height - 4) // 2
        gap_x = 5
        top_y = self.rect.y
        bot_y = self.rect.y + btn_h + 4

        self.btn_up = Button(
            pygame.Rect(dpad_x + btn_w + gap_x, top_y, btn_w, btn_h),
            "▲ W/↑",
            on_click=lambda: self._trigger("UP"),
            font_key="small"
        )
        self.btn_left = Button(
            pygame.Rect(dpad_x, bot_y, btn_w, btn_h),
            "◀ A/←",
            on_click=lambda: self._trigger("LEFT"),
            font_key="small"
        )
        self.btn_down = Button(
            pygame.Rect(dpad_x + btn_w + gap_x, bot_y, btn_w, btn_h),
            "▼ S/↓",
            on_click=lambda: self._trigger("DOWN"),
            font_key="small"
        )
        self.btn_right = Button(
            pygame.Rect(dpad_x + 2 * (btn_w + gap_x), bot_y, btn_w, btn_h),
            "▶ D/→",
            on_click=lambda: self._trigger("RIGHT"),
            font_key="small"
        )

        self.dir_buttons = {
            "UP": self.btn_up,
            "LEFT": self.btn_left,
            "DOWN": self.btn_down,
            "RIGHT": self.btn_right,
        }

    def _trigger(self, action):
        if self.on_direction:
            self.on_direction(action)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.held_mouse_action = None

        for act, btn in self.dir_buttons.items():
            if btn.handle_event(event):
                self.held_mouse_action = act
                return True
        return False

    def get_held_mouse_action(self):
        """Nếu người dùng đang nhấn giữ chuột trái trên một nút D-Pad thì trả về hướng đó"""
        if self.held_mouse_action and pygame.mouse.get_pressed()[0]:
            btn = self.dir_buttons.get(self.held_mouse_action)
            if btn and btn.rect.collidepoint(pygame.mouse.get_pos()):
                return self.held_mouse_action
        self.held_mouse_action = None
        return None

    def sync_active_directions(self, active_dirs):
        """Đồng bộ trạng thái sáng đèn của các nút D-Pad với bàn phím và chuột"""
        mouse_act = self.get_held_mouse_action()
        for act, btn in self.dir_buttons.items():
            btn.is_active = (act in active_dirs) or (act == mouse_act)

    def draw(self, surface, current_dir="RIGHT"):
        # Vẽ khung hướng dẫn điều khiển bên trái
        pygame.draw.rect(surface, BG_PANEL_ALT, self.info_rect, border_radius=5)
        pygame.draw.rect(surface, BORDER_COLOR, self.info_rect, width=1, border_radius=5)

        font_sub = get_font("subtitle")
        font_sm = get_font("small")

        t1 = font_sub.render("ĐIỀU KHIỂN TAY", True, COLOR_PACMAN)
        t2 = font_sm.render("Phím: WASD / ↑↓←→", True, TEXT_HEADER)
        t3 = font_sm.render(f"Hướng: {current_dir} (Bấm/Giữ)", True, TEXT_OLD_PAPER)

        surface.blit(t1, (self.info_rect.x + 10, self.info_rect.y + 6))
        surface.blit(t2, (self.info_rect.x + 10, self.info_rect.y + 28))
        surface.blit(t3, (self.info_rect.x + 10, self.info_rect.y + 46))

        # Vẽ 4 nút D-Pad bên phải
        for btn in self.dir_buttons.values():
            btn.draw(surface)
