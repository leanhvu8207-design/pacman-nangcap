"""Thuật toán BFS tìm đường đi ngắn nhất."""

import time
from collections import deque


class BFS:
    def __init__(self, problem):
        self.problem = problem
        self.expanded_count = 0
        self.time_used = 0.0

    def search(self):
        start_time = time.time()
        self.expanded_count = 0

        start_state = self.problem.get_pacman_spawn()

        queue = deque()
        initial_node = (start_state, [])
        queue.append(initial_node)

        visited = set()
        visited.add(start_state)

        while len(queue) > 0:
            current_element = queue.popleft()
            current_state = current_element[0]
            current_actions = current_element[1]

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

                if next_state in visited:
                    continue

                visited.add(next_state)

                new_actions = list(current_actions)
                new_actions.append(next_action)

                next_node = (next_state, new_actions)
                queue.append(next_node)

        end_time = time.time()
        self.time_used = end_time - start_time
        return None
