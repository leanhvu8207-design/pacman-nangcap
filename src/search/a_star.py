import heapq
class AStar: # Ktra f(n) = g(n) [Từ start -> n] + h(n) [Từ n -> Goal] 
    def __init__(self,problem):
        self.problem = problem
        
    def search(self):
        start = self.problem.get_pacman_spawn()
        queue = []
        
        g_n = 0
        counter = 0
        h_n = self.problem.heuristic(start)
        f_n = g_n + h_n
        
        heapq.heappush(queue,(f_n,counter,g_n,start,[]))
        visited = set()
        while queue:
            f_n,_, g_n,state,actions = heapq.heappop(queue)
            if state in visited:
                continue 
            visited.add(state)
            
            if self.problem.reached_target(state):
                return actions
            
            successors = self.problem.expand_pacman_moves(state)
            
            for next_state,next_action,move_cost in successors:
                new_g_n = g_n +move_cost
                new_h_n = self.problem.heuristic(next_state)
                new_f_n = new_g_n + new_h_n
                counter += 1
                
                new_actions = actions + [next_action]
                heapq.heappush(
                    queue,
                    (new_f_n,counter,new_g_n,next_state,new_actions)
                )
                
                
        return None
        