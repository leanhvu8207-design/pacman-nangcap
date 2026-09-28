from src.pacman.game_state import GameState
class PMSearchProblem:
    def __init__(self,spawn,target,game_map):
        self.pacman_spawn = spawn
        self.target = target
        self.game_map = game_map

    # state = (row,col) *** Quy ước***
    def get_pacman_spawn(self): # Lấy về địa chỉ của pacman
        return GameState(
            self.pacman_spawn,[],set(),0,self.game_map
        )
    
    def reached_target(self, state: GameState):# Check đã tới target chưa
        return state.pacman_position == self.target
    
    def expand_pacman_moves(self, state):
        successors = []
        actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        
        for action in actions:
            next_state = state.move(action)
            if next_state is not None:
                successors.append((next_state, action, 1))
                
        return successors
    
    def measure_path_cost(self,actions): # Tính chi phí dùng cho USC và A*
        return len(actions)
    
    def heuristic(self, state: GameState):
        row, col = state.pacman_position
        target_row, target_col = self.target
        #Chọn theo manhatan
        return abs(row-target_row) + abs(col-target_col)

