class PMSearchProblem:
    def __init__(self,spawn,target,game_map):
        self.pacman_spawn = spawn
        self.target = target
        self.game_map = game_map

    # state = (row,col) *** Quy ước***
    def get_pacman_spawn(self): # Lấy về địa chỉ của pacman
        return self.pacman_spawn
    
    def reached_target(self,state):# Check đã tới target chưa
        return state == self.target
    
    def expand_pacman_moves(self,state): # Mở rộng hướng đi theo 4 hướng
        successor = []
        row, col = state
        move = {"UP":(-1,0),
                "DOWN":(1,0),
                "LEFT":(0,-1),
                "RIGHT":(0,1)
                }
        for next_act,(dr,dc) in move.items():
                next_row = row + dr
                next_col = col + dc
                
                if next_row < 0 or next_row >= len(self.game_map):
                    continue
                
                if next_col < 0 or next_col >= len(self.game_map[next_row]):
                    continue
                
                if self.game_map[next_row][next_col] == "#":
                    continue
                
                next_state = (next_row,next_col)
                
                successor.append((next_state,next_act,1))
        
        return  successor
    
    def measure_path_cost(self,actions): # Tính chi phí dùng cho USC và A*
        return len(actions)
    
    def heuristic(self,state):
        row, col = state
        target_row, target_col = self.target
        return abs(row-target_row) + abs(col-target_col)  # Khoảng cách ước tính (ko phải thực tế) -> hg tiên theo hg đó

