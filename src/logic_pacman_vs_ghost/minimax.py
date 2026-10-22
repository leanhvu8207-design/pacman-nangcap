import time

"""
Thuật toán Minimax đối kháng:
Pacman (agent 0) là MAX agent, các Ghost (agent > 0) là MIN agents.
Có tích hợp cơ chế bảo vệ chống treo (Time & Node Budget + Lọc Ghost ngoài tầm ảnh hưởng khi depth >= 4).
"""


class Minimax:
    def __init__(self, problem, depth_limit, recent_positions=None, max_nodes=30000, max_time=0.45):
        self.problem = problem
        self.depth_limit = depth_limit
        self.recent_positions = list(recent_positions) if recent_positions else []
        self.max_nodes = max_nodes
        self.max_time = max_time
        self.expanded_count = 0
        self.last_value = 0
        self.time_used = 0
        self.chosen_action = None
        self._start_time = 0.0

    def search(self):
        self._start_time = time.time()
        self.expanded_count = 0

        start = self.problem.get_start_state()
        best_action = None
        best_value = float("-inf")
        best_dist = float("inf")

        successors = self.problem.get_successors_for_agent(start, 0)
        for next_state, action in successors:
            self.expanded_count += 1
            next_agent = self.problem.get_next_agent(0)

            if next_agent == 0:
                next_depth = self.depth_limit - 1
            else:
                next_depth = self.depth_limit

            value = self._minimax_value(next_state, next_depth, next_agent)

            # Phạt nếu đi vào ô vừa đi qua nhiều lần trong các bước gần đây
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

        self.chosen_action = best_action
        self.last_value = best_value
        self.time_used = time.time() - self._start_time
        return best_action

    def _minimax_value(self, state, depth, agent):
        # Điều kiện dừng: game kết thúc hoặc đã đạt độ sâu tối đa
        if self.problem.is_terminal(state) or depth <= 0:
            return self.problem.evaluate(state, depth)

        # Cơ chế bảo vệ chống đơ UI khi người dùng chọn depth lớn (>= 4) trên map nhiều Ghost
        if self.depth_limit >= 4 and self.expanded_count >= self.max_nodes:
            return self.problem.evaluate(state, depth)
        if self.depth_limit >= 4 and (self.expanded_count & 255) == 0:
            if time.time() - self._start_time >= self.max_time:
                return self.problem.evaluate(state, depth)

        next_agent = self.problem.get_next_agent(agent)
        next_depth = (depth - 1) if next_agent == 0 else depth

        # Lượt của Pacman (MAX node)
        if agent == 0:
            best = float("-inf")
            successors = self.problem.get_successors_for_agent(state, agent)
            if not successors:
                return self.problem.evaluate(state, depth)
            for next_state, _action in successors:
                self.expanded_count += 1
                value = self._minimax_value(next_state, next_depth, next_agent)
                if value > best:
                    best = value
            return best

        # Lượt của Ghost (MIN node)
        # Khi depth_limit >= 4, nếu Ghost ở quá xa ngoài bán kính tương tác thì chỉ xét nước đi truy đuổi tốt nhất
        if self.depth_limit >= 4 and hasattr(self.problem, "get_ordered_successors"):
            ghost_idx = agent - 1
            g_pos = state.ghost_positions[ghost_idx]
            dist_to_pac = self.problem.get_maze_distance(state.pacman_position, g_pos)
            if dist_to_pac > depth * 2 + 2:
                ordered = self.problem.get_ordered_successors(state, agent)
                if ordered:
                    self.expanded_count += 1
                    return self._minimax_value(ordered[0][0], next_depth, next_agent)

        best = float("inf")
        successors = self.problem.get_successors_for_agent(state, agent)
        if not successors:
            return self.problem.evaluate(state, depth)
        for next_state, _action in successors:
            self.expanded_count += 1
            value = self._minimax_value(next_state, next_depth, next_agent)
            if value < best:
                best = value
        return best
