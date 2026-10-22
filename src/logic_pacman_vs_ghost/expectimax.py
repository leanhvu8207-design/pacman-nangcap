import time

"""
Thuật toán Expectimax đối kháng nâng cao (Probabilistic Adversarial Search):
- Pacman (agent 0) là nút MAX: chọn hành động tối đa hóa giá trị kỳ vọng.
- Các Ghost (agent > 0) là nút CHANCE (Kỳ vọng xác suất): mô hình hóa Ghost vừa truy đuổi thông minh
  theo khoảng cách mê cung ngắn nhất (trọng số xác suất cao 80%), vừa tính đến khả năng Ghost rẽ hướng
  khác tại ngã giao (20%), giúp Pacman không bị bi quan cực đoan khi bị vây và tìm lối thoát thông minh hơn.
- Tối ưu hóa chống đơ 3 tầng:
  1. Bảng băm trạng thái (Transposition Table - TT) lưu kết quả các thế cờ trùng lặp O(1).
  2. Cắt tỉa Ghost ngoài bán kính đe dọa (Active Threat Horizon Filtering).
  3. Tìm kiếm sâu dần (Iterative Deepening) kết hợp giới hạn thời gian/node an toàn.
"""


class Expectimax:
    def __init__(self, problem, depth_limit, recent_positions=None, chase_prob=0.80, max_nodes=25000, max_time=0.35):
        self.problem = problem
        self.depth_limit = depth_limit
        self.recent_positions = list(recent_positions) if recent_positions else []
        self.chase_prob = chase_prob
        self.max_nodes = max_nodes
        self.max_time = max_time

        self.expanded_count = 0
        self.last_value = 0.0
        self.time_used = 0.0
        self.chosen_action = None
        self._transposition_table = {}
        self._start_time = 0.0
        self._aborted = False

    def search(self):
        self._start_time = time.time()
        self.expanded_count = 0
        self._transposition_table.clear()
        self._aborted = False

        start = self.problem.get_start_state()
        if hasattr(self.problem, "get_ordered_successors"):
            root_successors = self.problem.get_ordered_successors(start, 0)
        else:
            root_successors = self.problem.get_successors_for_agent(start, 0)

        if not root_successors:
            self.time_used = time.time() - self._start_time
            return None

        # Với depth <= 3, chạy trực tiếp ở độ sâu yêu cầu; với depth >= 4, dùng Iterative Deepening để chống đơ
        start_d = 2 if self.depth_limit >= 4 else self.depth_limit
        best_action = root_successors[0][1]
        best_value = float("-inf")

        for current_d in range(start_d, self.depth_limit + 1):
            self._transposition_table.clear()
            iter_best_act, iter_best_val = self._search_at_depth(start, root_successors, current_d)
            if not self._aborted or current_d == start_d:
                best_action = iter_best_act
                best_value = round(iter_best_val, 2)
            if self._aborted:
                break

        self.chosen_action = best_action
        self.last_value = best_value
        self.time_used = time.time() - self._start_time
        return best_action

    def _search_at_depth(self, start, root_successors, depth_target):
        best_action = None
        best_value = float("-inf")
        best_dist = float("inf")
        next_agent = self.problem.get_next_agent(0)
        next_depth = (depth_target - 1) if next_agent == 0 else depth_target

        for next_state, action in root_successors:
            self.expanded_count += 1
            value = self._expectimax_value(next_state, next_depth, next_agent)

            revisit_pen = 0
            if next_state.pacman_position in self.recent_positions:
                count = self.recent_positions.count(next_state.pacman_position)
                revisit_pen = count * 150

            adjusted_val = value - revisit_pen
            dist_to_goal = getattr(self.problem, "goal_distance_map", {}).get(next_state.pacman_position, 999)

            if adjusted_val > best_value or (adjusted_val == best_value and dist_to_goal < best_dist):
                best_value = adjusted_val
                best_action = action
                best_dist = dist_to_goal

            if self._aborted:
                break

        return best_action, best_value

    def _expectimax_value(self, state, depth, agent):
        if self.problem.is_terminal(state) or depth <= 0:
            return float(self.problem.evaluate(state, depth))

        # Kiểm tra giới hạn thời gian / số node khi tìm kiếm sâu để tuyệt đối không gây đơ UI
        if self.depth_limit >= 3 and self.expanded_count >= self.max_nodes:
            self._aborted = True
            return float(self.problem.evaluate(state, depth))
        if self.depth_limit >= 3 and (self.expanded_count & 127) == 0:
            if time.time() - self._start_time >= self.max_time:
                self._aborted = True
                return float(self.problem.evaluate(state, depth))

        # Tra cứu bảng băm trạng thái (Transposition Table) O(1)
        tt_key = (state.pacman_position, tuple(state.ghost_positions), depth, agent)
        if tt_key in self._transposition_table:
            return self._transposition_table[tt_key]

        next_agent = self.problem.get_next_agent(agent)
        next_depth = (depth - 1) if next_agent == 0 else depth

        # 1. Lượt của Pacman (MAX node)
        if agent == 0:
            if hasattr(self.problem, "get_ordered_successors"):
                successors = self.problem.get_ordered_successors(state, 0)
            else:
                successors = self.problem.get_successors_for_agent(state, 0)

            if not successors:
                val = float(self.problem.evaluate(state, depth))
                self._transposition_table[tt_key] = val
                return val

            best = float("-inf")
            for next_state, _action in successors:
                self.expanded_count += 1
                value = self._expectimax_value(next_state, next_depth, next_agent)
                if value > best:
                    best = value
                if self._aborted:
                    break

            self._transposition_table[tt_key] = best
            return best

        # 2. Lượt của Ghost (CHANCE / EXPECTATION node)
        ghost_idx = agent - 1
        g_pos = state.ghost_positions[ghost_idx]
        pac_pos = state.pacman_position
        dist_to_pac = self.problem.get_maze_distance(pac_pos, g_pos)

        if hasattr(self.problem, "get_ordered_successors"):
            successors = self.problem.get_ordered_successors(state, agent)
        else:
            successors = self.problem.get_successors_for_agent(state, agent)

        if not successors:
            val = float(self.problem.evaluate(state, depth))
            self._transposition_table[tt_key] = val
            return val

        # Tối ưu hóa Active Threat Horizon:
        # Nếu Ghost ở xa ngoài bán kính có thể chạm tới Pacman trong số bước còn lại (hoặc chỉ có 1 nước đi),
        # cho Ghost đi thẳng theo hướng ngắn nhất về phía Pacman để tránh bùng nổ tổ hợp vô ích.
        if len(successors) == 1 or dist_to_pac > depth * 2 + 2:
            self.expanded_count += 1
            val = self._expectimax_value(successors[0][0], next_depth, next_agent)
            self._transposition_table[tt_key] = val
            return val

        # Tính phân phối xác suất cho các nước đi của Ghost:
        # Các nước đi rút ngắn khoảng cách mê cung tới Pacman nhất nhận tổng xác suất `chase_prob` (80%),
        # các nước đi còn lại chia đều `1 - chase_prob` (20%).
        pac_dist_map = self.problem.get_distance_map(pac_pos)
        dists = [pac_dist_map.get(s[0].ghost_positions[ghost_idx], 999) for s in successors]
        min_d = min(dists)

        best_indices = [i for i, d in enumerate(dists) if d == min_d]
        other_indices = [i for i, d in enumerate(dists) if d > min_d]

        n_best = len(best_indices)
        n_other = len(other_indices)

        expected_value = 0.0
        for idx, (next_state, _action) in enumerate(successors):
            if n_other == 0:
                prob = 1.0 / n_best
            elif idx in best_indices:
                prob = self.chase_prob / n_best
            else:
                prob = (1.0 - self.chase_prob) / n_other

            self.expanded_count += 1
            val = self._expectimax_value(next_state, next_depth, next_agent)
            expected_value += prob * val
            if self._aborted:
                break

        self._transposition_table[tt_key] = expected_value
        return expected_value
