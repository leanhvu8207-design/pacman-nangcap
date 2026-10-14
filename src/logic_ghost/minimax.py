"""Thuật toán Minimax giới hạn độ sâu cho bài toán đối kháng."""

import time


class Minimax:
    def __init__(self, problem, depth_limit, recent_positions=None):
        self.problem = problem
        self.depth_limit = depth_limit

        if recent_positions is not None:
            self.recent_positions = list(recent_positions)
        else:
            self.recent_positions = []

        self.expanded_count = 0
        self.last_value = 0
        self.time_used = 0.0
        self.chosen_action = None

    def search(self):
        start_time = time.time()
        self.expanded_count = 0

        start_state = self.problem.get_start_state()
        best_action = None
        best_value = float('-inf')
        best_dist_to_goal = float('inf')

        successors = self.problem.get_successors_for_agent(start_state, 0)

        for successor in successors:
            next_state = successor[0]
            action = successor[1]
            self.expanded_count = self.expanded_count + 1

            next_agent = self.problem.get_next_agent(0)
            if next_agent == 0:
                next_depth = self.depth_limit - 1
            else:
                next_depth = self.depth_limit

            branch_value = self._minimax_value(next_state, next_depth, next_agent)

            revisit_penalty = 0
            if next_state.pacman_position in self.recent_positions:
                repeat_count = self.recent_positions.count(next_state.pacman_position)
                revisit_penalty = repeat_count * 150

            adjusted_value = branch_value - revisit_penalty

            if hasattr(self.problem, 'goal_distance_map'):
                dist_to_goal = self.problem.goal_distance_map.get(next_state.pacman_position, 999)
            else:
                dist_to_goal = 999

            is_strictly_better = (adjusted_value > best_value)
            is_equal_but_closer = (adjusted_value == best_value and dist_to_goal < best_dist_to_goal)

            if is_strictly_better or is_equal_but_closer:
                best_value = adjusted_value
                best_action = action
                best_dist_to_goal = dist_to_goal

        end_time = time.time()
        self.chosen_action = best_action
        self.last_value = best_value
        self.time_used = end_time - start_time
        return best_action

    def _minimax_value(self, state, depth, agent):
        is_game_over = self.problem.is_terminal(state)
        is_depth_limit_reached = (depth <= 0)

        if is_game_over or is_depth_limit_reached:
            heuristic_eval = self.problem.evaluate(state, depth)
            return heuristic_eval

        if agent == 0:
            max_value = float('-inf')
            successors = self.problem.get_successors_for_agent(state, agent)

            for successor in successors:
                next_state = successor[0]
                _action = successor[1]
                self.expanded_count = self.expanded_count + 1

                next_agent = self.problem.get_next_agent(agent)
                if next_agent == 0:
                    next_depth = depth - 1
                else:
                    next_depth = depth

                sub_value = self._minimax_value(next_state, next_depth, next_agent)
                if sub_value > max_value:
                    max_value = sub_value

            return max_value

        min_value = float('inf')
        successors = self.problem.get_successors_for_agent(state, agent)

        for successor in successors:
            next_state = successor[0]
            _action = successor[1]
            self.expanded_count = self.expanded_count + 1

            next_agent = self.problem.get_next_agent(agent)
            if next_agent == 0:
                next_depth = depth - 1
            else:
                next_depth = depth

            sub_value = self._minimax_value(next_state, next_depth, next_agent)
            if sub_value < min_value:
                min_value = sub_value

        return min_value
