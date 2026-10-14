"""
Bộ điều khiển logic game, thuật toán AI và trạng thái mô phỏng (Game Controller)
Dự án: Pacman AI Search - Nhóm 07
"""

import os
import glob
import time
import threading
from collections import deque

from src.utils.map_loader import load_map
from src.utils.map_info import get_map_info

from src.search.pm_search_problem import PMSearchProblem
from src.search.multi_goal_search import MultiGoal
from src.search.bfs import BFS
from src.search.dfs import DFS
from src.search.ucs import UCS
from src.search.greedy import Greedy
from src.search.a_star import AStar

from src.pacman.game_state import GameState
from src.logic_pacman_vs_ghost.adv_problem import AdvProblem
from src.logic_pacman_vs_ghost.minimax import Minimax
from src.logic_pacman_vs_ghost.alpha_beta import AlphaBeta

from ui.theme import (
    TEXT_BODY,
    TEXT_MUTED,
    TEXT_TITLE,
    STATUS_COLORS,
    COLOR_PACMAN,
)

class GameController:
    """Quản lý nạp map, điều phối thuật toán và vòng lặp mô phỏng UI không block giao diện"""

    def __init__(self, log_callback=None):
        self.log_callback = log_callback

        self.map_files = self._scan_maps()
        self.current_map_file = "maps/test_map.txt" if "maps/test_map.txt" in self.map_files else (self.map_files[0] if self.map_files else "")
        self.game_map = None

        self.spawn = None
        self.goals = []
        self.ghosts = []
        self.foods = []
        self.initial_foods = set()

        self.algorithm = "A*"
        self.depth = 3
        self.adv_mode = "MATCH"
        self.speed = 1.0

        self.status = "READY"
        self.pacman_pos = None
        self.ghost_positions = []
        self.remaining_foods = set()
        self.score = 0
        self.facing_dir = "RIGHT"
        self.path_trail = []

        self.expanded_count = None
        self.time_used = None
        self.last_value = None
        self.steps_taken = 0
        self.path_cost = None

        self._thread = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._step_trigger = threading.Event()
        self.is_stepping = False

        self.lich_su_positions = []
        self.lich_su_actions = []

        if self.current_map_file:
            self.load_current_map()

    def _scan_maps(self):
        """Quét tất cả các file bản đồ trong thư mục maps/ (loại bỏ các file lỗi dành riêng cho unit test)"""
        maps = glob.glob("maps/*.txt")
        maps = [m.replace("\\", "/") for m in maps if not m.endswith("bad_map.txt")]
        preferred = [
            "maps/classic_pacman_arcade.txt",
            "maps/single_goal_small_open.txt",
            "maps/single_goal_dense_maze.txt",
            "maps/multi_food_four_corners.txt",
            "maps/multi_food_and_final_goal.txt",
            "maps/adversarial_single_ghost_corridor.txt",
            "maps/adversarial_two_ghosts_pincer.txt",
            "maps/test_map.txt",
            "maps/adversarial_small.txt",
            "maps/multi_goal_test.txt",
            "maps/large_map.txt",
            "maps/dead_end_maze.txt",
            "maps/no_solution_map.txt",
        ]
        sorted_maps = []
        for p in preferred:
            if p in maps:
                sorted_maps.append(p)
        for m in maps:
            if m not in sorted_maps:
                sorted_maps.append(m)
        return sorted_maps

    def log(self, text, color=TEXT_BODY):
        if self.log_callback:
            self.log_callback(text, color)

    def load_current_map(self):
        """Nạp bản đồ từ file hiện tại và reset các thông số"""
        self.stop_execution()
        self.game_map = load_map(self.current_map_file)

        if self.game_map is None:
            self.status = "ERROR"
            self.spawn = None
            self.goals = []
            self.ghosts = []
            self.foods = []
            self.remaining_foods = set()
            self.pacman_pos = None
            self.ghost_positions = []
            self.log(f"[LỖI] Không thể nạp bản đồ từ: {self.current_map_file}", STATUS_COLORS["ERROR"])
            self.log("Vui lòng kiểm tra cú pháp file bản đồ!", TEXT_MUTED)
            return False

        self.spawn, self.goals, self.ghosts, self.foods = get_map_info(self.game_map, return_foods=True)
        self.initial_foods = set(self.foods)
        self.reset_state()

        self.log(f"Đã nạp bản đồ: {self.current_map_file}", TEXT_TITLE)
        self.log(f"-> Pacman: {self.spawn} | Goals: {len(self.goals)} | Foods: {len(self.foods)} | Ghosts: {len(self.ghosts)}", TEXT_MUTED)
        return True

    def set_map_file(self, file_path):
        self.current_map_file = file_path
        self.load_current_map()

    def set_algorithm(self, algo_name):
        self.algorithm = algo_name
        self.log(f"Đã chọn thuật toán: {self.algorithm}", (255, 214, 10))

    def set_depth(self, depth):
        self.depth = depth
        self.log(f"Độ sâu tìm kiếm đối kháng: {self.depth}", TEXT_MUTED)

    def set_adv_mode(self, mode):
        self.adv_mode = mode

    def set_speed(self, speed_val):
        self.speed = speed_val

    def reset_state(self):
        """Đặt lại vị trí ban đầu của nhân vật và thống kê"""
        self.stop_execution()
        self.status = "READY"
        self.pacman_pos = self.spawn
        self.ghost_positions = list(self.ghosts)
        self.remaining_foods = set(self.initial_foods)
        self.remaining_goals = list(self.goals)
        self.score = 0
        self.facing_dir = "RIGHT"
        self.path_trail = []

        self.expanded_count = None
        self.time_used = None
        self.last_value = None
        self.steps_taken = 0
        self.path_cost = None

        self.lich_su_positions = [self.spawn] if self.spawn else []
        self.lich_su_actions = []

    def stop_execution(self):
        """Dừng luồng thực thi nền an toàn"""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._pause_event.set()
            self._step_trigger.set()
            self._thread.join(timeout=0.4)
        self._stop_event.clear()
        self._pause_event.set()
        self._step_trigger.clear()

    def start(self):
        """Bắt đầu chạy thuật toán hoặc tiếp tục từ trạng thái PAUSED"""
        if self.status == "PAUSED":
            self.resume()
            return

        if self.status in ["RUNNING"]:
            return

        if self.game_map is None:
            self.log("[LỖI] Chưa có bản đồ hợp lệ!", STATUS_COLORS["ERROR"])
            return

        self.reset_state()
        self.status = "RUNNING"
        self.log(f"--- BẮT ĐẦU CHẠY [{self.algorithm}] ---", (56, 189, 248))

        self._stop_event.clear()
        self._pause_event.set()
        self._step_trigger.clear()

        if self.algorithm in ["DFS", "BFS", "UCS", "GREEDY", "A*"]:
            self._thread = threading.Thread(target=self._run_classic_search, daemon=True)
        else:
            self._thread = threading.Thread(target=self._run_adversarial_search, daemon=True)

        self._thread.start()

    def pause(self):
        """Tạm dừng mô phỏng"""
        if self.status == "RUNNING":
            self.status = "PAUSED"
            self._pause_event.clear()
            self.log("[TẠM DỪNG] Đã dừng mô phỏng.", STATUS_COLORS["PAUSED"])

    def resume(self):
        """Tiếp tục sau khi tạm dừng"""
        if self.status == "PAUSED":
            self.status = "RUNNING"
            self._pause_event.set()
            self.log("[TIẾP TỤC] Tiếp tục mô phỏng.", STATUS_COLORS["RUNNING"])

    def step_forward(self):
        """Thực hiện duy nhất 1 bước (Hữu ích khi debug hoặc quan sát từng bước)"""
        if self.status == "READY":
            self.start()
            self.pause()
            self.is_stepping = True
            self._step_trigger.set()
        elif self.status == "PAUSED":
            self.is_stepping = True
            self._step_trigger.set()

    def _plan_multi_food_tour(self, algo_name, final_goal=None):
        """
        Lập kế hoạch ăn sạch toàn bộ thức ăn bằng cách tìm đường liên tiếp tới viên gần nhất.
        Giải quyết bài toán bùng nổ tổ hợp khi số lượng food lớn (> 12).
        Tự động loại bỏ các viên thức ăn bị Pacman bước qua trên đường đi.
        """
        remaining = set(self.foods)
        curr = self.spawn
        remaining.discard(curr)
        all_actions = []
        total_nodes = 0
        t0 = time.time()

        while remaining:
            if self._stop_event.is_set():
                return None, 0, 0
            next_food = min(remaining, key=lambda f: abs(curr[0] - f[0]) + abs(curr[1] - f[1]))
            if curr == next_food:
                remaining.discard(curr)
                continue

            prob = PMSearchProblem(curr, next_food, self.game_map)
            if algo_name == "DFS": searcher = DFS(prob)
            elif algo_name == "BFS": searcher = BFS(prob)
            elif algo_name == "UCS": searcher = UCS(prob)
            elif algo_name == "GREEDY": searcher = Greedy(prob)
            else: searcher = AStar(prob)

            sub_acts = searcher.search()
            if sub_acts is None:
                break
            all_actions.extend(sub_acts)
            total_nodes += searcher.expanded_count

            tr, tc = curr
            remaining.discard((tr, tc))
            for act in sub_acts:
                if act == "UP": tr -= 1
                elif act == "DOWN": tr += 1
                elif act == "LEFT": tc -= 1
                elif act == "RIGHT": tc += 1
                remaining.discard((tr, tc))
            curr = (tr, tc)
            remaining.discard(curr)

        if final_goal is not None and curr != final_goal and not self._stop_event.is_set():
            prob = PMSearchProblem(curr, final_goal, self.game_map)
            if algo_name == "DFS": searcher = DFS(prob)
            elif algo_name == "BFS": searcher = BFS(prob)
            elif algo_name == "UCS": searcher = UCS(prob)
            elif algo_name == "GREEDY": searcher = Greedy(prob)
            else: searcher = AStar(prob)
            sub_acts = searcher.search()
            if sub_acts is not None:
                all_actions.extend(sub_acts)
                total_nodes += searcher.expanded_count

        time_used = time.time() - t0
        return all_actions, total_nodes, time_used

    def _run_classic_search(self):
        if len(self.goals) == 0 and len(self.foods) == 0:
            self.log("[LỖI] Bản đồ không có Goal (G) hoặc Food (.)!", STATUS_COLORS["ERROR"])
            self.status = "ERROR"
            return

        actions = None
        final_goal = self.goals[0] if len(self.goals) > 0 else None

        if len(self.foods) > 0:
            if len(self.foods) <= 12:
                problem = MultiGoal(self.spawn, tuple(self.foods), self.game_map, goal=final_goal)
                if self.algorithm == "DFS": searcher = DFS(problem)
                elif self.algorithm == "BFS": searcher = BFS(problem)
                elif self.algorithm == "UCS": searcher = UCS(problem)
                elif self.algorithm == "GREEDY": searcher = Greedy(problem)
                else: searcher = AStar(problem)

                self.log(f"Đang tính toán gom hết {len(self.foods)} thức ăn với {self.algorithm}...", TEXT_MUTED)
                actions = searcher.search()
                self.expanded_count = searcher.expanded_count
                self.time_used = searcher.time_used
                if actions is not None:
                    self.path_cost = problem.measure_path_cost(actions)
            else:
                self.log(f"Đang lập kế hoạch gom sạch {len(self.foods)} thức ăn với {self.algorithm}...", TEXT_MUTED)
                actions, self.expanded_count, self.time_used = self._plan_multi_food_tour(self.algorithm, final_goal=final_goal)
                self.path_cost = len(actions) if actions is not None else None

        elif len(self.goals) > 1:
            problem = MultiGoal(self.spawn, tuple(self.goals), self.game_map, goal=None)
            if self.algorithm == "DFS": searcher = DFS(problem)
            elif self.algorithm == "BFS": searcher = BFS(problem)
            elif self.algorithm == "UCS": searcher = UCS(problem)
            elif self.algorithm == "GREEDY": searcher = Greedy(problem)
            else: searcher = AStar(problem)

            self.log(f"Đang tính toán đi qua {len(self.goals)} Goal với {self.algorithm}...", TEXT_MUTED)
            actions = searcher.search()
            self.expanded_count = searcher.expanded_count
            self.time_used = searcher.time_used
            if actions is not None:
                self.path_cost = problem.measure_path_cost(actions)

        else:
            problem = PMSearchProblem(self.spawn, self.goals[0], self.game_map)
            if self.algorithm == "DFS": searcher = DFS(problem)
            elif self.algorithm == "BFS": searcher = BFS(problem)
            elif self.algorithm == "UCS": searcher = UCS(problem)
            elif self.algorithm == "GREEDY": searcher = Greedy(problem)
            else: searcher = AStar(problem)

            self.log(f"Đang tính toán đường đi với {self.algorithm}...", TEXT_MUTED)
            actions = searcher.search()
            self.expanded_count = searcher.expanded_count
            self.time_used = searcher.time_used
            if actions is not None:
                self.path_cost = problem.measure_path_cost(actions)

        if actions is None:
            self.path_cost = None
            self.status = "LOSE"
            self.log(">>> KHÔNG TÌM THẤY ĐƯỜNG ĐI HOÀN THÀNH MỤC TIÊU! <<<", STATUS_COLORS["LOSE"])
            return

        self.log(f"Tìm thấy đường đi! Số bước: {len(actions)} | Chi phí: {self.path_cost} | Expanded: {self.expanded_count} | Thời gian: {round(self.time_used, 5)}s", STATUS_COLORS["WIN"])

        curr_r, curr_c = self.spawn
        trail = [(curr_r, curr_c)]
        self.path_trail = trail

        for i, act in enumerate(actions):
            if self._stop_event.is_set():
                return

            while not self._pause_event.is_set():
                if self._stop_event.is_set():
                    return
                if self.is_stepping and self._step_trigger.is_set():
                    self._step_trigger.clear()
                    break
                time.sleep(0.04)

            self.facing_dir = act
            if act == "UP":
                curr_r -= 1
            elif act == "DOWN":
                curr_r += 1
            elif act == "LEFT":
                curr_c -= 1
            elif act == "RIGHT":
                curr_c += 1

            self.pacman_pos = (curr_r, curr_c)
            trail.append((curr_r, curr_c))
            self.path_trail = list(trail)
            self.steps_taken = i + 1

            if (curr_r, curr_c) in self.remaining_foods:
                self.remaining_foods.remove((curr_r, curr_c))
                self.score += 10
                self.log(f"Bước {i+1}: Ăn Food tại {(curr_r, curr_c)} | Điểm: {self.score}", COLOR_PACMAN)
            elif (curr_r, curr_c) in self.remaining_goals:
                self.remaining_goals.remove((curr_r, curr_c))
                self.score += 20
                rem_g_cnt = len(self.remaining_goals)
                self.log(f"Bước {i+1}: Đã thu thập Goal tại {(curr_r, curr_c)} (Còn lại {rem_g_cnt} Goal) | Điểm: {self.score}", (52, 211, 153))
            else:
                self.log(f"Bước {i+1}: Đi {act} -> {(curr_r, curr_c)}", TEXT_BODY)

            delay = max(0.02, 0.25 / max(0.1, self.speed))
            time.sleep(delay)

        self.status = "WIN"
        self.log(">>> CHIẾN THẮNG: PACMAN ĐÃ HOÀN THÀNH MỤC TIÊU! <<<", STATUS_COLORS["WIN"])

    def _find_nearest_food(self, current_pos, foods):
        """
        Tìm viên thức ăn gần nhất theo khoảng cách thực tế trong mê cung bằng BFS.
        """
        if not foods:
            return None
        queue = deque([current_pos])
        visited = {current_pos}
        while queue:
            curr = queue.popleft()
            if curr in foods:
                return curr
            r, c = curr
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(self.game_map) and 0 <= nc < len(self.game_map[nr]):
                    if self.game_map[nr][nc] != "#" and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        return min(foods, key=lambda f: abs(current_pos[0] - f[0]) + abs(current_pos[1] - f[1]))

    def _run_adversarial_search(self):
        if len(self.goals) == 0 and len(self.foods) == 0:
            self.log("[LỖI] Bản đồ cần có ít nhất 1 Goal (G) hoặc Food (.)!", STATUS_COLORS["ERROR"])
            self.status = "ERROR"
            return

        if len(self.remaining_foods) > 0:
            target = self._find_nearest_food(self.spawn, self.remaining_foods)
        elif len(self.remaining_goals) > 0:
            target = self._find_nearest_food(self.spawn, self.remaining_goals)
        else:
            target = None

        if self.adv_mode == "STEP":
            prob = AdvProblem(self.spawn, self.ghosts, target, self.game_map)
            ai = Minimax(prob, self.depth) if self.algorithm == "MINIMAX" else AlphaBeta(prob, self.depth)

            self.log(f"Tính quyết định bước đầu với {self.algorithm} (depth={self.depth})...", TEXT_MUTED)
            action = ai.search()

            self.expanded_count = ai.expanded_count
            self.time_used = ai.time_used
            self.last_value = ai.last_value

            self.log(f"Nước đi tốt nhất: {action} | Eval: {ai.last_value} | Nodes: {ai.expanded_count} | Time: {round(ai.time_used, 5)}s", STATUS_COLORS["WIN"])
            if action:
                self.facing_dir = action
                r, c = self.spawn
                if action == "UP": r -= 1
                elif action == "DOWN": r += 1
                elif action == "LEFT": c -= 1
                elif action == "RIGHT": c += 1
                self.pacman_pos = (r, c)
                self.steps_taken = 1
                self.path_trail = [self.spawn, (r, c)]

                if self.pacman_pos in self.remaining_goals:
                    self.remaining_goals.remove(self.pacman_pos)
                if self.pacman_pos in self.remaining_foods:
                    self.remaining_foods.remove(self.pacman_pos)

            da_het_muc_tieu = len(self.remaining_goals) == 0 and len(self.remaining_foods) == 0
            self.status = "WIN" if (self.pacman_pos == target and da_het_muc_tieu) else "READY"
            return

        state = GameState(self.spawn, self.ghosts.copy(), set(self.foods), 0, self.game_map)
        buoc = 0
        max_steps = max(100, len(self.initial_foods) * 4 if len(self.initial_foods) > 0 else 60)
        huong_nguoc_lai = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}

        self.lich_su_positions = [state.pacman_position]
        self.lich_su_actions = []
        self.path_trail = [state.pacman_position]

        total_nodes = 0
        total_time = 0.0

        while buoc < max_steps:
            if self._stop_event.is_set():
                return

            while not self._pause_event.is_set():
                if self._stop_event.is_set():
                    return
                if self.is_stepping and self._step_trigger.is_set():
                    self._step_trigger.clear()
                    break
                time.sleep(0.04)

            if len(state.food) > 0:
                target = self._find_nearest_food(state.pacman_position, state.food)
            elif len(self.remaining_goals) > 0:
                target = self._find_nearest_food(state.pacman_position, self.remaining_goals)
            else:
                target = None

            if target is None:
                self.status = "WIN"
                self.log(">>> CHIẾN THẮNG: TẤT CẢ MỤC TIÊU ĐÃ HOÀN THÀNH! <<<", STATUS_COLORS["WIN"])
                break

            buoc += 1
            prob = AdvProblem(state.pacman_position, state.ghost_positions, target, self.game_map)
            recent = self.lich_su_positions[-8:]

            ai = Minimax(prob, self.depth, recent_positions=recent) if self.algorithm == "MINIMAX" else AlphaBeta(prob, self.depth, recent_positions=recent)
            act = ai.search()

            total_nodes += ai.expanded_count
            total_time += ai.time_used

            self.expanded_count = total_nodes
            self.time_used = total_time
            self.last_value = ai.last_value

            if act is None:
                self.log(f"Bước {buoc}: Pacman không còn nước đi hợp lệ!", STATUS_COLORS["LOSE"])
                self.status = "LOSE"
                break

            self.facing_dir = act
            self.lich_su_actions.append(act)

            prev_food_count = len(self.remaining_foods)
            is_final = (len(state.food) == 0 and len(self.remaining_goals) <= 1)
            state = state.step(act, target, is_final_goal=is_final)
            if state is None:
                self.status = "ERROR"
                break

            self.lich_su_positions.append(state.pacman_position)
            self.path_trail = list(self.lich_su_positions)
            self.pacman_pos = state.pacman_position
            self.ghost_positions = list(state.ghost_positions)
            self.remaining_foods = set(state.food)
            self.score = state.score
            self.steps_taken = buoc

            self.log(f"Bước {buoc}: Pacman {act} -> {self.pacman_pos} | Eval: {ai.last_value} | Nodes: {ai.expanded_count}", COLOR_PACMAN)
            for gi, gp in enumerate(self.ghost_positions):
                self.log(f"  Ghost {gi} -> {gp}", (38, 198, 218))

            if len(self.remaining_foods) < prev_food_count:
                self.log(f"  Đã ăn Food tại {self.pacman_pos}! Còn lại {len(self.remaining_foods)} Food | Điểm: {self.score}", (254, 240, 138))

            if state.pacman_position in self.remaining_goals:
                self.remaining_goals.remove(state.pacman_position)
                self.score += 20
                self.log(f"  Đã thu thập Goal tại {state.pacman_position}! Còn lại {len(self.remaining_goals)} Goal.", (52, 211, 153))

            if state.status == "LOSE":
                self.status = "LOSE"
                self.log(">>> THUA CUỘC: PACMAN ĐÃ BỊ GHOST BẮT! <<<", STATUS_COLORS["LOSE"])
                break

            da_het_goal = len(self.remaining_goals) == 0
            da_het_food = len(state.food) == 0
            if da_het_goal and da_het_food:
                self.status = "WIN"
                self.log(">>> CHIẾN THẮNG: PACMAN ĐÃ HOÀN THÀNH TẤT CẢ MỤC TIÊU! <<<", STATUS_COLORS["WIN"])
                break
            else:
                state.status = "PLAYING"

            delay = max(0.04, 0.4 / max(0.1, self.speed))
            time.sleep(delay)

        if buoc >= max_steps and self.status == "RUNNING":
            self.status = "PAUSED"
            self.log(f"Đã đạt giới hạn {max_steps} bước mô phỏng.", STATUS_COLORS["PAUSED"])

