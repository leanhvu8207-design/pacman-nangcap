import time

"""
Pacman (agent 0) là MAX agent, các Ghost (agent > 0) là MIN agennts
"""
class Minimax:
    def __init__(self, problem, depth_limit, recent_positions=None):
        self.problem = problem
        self.depth_limit = depth_limit
        self.recent_positions = list(recent_positions) if recent_positions else []
        self.expanded_count = 0
        self.last_value = 0
        self.time_used = 0
        self.chosen_action = None

    def search(self):
        start_time = time.time()
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
        self.time_used = time.time() - start_time
        return best_action

    def _minimax_value(self, state, depth, agent):
        # Điều kiện dừng: game kết thúc hoặc đã đạt độ sâu tối đa
        if self.problem.is_terminal(state):
            return self.problem.evaluate(state, depth)
        if depth <= 0:
            return self.problem.evaluate(state, depth)

        # Lượt của Pacman (MAX node)
        if agent == 0:
            best = float("-inf")
            successors = self.problem.get_successors_for_agent(state, agent)
            for next_state, _action in successors:
                self.expanded_count += 1
                next_agent = self.problem.get_next_agent(agent)
                if next_agent == 0:
                    next_depth = depth - 1
                else:
                    next_depth = depth
                value = self._minimax_value(next_state, next_depth, next_agent)
                if value > best:
                    best = value
            return best

        # Lượt của Ghost (MIN node)
        best = float("inf")
        successors = self.problem.get_successors_for_agent(state, agent)
        for next_state, _action in successors:
            self.expanded_count += 1
            next_agent = self.problem.get_next_agent(agent)
            if next_agent == 0:
                next_depth = depth - 1
            else:
                next_depth = depth
            value = self._minimax_value(next_state, next_depth, next_agent)
            if value < best:
                best = value
        return best
