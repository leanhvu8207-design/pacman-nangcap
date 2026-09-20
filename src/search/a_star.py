import heapq
from .pm_search_problem import PMSearchProblem
class AStar: # Ktra f(n) = g(n) [Từ start -> n] + h(n) [Từ n -> Goal] 
    def __init__(self,problem: PMSearchProblem):
        self.problem = problem
        
    def heuristic(self,state):
        row, col = state
        target_row, target_col = self.problem.target
        return abs(row-target_row) + abs(col-target_col)  # Khoảng cách ước tính (ko phải thực tế) 
        
    def search(self):
        start = self.problem.get_pacman_spawn()
        queue = []
        
        g_n = 0
        h_n = self.heuristic(start)
        f_n = g_n + h_n
        
        heapq.heappush(queue,(f_n,g_n,start,[]))
        visited = set()
        while queue:
            f_n, g_n,state,actions = heapq.heappop(queue)
            if state in visited:
                continue
            visited.add(state)
            
            if self.problem.reached_target(state):
                return actions
            
            successors = self.problem.expand_pacman_moves(state)
            
            for next_state,next_action,move_cost in successors:
                new_g_n = g_n +move_cost
                new_h_n = self.heuristic(next_state)
                new_f_n = new_g_n + new_h_n
                
                new_actions = actions + [next_action]
                heapq.heappush(
                    queue,
                    (new_f_n,new_g_n,next_state,new_actions)
                )
                
                
        
        