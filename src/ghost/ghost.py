from collections import deque


class Ghost:
    def __init__(self, position):
        self.position = position

    def get_next_position(self, action, game_map):
        r, c = self.position
        if action == "UP":
            r -= 1
        elif action == "DOWN":
            r += 1
        elif action == "LEFT":
            c -= 1
        elif action == "RIGHT":
            c += 1

        new_position = (r, c)
        if r < 0 or r >= len(game_map):
            return None
        if c < 0 or c >= len(game_map[r]):
            return None
        if game_map[r][c] == "#":
            return None

        return new_position

    def get_valid_actions(self, game_map):
        actions = ["UP", "DOWN", "RIGHT", "LEFT"]
        valid_actions = []

        for action in actions:
            next_position = self.get_next_position(action, game_map)
            if next_position is not None:
                valid_actions.append(action)

        return valid_actions

    def choose_action(self, game_map, pacman_position, other_ghost_positions=None):
        """
        Tìm nước đi thông minh để dí theo Pacman:
        - Sử dụng thuật toán BFS tìm đường đi ngắn nhất thực tế trong mê cung tới Pacman.
        - Tránh hoàn toàn hiện tượng dao động lặp chu kỳ do bị tường cản.
        - Tránh đè lên vị trí của các Ghost khác (Ghost Collision Avoidance), giúp ma không bị nhập vào nhau.
        """
        valid_actions = self.get_valid_actions(game_map)
        if not valid_actions:
            return None

        if self.position == pacman_position:
            return None

        other_ghosts = set(other_ghost_positions) if other_ghost_positions else set()

        # Lọc các hành động an toàn không đi vào ô của Ghost khác
        safe_actions = [
            act for act in valid_actions
            if self.get_next_position(act, game_map) not in other_ghosts
        ]
        # Nếu bị quây kín không có lối đi an toàn nào thì dùng valid_actions
        candidate_actions = safe_actions if safe_actions else valid_actions

        # 1. Tìm đường đi ngắn nhất bằng BFS tới Pacman (coi các Ghost khác là vật cản tạm thời)
        queue = deque([(self.position, None)])
        visited = {self.position} | other_ghosts
        first_step_to_target = None

        directions = [("UP", (-1, 0)), ("DOWN", (1, 0)), ("LEFT", (0, -1)), ("RIGHT", (0, 1))]

        while queue:
            curr_pos, first_act = queue.popleft()
            if curr_pos == pacman_position:
                first_step_to_target = first_act
                break

            for act, (dr, dc) in directions:
                nr = curr_pos[0] + dr
                nc = curr_pos[1] + dc
                if 0 <= nr < len(game_map) and 0 <= nc < len(game_map[nr]):
                    if game_map[nr][nc] != "#" and ((nr, nc) not in visited or (nr, nc) == pacman_position):
                        visited.add((nr, nc))
                        next_first_act = first_act if first_act is not None else act
                        queue.append(((nr, nc), next_first_act))

        if first_step_to_target is not None and first_step_to_target in candidate_actions:
            return first_step_to_target

        # 2. Nếu không tìm được đường né Ghost, thử BFS thông thường nhưng ưu tiên bước đầu không đè lên Ghost khác
        queue2 = deque([(self.position, None)])
        visited2 = {self.position}
        while queue2:
            curr_pos, first_act = queue2.popleft()
            if curr_pos == pacman_position:
                if first_act in candidate_actions:
                    return first_act
                break
            for act, (dr, dc) in directions:
                nr = curr_pos[0] + dr
                nc = curr_pos[1] + dc
                if 0 <= nr < len(game_map) and 0 <= nc < len(game_map[nr]):
                    if game_map[nr][nc] != "#" and (nr, nc) not in visited2:
                        visited2.add((nr, nc))
                        next_first_act = first_act if first_act is not None else act
                        queue2.append(((nr, nc), next_first_act))

        # 3. Fallback: chọn hành động có cự ly Manhattan nhỏ nhất tới Pacman trong danh sách ứng viên
        best_action = candidate_actions[0]
        best_distance = float("inf")
        for action in candidate_actions:
            next_pos = self.get_next_position(action, game_map)
            dist = abs(next_pos[0] - pacman_position[0]) + abs(next_pos[1] - pacman_position[1])
            if dist < best_distance:
                best_distance = dist
                best_action = action

        return best_action

    def get_distance(self, pacman_position):
        ghost_r, ghost_c = self.position
        pacman_r, pacman_c = pacman_position
        return abs(pacman_r - ghost_r) + abs(pacman_c - ghost_c)
    
    