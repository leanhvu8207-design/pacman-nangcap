import time
from collections import deque

class BFS:
    def __init__(self, problem):
        self.problem = problem
        self.expanded_count = 0
        self.time_used = 0

    def search(self):
        start_time = time.time()
        self.expanded_count = 0

        start = self.problem.get_pacman_spawn()
        queue = deque()
        queue.append((start, []))
        visited = set()
        visited.add(start)

        while len(queue) > 0:
            state, actions = queue.popleft()

            if self.problem.reached_target(state):
                self.time_used = time.time() - start_time
                return actions

            self.expanded_count += 1
            successors = self.problem.expand_pacman_moves(state)

            for next_state, next_action, cost in successors:
                if next_state in visited:
                    continue

                visited.add(next_state)
                new_action = actions + [next_action]
                queue.append((next_state, new_action))

        self.time_used = time.time() - start_time
        return None
