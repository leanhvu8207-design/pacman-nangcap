import heapq
from .pm_search_problem import PMSearchProblem

class UCS:
    def __init__(self,problem: PMSearchProblem):
        self.problem = problem
        
    def search(self):
        start = self.problem.get_pacman_spawn()
        
        queue = []
        heapq.heappush(queue,(0,start,[]))
        
        visited = set()
        while queue:
            cost, state, actions = heapq.heappop(queue)
            
            if state in visited:
                continue
                
            visited.add(state)
            
            if self.problem.reached_target(state):
                return actions
            
            successor = self.problem.expand_pacman_moves(state)
            
            for next_state, next_action, move_cost in successor:
                new_cost = cost + move_cost
                new_actions = actions + [next_action]
                
                heapq.heappush(
                    queue,
                    (new_cost,next_state,new_actions)
                )
                