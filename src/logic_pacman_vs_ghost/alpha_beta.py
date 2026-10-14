import time

class AlphaBeta:
    """Thuật toán Alpha-Beta Pruning: Cắt tỉa nhánh tìm kiếm cho Minimax."""

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
        alpha = float("-inf")
        beta = float("inf")

        successors = self.problem.get_successors_for_agent(start, 0)
        for next_state, action in successors:
            self.expanded_count += 1
            next_agent = self.problem.get_next_agent(0)
            next_depth = self.depth_limit - 1 if next_agent == 0 else self.depth_limit

            value = self._alpha_beta_value(next_state, next_depth, next_agent, alpha, beta)

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

            if adjusted_val > alpha:
                alpha = adjusted_val - 1e-9

        self.chosen_action = best_action
        self.last_value = best_value
        self.time_used = time.time() - start_time
        return best_action

    def _alpha_beta_value(self, state, depth, agent, alpha, beta):
        if self.problem.is_terminal(state) or depth <= 0:
            return self.problem.evaluate(state, depth)

        if agent == 0:
            best = float("-inf")
            successors = self.problem.get_successors_for_agent(state, agent)
            for next_state, _action in successors:
                self.expanded_count += 1
                next_agent = self.problem.get_next_agent(agent)
                next_depth = depth - 1 if next_agent == 0 else depth
                value = self._alpha_beta_value(next_state, next_depth, next_agent, alpha, beta)

                if value > best:
                    best = value
                if best > alpha:
                    alpha = best
                if beta <= alpha:
                    break
            return best

        best = float("inf")
        successors = self.problem.get_successors_for_agent(state, agent)
        for next_state, _action in successors:
            self.expanded_count += 1
            next_agent = self.problem.get_next_agent(agent)
            next_depth = depth - 1 if next_agent == 0 else depth
            value = self._alpha_beta_value(next_state, next_depth, next_agent, alpha, beta)

            if value < best:
                best = value
            if best < beta:
                beta = best
            if beta <= alpha:
                break
        return best
