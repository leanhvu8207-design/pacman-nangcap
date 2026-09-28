class GameState:
    def __init__(self, pacman_position, ghost_positions, food, score, game_map  ):
        self.pacman_position = pacman_position
        self.ghost_positions = ghost_positions
        self.food = food
        self.score = score
        self.game_map = game_map
        
    """
    Tạo 1 state mới để lưu vị trí mới
    """
        
    def copy_pacman_position(self, new_position):
        return GameState(new_position,self.ghost_positions,
                        self.food,self.score,self.game_map)
    
    """
    def check_valid_position
    Lưu vị trí hiện tại có hợp lệ không, có trùng với tường hay ko.
    """
    
    def check_valid_position(self, position):
        r, c = position
        if r < 0 or r >= len(self.game_map):
            return False
        if c < 0 or c >= len(self.game_map[r]):
            return False
        if self.game_map[r][c] == "#":
            return False
        return True
    
    """
    State mới theo action kết hợp với check trên để đưa ra quyết định
    1) Tạo 1 state mới nếu nếu check = True
    2) Để im state cũ ko cập nhật gì mới 
    """
    
    def move(self,action):
        r,c = self.pacman_position
        if action == "UP":
            r -= 1
        elif action == "DOWN":
            r += 1
        elif action == "LEFT":
            c -= 1
        elif action == "RIGHT":
            c += 1
        
        new_position = (r,c)
        if self.check_valid_position(new_position) == False:
            return None
        
        new_food = self.food.copy()
        if new_position in new_food:
            new_food.remove(new_position)
            
        return GameState(new_position,self.ghost_positions,
                        new_food,self.score,self.game_map)
    
    """
    Check 2 trạng thái có trùng nhau ko => phục vụ Search không bị rơi vào vòng lặp
    """
    
    
    def __eq__(self, other):
        if isinstance(other,GameState) == False:
            return False
        return(
            self.pacman_position == other.pacman_position
            and self.ghost_positions == other.ghost_positions
            and self.food == other.food
            and self.score == other.score
        )
    
    """
    Tạo mã cho vistied check nhanh = set
    """
    def __hash__(self):
        return hash((
            self.pacman_position,
            tuple(self.ghost_positions),
            frozenset(self.food),
            self.score
        ))