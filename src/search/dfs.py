
class DFS:
    def __init__(self, problem):
        self.problem = problem

    def search(self):
        start = self.problem.get_pacman_spawn()
        stack = [(start, [])]
        visited = set()

        while stack:
            state, actions = stack.pop()
            
            if state in visited:
                continue
            
            visited.add(state)
            
            
            if self.problem.reached_target(state):
                return actions  
            
            successors = self.problem.expand_pacman_moves(state)

            for next_state, next_action, cost in successors:
                new_action = actions + [next_action]  
                stack.append((next_state,new_action))
        return None         
                