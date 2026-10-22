import time
import heapq
"""
Đánh giá độ ưu tiên node theo hàm f(n) = g(n) + h(n),
kết hợp tie-breaking theo h(n) nhỏ hơn và cắt tỉa đường đi theo best_g.
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

        # Hàng đợi ưu tiên: (f_n, h_n, counter, g_n, state, actions)
        # Khi f_n bằng nhau, ưu tiên node có h_n nhỏ hơn (gần đích hơn)
        heapq.heappush(queue, (f_n, h_n, counter, g_n, start, []))
        visited = set()
        best_g = {start: 0}

        while len(queue) > 0:
            f_n, h_n, _, g_n, state, actions = heapq.heappop(queue)

            if state in visited or g_n > best_g.get(state, float("inf")):
                continue

            visited.add(state)
            self.expanded_count += 1

            if self.problem.reached_target(state):
                self.time_used = time.time() - start_time
                return actions

            successors = self.problem.expand_pacman_moves(state)

            for next_state, next_action, move_cost in successors:
                new_g_n = g_n + move_cost

                if next_state in visited or new_g_n >= best_g.get(next_state, float("inf")):
                    continue

                best_g[next_state] = new_g_n
                new_h_n = self.problem.heuristic(next_state)
                new_f_n = new_g_n + new_h_n
                counter += 1

                new_actions = actions + [next_action]
                heapq.heappush(queue, (new_f_n, new_h_n, counter, new_g_n, next_state, new_actions))

        self.time_used = time.time() - start_time
        return None