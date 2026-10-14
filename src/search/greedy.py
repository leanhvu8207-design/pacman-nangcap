import time
import heapq

"""
Mở rộng node có giá trị hàm heuristic h(n) nhỏ nhất (ước lượng gần đích nhất).
"""

class Greedy:
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
        h_n = self.problem.heuristic(start)
        heapq.heappush(queue, (h_n, counter, start, []))
        visited = set()

        while len(queue) > 0:
            h_n, _, state, actions = heapq.heappop(queue)

            if state in visited:
                continue

            visited.add(state)
            self.expanded_count += 1

            if self.problem.reached_target(state):
                self.time_used = time.time() - start_time
                return actions

            successors = self.problem.expand_pacman_moves(state)

            for new_state, next_act, move_cost in successors:
                new_h_n = self.problem.heuristic(new_state)
                new_actions = actions + [next_act]
                counter += 1
                heapq.heappush(queue, (new_h_n, counter, new_state, new_actions))

        self.time_used = time.time() - start_time
        return None