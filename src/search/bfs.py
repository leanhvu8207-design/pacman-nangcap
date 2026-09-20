from collections import deque
from .pm_search_problem import PMSearchProblem

class BFS:
    def __init__(self,problem: PMSearchProblem):
        self.problem = problem
        
    def search(self):
        start = self.problem.get_pacman_spawn()
        queue = deque()
        queue.append((start,[]))
        visited = set()
        visited.add(start)
        
        while queue:
            state, actions = queue.popleft()
            if self.problem.reached_target(state):
                return actions
            
            successors = self.problem.expand_pacman_moves(state)
            
            for next_state, next_action, cost in successors:
                if next_state in visited:
                    continue
                
                visited.add(next_state)
                new_action = actions + [next_action]
                queue.append((next_state,new_action))
            
        return None 
        