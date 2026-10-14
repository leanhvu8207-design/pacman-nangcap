"""Tác tử Ghost tìm đường BFS truy đuổi Pacman."""

from collections import deque


class Ghost:
    def __init__(self, position):
        self.position = position

    def get_next_position(self, action, game_map):
        curr_row = self.position[0]
        curr_col = self.position[1]

        if action == 'UP':
            next_row = curr_row - 1
            next_col = curr_col
        elif action == 'DOWN':
            next_row = curr_row + 1
            next_col = curr_col
        elif action == 'LEFT':
            next_row = curr_row
            next_col = curr_col - 1
        elif action == 'RIGHT':
            next_row = curr_row
            next_col = curr_col + 1
        else:
            return None

        if next_row < 0 or next_row >= len(game_map):
            return None
        if next_col < 0 or next_col >= len(game_map[next_row]):
            return None
        if game_map[next_row][next_col] == '#':
            return None

        valid_new_position = (next_row, next_col)
        return valid_new_position

    def get_valid_actions(self, game_map):
        all_actions = ['UP', 'DOWN', 'RIGHT', 'LEFT']
        valid_actions = []

        for action in all_actions:
            next_pos = self.get_next_position(action, game_map)
            if next_pos is not None:
                valid_actions.append(action)

        return valid_actions

    def choose_action(self, game_map, pacman_position, other_ghost_positions=None):
        valid_actions = self.get_valid_actions(game_map)
        if len(valid_actions) == 0:
            return None

        if self.position == pacman_position:
            return valid_actions[0]

        if other_ghost_positions is not None:
            other_ghosts = set(other_ghost_positions)
        else:
            other_ghosts = set()

        safe_actions = []
        for act in valid_actions:
            next_pos = self.get_next_position(act, game_map)
            if next_pos not in other_ghosts:
                safe_actions.append(act)

        if len(safe_actions) > 0:
            candidate_actions = safe_actions
        else:
            candidate_actions = valid_actions

        queue = deque()
        initial_element = (self.position, None)
        queue.append(initial_element)

        visited = set()
        visited.add(self.position)
        for g_pos in other_ghosts:
            visited.add(g_pos)

        first_step_to_target = None
        move_directions = [('UP', -1, 0), ('DOWN', 1, 0), ('LEFT', 0, -1), ('RIGHT', 0, 1)]

        while len(queue) > 0:
            current_item = queue.popleft()
            curr_pos = current_item[0]
            first_action_taken = current_item[1]

            if curr_pos == pacman_position:
                first_step_to_target = first_action_taken
                break

            for direction_name, dr, dc in move_directions:
                next_r = curr_pos[0] + dr
                next_c = curr_pos[1] + dc

                if next_r >= 0 and next_r < len(game_map):
                    if next_c >= 0 and next_c < len(game_map[next_r]):
                        cell_char = game_map[next_r][next_c]
                        neighbor_pos = (next_r, next_c)

                        is_wall = (cell_char == '#')
                        is_unvisited = (neighbor_pos not in visited)
                        is_pacman = (neighbor_pos == pacman_position)

                        if not is_wall and (is_unvisited or is_pacman):
                            visited.add(neighbor_pos)

                            if first_action_taken is not None:
                                next_first_action = first_action_taken
                            else:
                                next_first_action = direction_name

                            queue.append((neighbor_pos, next_first_action))

        if first_step_to_target is not None:
            if first_step_to_target in candidate_actions:
                return first_step_to_target

        queue_fallback = deque()
        queue_fallback.append((self.position, None))

        visited_fallback = set()
        visited_fallback.add(self.position)

        while len(queue_fallback) > 0:
            current_item = queue_fallback.popleft()
            curr_pos = current_item[0]
            first_action_taken = current_item[1]

            if curr_pos == pacman_position:
                if first_action_taken in candidate_actions:
                    return first_action_taken
                break

            for direction_name, dr, dc in move_directions:
                next_r = curr_pos[0] + dr
                next_c = curr_pos[1] + dc

                if next_r >= 0 and next_r < len(game_map):
                    if next_c >= 0 and next_c < len(game_map[next_r]):
                        cell_char = game_map[next_r][next_c]
                        neighbor_pos = (next_r, next_c)

                        if cell_char != '#' and neighbor_pos not in visited_fallback:
                            visited_fallback.add(neighbor_pos)

                            if first_action_taken is not None:
                                next_first_action = first_action_taken
                            else:
                                next_first_action = direction_name

                            queue_fallback.append((neighbor_pos, next_first_action))

        best_action = candidate_actions[0]
        best_distance = float('inf')

        for action in candidate_actions:
            next_pos = self.get_next_position(action, game_map)
            dist_r = abs(next_pos[0] - pacman_position[0])
            dist_c = abs(next_pos[1] - pacman_position[1])
            manhattan_dist = dist_r + dist_c

            if manhattan_dist < best_distance:
                best_distance = manhattan_dist
                best_action = action

        return best_action

    def get_distance(self, pacman_position):
        ghost_r = self.position[0]
        ghost_c = self.position[1]
        pacman_r = pacman_position[0]
        pacman_c = pacman_position[1]
        distance = abs(pacman_r - ghost_r) + abs(pacman_c - ghost_c)
        return distance
