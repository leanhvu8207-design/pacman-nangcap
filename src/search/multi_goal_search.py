from src.pacman.game_state import GameState

class MultiGoal:
    
    def __init__(self,spawn, food, game_map):
        self.pacman_spawn = spawn
        self.food = food
        self.game_map = game_map
    
    def get_pacman_spawn(self):
        return GameState(self.pacman_spawn,[],set(self.food),
                        0,self.game_map)
    
    def reached_target(self,state: GameState):
        return len(state.food) == 0
    
    def expand_pacman_moves(self, state: GameState):
        successors = []
        actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        for action in actions:
            next_state = state.move(action)
            if next_state is not None:
                successors.append((next_state, action, 1))
        return successors
    
    def measure_path_cost(self,actions):
        return len(actions)
    
    def heuristic(self,state: GameState):
        if len(state.food) == 0:
            return 0
        
        pm_r, pm_c = state.pacman_position
        distances = []
        
        for food_r, food_c in state.food:
            distance = abs(pm_r-food_r) + abs(pm_c - food_c)
            distances.append(distance)
            
        return max(distances)