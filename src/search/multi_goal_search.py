class MultiGoal: 
    def __init__(self,spawn, food, game_map):
        self.pacman_spawn = spawn
        self.food = food
        self.game_map = game_map
        
    # state = (spawn,post_food)
    
    def get_pacman_spawn(self):
        return (self.pacman_spawn,self.food)
    
    def reached_target(self,state):
        pacman_position, remaining_food = state
        return len(remaining_food) == 0
    
    def expand_pacman_moves(self,state):
        successors = []
        pacman_position, remaining_food = state
        row, col = pacman_position
        
        move = {
            "UP":(-1,0),
            "DOWN":(1,0),
            "LEFT":(0,-1),
            "RIGHT":(0,1)
        }
        
        for next_act,(dr,dc) in move.items():
            next_row = row + dr
            next_col = col + dc
            
            if next_row < 0 or next_row>=len(self.game_map):
                continue
            
            if next_col<0 or next_col >=len(self.game_map[next_row]):
                continue
            
            if self.game_map[next_row][next_col] == "#":
                continue
            
            next_position = (next_row,next_col)
            if next_position in remaining_food:
                next_food = list(remaining_food)
                next_food.remove(next_position)
                next_food = tuple(next_food)
                
            else: 
                next_food = remaining_food
                
            next_state = (next_position,next_food)
            successors.append((next_state,next_act,1))
        
        return successors
    
    def measure_path_cost(self,actions):
        return len(actions)
    
    def heuristic(self,state):
        pacman_position, remaining_food = state
        if len(remaining_food) == 0:
            return 0
        pacman_row, pacman_col = pacman_position
        
        distances = []
        for food_row, food_col in remaining_food:
            distance = abs(pacman_row - food_row) + abs(pacman_col-food_col)
            distances.append(distance)
            
        return max(distances)