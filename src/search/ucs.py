import heapq
class UCS:
    def __init__(self,problem):
        self.problem = problem
        
    def search(self):
        start = self.problem.get_pacman_spawn()

        queue = []
        counter = 0
        heapq.heappush(queue, (0, counter, start, []))
        visited = set()
        while queue:
            cost, _, state, actions = heapq.heappop(queue)
            if state in visited:
                continue
            
            visited.add(state)
            if self.problem.reached_target(state):
                return actions
            
            successor = self.problem.expand_pacman_moves(state)
            for next_state, next_action, move_cost in successor:
                new_cost = cost + move_cost
                new_actions = actions + [next_action]
                counter += 1
                heapq.heappush(
                    queue,
                    (new_cost, counter, next_state, new_actions)
                )

        return None
    