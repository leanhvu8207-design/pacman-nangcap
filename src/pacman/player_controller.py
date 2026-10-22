"""
Module điều khiển Pacman dành cho Người chơi (Human Player Controller) theo thiết kế OOP.
Hỗ trợ:
- Điều khiển bằng cụm phím WASD, phím mũi tên (UP/DOWN/LEFT/RIGHT) và nút D-Pad trên giao diện.
- Cơ chế đệm phím thông minh (Input Buffering & Corner Pre-turning): vừa hỗ trợ bấm nhấp từng bước chính xác,
  vừa hỗ trợ nhấn giữ để di chuyển liên tục mượt mà và rẽ sớm tại các ngã giao.
- Quản lý phiên chơi của người dùng (PlayerSession): tính điểm, chi phí địa hình, ăn Food/Goal và Ghost đuổi theo.
"""

import time
import pygame
from src.pacman.game_state import GameState
from src.ghost.ghost import Ghost
from src.utils.map_info import get_tile_cost


class DirectionInputBuffer:
    """
    Bộ quản lý và đệm tín hiệu điều khiển hướng đi của người chơi (Keyboard WASD / Arrow Keys / UI D-Pad).
    """

    KEY_MAP = {
        pygame.K_w: "UP",
        pygame.K_UP: "UP",
        pygame.K_s: "DOWN",
        pygame.K_DOWN: "DOWN",
        pygame.K_a: "LEFT",
        pygame.K_LEFT: "LEFT",
        pygame.K_d: "RIGHT",
        pygame.K_RIGHT: "RIGHT",
    }

    VALID_ACTIONS = ("UP", "DOWN", "LEFT", "RIGHT")

    def __init__(self):
        # Danh sách các hướng tương ứng với phím đang được nhấn giữ (theo thứ tự thời gian nhấn)
        self._held_actions = []
        # Bước đi tức thời khi người chơi vừa gõ phím hoặc bấm nút D-Pad trên màn hình
        self._queued_action = None
        # Hướng rẽ dự kiến được lưu đệm khi người chơi bấm trước ở gần ngã rẽ (Corner Pre-turn)
        self._buffered_turn = None
        self._buffered_turn_time = 0.0
        # Thời hạn hiệu lực của phím rẽ đệm (giây)
        self.buffer_window_sec = 0.40

    def reset(self):
        """Xóa toàn bộ trạng thái phím đang giữ và bộ đệm hướng đi"""
        self._held_actions.clear()
        self._queued_action = None
        self._buffered_turn = None
        self._buffered_turn_time = 0.0

    @classmethod
    def key_to_action(cls, key):
        """Ánh xạ mã phím Pygame sang hành động chuẩn ('UP', 'DOWN', 'LEFT', 'RIGHT')"""
        return cls.KEY_MAP.get(key)

    def _sync_hardware_keys(self):
        """Đồng bộ danh sách phím giữ với trạng thái bàn phím thực tế để tránh kẹt phím"""
        if not pygame.get_init() or not pygame.key.get_focused():
            return
        pressed = pygame.key.get_pressed()
        active_hw_actions = set()
        for k, act in self.KEY_MAP.items():
            if pressed[k]:
                active_hw_actions.add(act)
        self._held_actions = [act for act in self._held_actions if act in active_hw_actions]

    def on_key_down(self, key):
        """Xử lý sự kiện nhấn phím xuống (KEYDOWN)"""
        action = self.key_to_action(key)
        if action is None:
            return None

        if action in self._held_actions:
            self._held_actions.remove(action)
        self._held_actions.append(action)

        self._queued_action = action
        self._buffered_turn = action
        self._buffered_turn_time = time.time()
        return action

    def on_key_up(self, key):
        """Xử lý sự kiện nhả phím (KEYUP)"""
        action = self.key_to_action(key)
        if action is None:
            return None

        still_held = False
        if pygame.get_init():
            pressed = pygame.key.get_pressed()
            for k, act in self.KEY_MAP.items():
                if act == action and k != key and pressed[k]:
                    still_held = True
                    break

        if not still_held and action in self._held_actions:
            self._held_actions.remove(action)
        return action

    def trigger_button_action(self, action):
        """Kích hoạt bước di chuyển từ nút bấm D-Pad trên giao diện"""
        if action in self.VALID_ACTIONS:
            self._held_actions.clear()
            self._queued_action = action
            self._buffered_turn = action
            self._buffered_turn_time = time.time()
            return action
        return None

    def get_active_directions(self):
        """Trả về tập các hướng đang được nhấn giữ hoặc vừa kích hoạt (phục vụ highlight nút D-Pad)"""
        self._sync_hardware_keys()
        active = set(self._held_actions)
        if self._queued_action:
            active.add(self._queued_action)
        return active

    def pop_next_action(self, can_move_fn):
        """
        Lấy hành động hợp lệ tiếp theo cho Pacman tại khung thời gian hiện tại:
        1. Ưu tiên hướng rẽ được đệm (_buffered_turn) nếu còn hiệu lực và ô đó rẽ vào được.
        2. Tiếp theo xét bước gõ phím tức thời (_queued_action).
        3. Nếu người chơi đang nhấn giữ phím (_held_actions), lấy phím mới nhất có thể đi được.
        """
        now = time.time()
        self._sync_hardware_keys()

        # 1. Kiểm tra hướng rẽ đệm (Corner Pre-turn) nếu còn trong thời gian buffer
        if self._buffered_turn is not None:
            if now - self._buffered_turn_time <= self.buffer_window_sec:
                if can_move_fn(self._buffered_turn):
                    act = self._buffered_turn
                    self._buffered_turn = None
                    if self._queued_action == act:
                        self._queued_action = None
                    return act
            else:
                self._buffered_turn = None

        # 2. Kiểm tra bước nhấn phím tức thời (Tap)
        if self._queued_action is not None:
            act = self._queued_action
            self._queued_action = None
            if can_move_fn(act):
                if self._buffered_turn == act:
                    self._buffered_turn = None
                return act
            # Nếu không có phím giữ khác khả dụng thì trả về act để cập nhật hướng mặt Pacman
            for held_act in reversed(self._held_actions):
                if held_act != act and can_move_fn(held_act):
                    return held_act
            return act

        # 3. Kiểm tra danh sách phím đang giữ (từ phím mới nhấn nhất tới phím cũ hơn)
        for act in reversed(self._held_actions):
            if can_move_fn(act):
                return act

        return None


class PlayerSession:
    """
    Quản lý logic trạng thái một ván chơi điều khiển thủ công bởi Người chơi (Human Mode).
    Đóng gói toàn bộ quy tắc di chuyển, tính chi phí địa hình, ăn Food/Goal và Ghost truy đuổi.
    """

    MOVE_DELTAS = {
        "UP": (-1, 0),
        "DOWN": (1, 0),
        "LEFT": (0, -1),
        "RIGHT": (0, 1),
    }

    def __init__(self, game_map, spawn, goals, ghosts, foods):
        self.game_map = game_map
        self.spawn = spawn
        self.initial_goals = list(goals) if goals else []
        self.initial_ghosts = list(ghosts) if ghosts else []
        self.initial_foods = set(foods) if foods else set()

        self.pacman_pos = spawn
        self.ghost_positions = list(self.initial_ghosts)
        self.ghost_facing_dirs = ["DOWN"] * len(self.initial_ghosts)
        self.remaining_foods = set(self.initial_foods)
        self.remaining_goals = list(self.initial_goals)

        self.facing_dir = "RIGHT"
        self.score = 0
        self.steps_taken = 0
        self.path_cost = 0
        self.path_trail = [spawn] if spawn else []
        self.status = "READY"
        self.start_time = None
        self.elapsed_time = 0.0

    def can_move_from(self, pos, action):
        """Kiểm tra từ vị trí `pos` có thể bước theo hướng `action` mà không đụng tường '#' không"""
        if not self.game_map or pos is None or action not in self.MOVE_DELTAS:
            return False
        dr, dc = self.MOVE_DELTAS[action]
        nr, nc = pos[0] + dr, pos[1] + dc
        if 0 <= nr < len(self.game_map) and 0 <= nc < len(self.game_map[nr]):
            return self.game_map[nr][nc] != "#"
        return False

    def can_move(self, action):
        """Kiểm tra Pacman hiện tại có thể di chuyển theo hướng `action` không"""
        return self.can_move_from(self.pacman_pos, action)

    def execute_step(self, action):
        """
        Thực hiện 1 bước di chuyển của người chơi theo hướng `action` và cập nhật lượt đi của các Ghost.
        Trả về dict chứa thông tin chi tiết của bước đi để Controller và UI hiển thị.
        """
        if self.status in ("WIN", "LOSE", "ERROR") or self.pacman_pos is None:
            return {"moved": False, "reason": "TERMINATED"}

        if action not in self.MOVE_DELTAS:
            return {"moved": False, "reason": "INVALID_ACTION"}

        # Luôn xoay mặt Pacman theo hướng người chơi bấm để phản hồi thị giác tức thì
        self.facing_dir = action

        if not self.can_move(action):
            return {"moved": False, "reason": "WALL", "action": action}

        if self.start_time is None:
            self.start_time = time.time()
        if self.status == "READY":
            self.status = "RUNNING"

        dr, dc = self.MOVE_DELTAS[action]
        new_pos = (self.pacman_pos[0] + dr, self.pacman_pos[1] + dc)
        self.pacman_pos = new_pos
        self.steps_taken += 1

        step_cost = get_tile_cost(new_pos, self.game_map)
        self.path_cost += step_cost
        self.path_trail.append(new_pos)
        self.elapsed_time = time.time() - self.start_time

        events = []

        # 1. Kiểm tra ăn Food (.)
        if new_pos in self.remaining_foods:
            self.remaining_foods.remove(new_pos)
            self.score += 10
            events.append(("FOOD", new_pos, len(self.remaining_foods), self.score))

        # 2. Kiểm tra thu thập Goal (G)
        if new_pos in self.remaining_goals:
            # Nếu còn Food và chỉ có 1 Goal đích cuối cùng -> bắt buộc ăn hết Food trước
            if len(self.remaining_foods) > 0 and len(self.initial_goals) == 1:
                events.append(("GOAL_LOCKED", new_pos, len(self.remaining_foods)))
            else:
                self.remaining_goals.remove(new_pos)
                self.score += 20
                events.append(("GOAL", new_pos, len(self.remaining_goals), self.score))

        # 3. Kiểm tra Pacman đâm vào Ghost ngay khi bước tới
        if new_pos in self.ghost_positions:
            self.status = "LOSE"
            events.append(("CAUGHT", new_pos))
            return {
                "moved": True,
                "action": action,
                "position": new_pos,
                "step_cost": step_cost,
                "events": events,
                "status": self.status,
            }

        # 4. Kiểm tra điều kiện Chiến thắng (Đã ăn hết toàn bộ Food và thu thập hết Goal)
        if len(self.remaining_foods) == 0 and len(self.remaining_goals) == 0:
            self.status = "WIN"
            events.append(("WIN", new_pos))
            return {
                "moved": True,
                "action": action,
                "position": new_pos,
                "step_cost": step_cost,
                "events": events,
                "status": self.status,
            }

        # 5. Cho các Ghost di chuyển đuổi theo Pacman (nếu bản đồ có Ghost)
        ghost_moves = []
        for g_idx in range(len(self.ghost_positions)):
            g_pos = self.ghost_positions[g_idx]
            ghost = Ghost(g_pos)
            other_ghosts = [
                pos for idx, pos in enumerate(self.ghost_positions) if idx != g_idx
            ]
            g_act = ghost.choose_action(
                self.game_map,
                self.pacman_pos,
                other_ghost_positions=other_ghosts
            )
            if g_act is not None:
                next_g_pos = ghost.get_next_position(g_act, self.game_map)
                if next_g_pos is not None:
                    self.ghost_positions[g_idx] = next_g_pos
                    self.ghost_facing_dirs[g_idx] = g_act
                    ghost_moves.append((g_idx, g_act, next_g_pos))

            # Kiểm tra Ghost bắt được Pacman
            if self.pacman_pos in self.ghost_positions:
                self.status = "LOSE"
                events.append(("CAUGHT", self.pacman_pos))
                break

        self.elapsed_time = time.time() - self.start_time
        return {
            "moved": True,
            "action": action,
            "position": new_pos,
            "step_cost": step_cost,
            "events": events,
            "ghost_moves": ghost_moves,
            "status": self.status,
        }
