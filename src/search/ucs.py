import time
import heapq

"""
Mở rộng node có chi phí đường đi g(n) tích lũy nhỏ nhất bằng hàng đợi ưu tiên (min-heap).
"""

class UCS:
    def __init__(self, problem):
        self.problem = problem
        self.expanded_count = 0
        self.time_used = 0

    def search(self):
        start_time = time.time()
        self.expanded_count = 0

        start = self.problem.get_pacman_spawn()
        queue = []
        counter = 0
        heapq.heappush(queue, (0, counter, start, []))
        visited = set()

        while len(queue) > 0:
            cost, _, state, actions = heapq.heappop(queue)

            if state in visited:
                continue

            visited.add(state)
            self.expanded_count += 1

            if self.problem.reached_target(state):
                self.time_used = time.time() - start_time
                return actions

            successors = self.problem.expand_pacman_moves(state)

            for next_state, next_action, move_cost in successors:
                new_cost = cost + move_cost
                new_actions = actions + [next_action]
                counter += 1
                heapq.heappush(queue, (new_cost, counter, next_state, new_actions))

        self.time_used = time.time() - start_time
        return None