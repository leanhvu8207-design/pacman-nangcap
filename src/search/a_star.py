import time
import heapq
"""
Đánh giá độ ưu tiên node theo hàm f(n) = g(n) + h(n):
"""

class AStar:
    def __init__(self, problem):
        self.problem = problem
        self.expanded_count = 0
        self.time_used = 0

    def search(self):
        start_time = time.time()
        self.expanded_count = 0

        start = self.problem.get_pacman_spawn()
        queue = []

        g_n = 0
        counter = 0
        h_n = self.problem.heuristic(start)
        f_n = g_n + h_n

        heapq.heappush(queue, (f_n, counter, g_n, start, []))
        visited = set()

        while len(queue) > 0:
            f_n, _, g_n, state, actions = heapq.heappop(queue)

            if state in visited:
                continue

            visited.add(state)
            self.expanded_count += 1

            if self.problem.reached_target(state):
                self.time_used = time.time() - start_time
                return actions

            successors = self.problem.expand_pacman_moves(state)

            for next_state, next_action, move_cost in successors:
                new_g_n = g_n + move_cost
                new_h_n = self.problem.heuristic(next_state)
                new_f_n = new_g_n + new_h_n
                counter += 1

                new_actions = actions + [next_action]
                heapq.heappush(queue, (new_f_n, counter, new_g_n, next_state, new_actions))

        self.time_used = time.time() - start_time
        return None