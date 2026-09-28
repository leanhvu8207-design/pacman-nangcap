class Ghost:
    def __init__(self,position):
        self.position = position
    
    def get_next_position(self,action,game_map):
        r,c = self.position
        if action == "UP":
            r -= 1
        if action == "DOWN":
            r += 1
        if action == "LEFT":
            c -= 1
        if action == "RIGHT":
            c += 1
            
        new_position = (r,c)
        if r<0 or r>= len(game_map):
            return None
        if c<0 or c>=len(game_map[r]):
            return None
        if game_map[r][c] == "#":
            return None
        
        return new_position
    
    def get_valid_actions(self, game_map):
        actions = ["UP","DOWN","RIGHT","LEFT"]
        valid_actions = []
        
        for action in actions:
            next_position = self.get_next_position(action,game_map)
            
            if next_position is not None:
                valid_actions.append(action)
                
        return valid_actions
    
    def choose_action(self,game_map,pacman_posititon):
        valid_actions = self.get_valid_actions(game_map)
        if not valid_actions:
            return None
        
        best_action = None
        best_distance = float("inf")
        
        for action in valid_actions:
            next_position = self.get_next_position(action, game_map)
            next_ghost = Ghost(next_position)
            distance = next_ghost.get_distance(pacman_posititon)
            
            if distance < best_distance:
                best_distance = distance
                best_action = action
        
        return best_action
    
    def get_distance(self,pacman_position):
        ghost_r, ghost_c = self.position
        pacman_r, pacman_c = pacman_position
        return abs(pacman_r-ghost_r) + abs(pacman_c-ghost_c)