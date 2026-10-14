"""Thuật toán A* tìm đường đi ngắn nhất kết hợp chi phí thực tế và heuristic."""

import time
import heapq


class AStar:
    def __init__(self, problem):
        self.problem = problem
        self.expanded_count = 0
        self.time_used = 0.0

    def search(self):
        start_time = time.time()
        self.expanded_count = 0

        start_state = self.problem.get_pacman_spawn()
        initial_g = 0
        initial_h = self.problem.heuristic(start_state)
        initial_f = initial_g + initial_h

        priority_queue = []
        counter = 0
        initial_element = (initial_f, counter, initial_g, start_state, [])
        heapq.heappush(priority_queue, initial_element)

        visited = set()

        while len(priority_queue) > 0:
            current_element = heapq.heappop(priority_queue)
            current_f = current_element[0]
            _entry_index = current_element[1]
            current_g = current_element[2]
            current_state = current_element[3]
            current_actions = current_element[4]

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
                move_cost = successor[2]

                new_g = current_g + move_cost
                new_h = self.problem.heuristic(next_state)
                new_f = new_g + new_h

                new_actions = list(current_actions)
                new_actions.append(next_action)

                counter = counter + 1
                next_element = (new_f, counter, new_g, next_state, new_actions)
                heapq.heappush(priority_queue, next_element)

        end_time = time.time()
        self.time_used = end_time - start_time
        return None
