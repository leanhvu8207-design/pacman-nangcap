import heapq
#Khác A*, chỉ quan tâm tới h(n) ko quan tâm tới g(n)
class Greedy:
    def __init__(self,problem):
        self.problem = problem
        
    def search(self):
        start = self.problem.get_pacman_spawn()
        
        queue = []
        counter = 0
        h_n = self.problem.heuristic(start)
        heapq.heappush(queue,(h_n,counter,start,[]))
        visited = set()
        
        while queue:
            h_n,_,state,actions = heapq.heappop(queue)
            
            if state in visited:
                continue
            visited.add(state)
            if self.problem.reached_target(state):
                return actions
            
            successors = self.problem.expand_pacman_moves(state)
            
            for new_state, next_act, move_cost in successors:
                new_h_n = self.problem.heuristic(new_state)
                new_actions = actions + [next_act]
                counter += 1
                
                heapq.heappush(queue,(new_h_n,counter,new_state,new_actions))
            
        return None
            
        