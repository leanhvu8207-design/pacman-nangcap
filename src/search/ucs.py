import time
import heapq

class UCS:
    """Tìm kiếm chi phí đồng nhất (Uniform-Cost Search) sử dụng min-heap theo g(n)."""

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

            if self.problem.reached_target(state):
                self.time_used = time.time() - start_time
                return actions

            self.expanded_count += 1
            successors = self.problem.expand_pacman_moves(state)

            for next_state, next_action, move_cost in successors:
                new_cost = cost + move_cost
                new_actions = actions + [next_action]
                counter += 1
                heapq.heappush(queue, (new_cost, counter, next_state, new_actions))

        self.time_used = time.time() - start_time
        return None