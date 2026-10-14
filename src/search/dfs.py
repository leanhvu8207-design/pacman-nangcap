"""Thuật toán DFS tìm kiếm theo chiều sâu."""

import time


class DFS:
    def __init__(self, problem):
        self.problem = problem
        self.expanded_count = 0
        self.time_used = 0.0

    def search(self):
        start_time = time.time()
        self.expanded_count = 0

        start_state = self.problem.get_pacman_spawn()

        stack = []
        initial_node = (start_state, [])
        stack.append(initial_node)

        visited = set()

        while len(stack) > 0:
            current_element = stack.pop()
            current_state = current_element[0]
            current_actions = current_element[1]

            if current_state in visited:
                continue
            visited.add(current_state)

            if self.problem.reached_target(current_state):
                end_time = time.time()
                self.time_used = end_time - start_time
                return current_actions

            self.expanded_count = self.expanded_count + 1
            successors = self.problem.expand_pacman_moves(current_state)

            for successor in successors:
                next_state = successor[0]
                next_action = successor[1]
                step_cost = successor[2]

                new_actions = list(current_actions)
                new_actions.append(next_action)

                next_node = (next_state, new_actions)
                stack.append(next_node)

        end_time = time.time()
        self.time_used = end_time - start_time
        return None
