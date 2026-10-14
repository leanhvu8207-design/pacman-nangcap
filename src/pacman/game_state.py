from src.ghost.ghost import Ghost


class GameState:
    def __init__(self,pacman_position,ghost_positions,food,score,game_map,status="PLAYING"):
        self.pacman_position = pacman_position
        self.ghost_positions = ghost_positions
        self.food = food
        self.score = score
        self.game_map = game_map
        self.status = status
    
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
    
    def move(self, action):
        r, c = self.pacman_position
        if action == "UP":
            r -= 1
        elif action == "DOWN":
            r += 1
        elif action == "LEFT":
            c -= 1
        elif action == "RIGHT":
            c += 1
        new_position = (r, c)
        if self.check_valid_position(new_position) == False:
            return None
        new_food = self.food.copy()
        new_score = self.score
        
        if new_position in new_food:
            new_food.remove(new_position)
            new_score += 10
            
        return GameState(new_position,self.ghost_positions,new_food,
                        new_score,self.game_map)
    
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
        
    
    def move_ghost(self,ghost_index,action):
        ghost = Ghost(self.ghost_positions[ghost_index])
        new_position = ghost.get_next_position(action,self.game_map)
        if new_position is None:
            return None
        
        new_ghost_positions = self.ghost_positions.copy()
        new_ghost_positions[ghost_index] = new_position
        
        return GameState(
            self.pacman_position,
            new_ghost_positions,
            self.food,
            self.score,
            self.game_map
        )
        
    def get_pacman_successors(self):
        successors = []
        actions = ["UP", "DOWN", "LEFT", "RIGHT"]

        for action in actions:
            next_state = self.move(action)

            if next_state is not None:
                successors.append((next_state, action))

        return successors
    
    def get_ghost_successors(self,ghost_index):
        successors = []
        ghost = Ghost(self.ghost_positions[ghost_index])
        valid_actions = ghost.get_valid_actions(self.game_map)
        
        for action in valid_actions:
            next_state = self.move_ghost(ghost_index,action)
            
            if next_state is not None:
                successors.append((next_state,action))
                
        return successors
    
    
    """
    Check Pacman & Ghost ở next_state
    1) Ko có gì xảy ra => state mới đc thêm vào 
    2) Vachạm =>  dừng
    """
    
    def check_pacman_caught(self):
        return self.pacman_position in self.ghost_positions
    
    def step(self, pacman_action, target, is_final_goal=False):
        next_state = self.move(pacman_action)
        if next_state is None:
            return None

        # Pacman va chạm Ghost ngay sau khi di chuyển
        if next_state.pacman_position in next_state.ghost_positions:
            next_state.status = "LOSE"
            return next_state

        # Pacman tới đích cuối cùng (khi đã hoàn thành hết food hoặc được chỉ định là final goal)
        if next_state.pacman_position == target and (is_final_goal or len(next_state.food) == 0):
            next_state.status = "WIN"
            return next_state

        # Cho từng Ghost di chuyển
        for ghost_index in range(len(next_state.ghost_positions)):
            ghost = Ghost(next_state.ghost_positions[ghost_index])
            other_ghosts = [
                pos for idx, pos in enumerate(next_state.ghost_positions) if idx != ghost_index
            ]

            ghost_action = ghost.choose_action(
                next_state.game_map,
                next_state.pacman_position,
                other_ghost_positions=other_ghosts
            )
            if ghost_action is None:
                continue
            next_state = next_state.move_ghost(
                ghost_index,
                ghost_action
            )
            if next_state is None:
                return None

            # Ghost bắt được Pacman
            if next_state.pacman_position in next_state.ghost_positions:
                next_state.status = "LOSE"
                return next_state
        return next_state