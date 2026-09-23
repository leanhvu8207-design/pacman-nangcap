import heapq

class Greedy:
    def __init__(self,problem):
        self.problem = problem
        
    def search(self):
        start = self.problem.get_pacman_spawn()
        
        queue = []
        h_n = self.problem.heuristic(start)
        heapq.heappush(queue,(h_n,start,[]))
        visited = set()
        
        while queue:
            h_n,state,actions = heapq.heappop(queue)
            if state in visited:
                continue
            if self.problem.reached_target(state):
                return actions
            
            successors = self.problem.expand_pacman_moves(state)
            
            for new_state, next_act, move_cost in successors:
                new_h_n = self.problem.heuristic(new_state)
                new_actions = actions + [next_act]
                
                heapq.heappush(queue,(new_h_n,new_state,new_actions))
            
        return None
            
        