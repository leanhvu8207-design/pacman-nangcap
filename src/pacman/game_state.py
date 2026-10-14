"""Biểu diễn trạng thái bàn cờ Pacman và luật chuyển trạng thái."""

from src.ghost.ghost import Ghost


class GameState:
    def __init__(self, pacman_position, ghost_positions, food, score, game_map, status='PLAYING'):
        self.pacman_position = pacman_position
        self.ghost_positions = list(ghost_positions)
        self.food = set(food)
        self.score = score
        self.game_map = game_map
        self.status = status

    def copy_pacman_position(self, new_position):
        cloned_ghosts = list(self.ghost_positions)
        cloned_food = self.food.copy()
        new_state = GameState(new_position, cloned_ghosts, cloned_food, self.score, self.game_map)
        return new_state

    def check_valid_position(self, position):
        r = position[0]
        c = position[1]

        if r < 0 or r >= len(self.game_map):
            return False
        if c < 0 or c >= len(self.game_map[r]):
            return False

        cell_character = self.game_map[r][c]
        if cell_character == '#':
            return False

        return True

    def move(self, action):
        curr_r = self.pacman_position[0]
        curr_c = self.pacman_position[1]

        if action == 'UP':
            next_r = curr_r - 1
            next_c = curr_c
        elif action == 'DOWN':
            next_r = curr_r + 1
            next_c = curr_c
        elif action == 'LEFT':
            next_r = curr_r
            next_c = curr_c - 1
        elif action == 'RIGHT':
            next_r = curr_r
            next_c = curr_c + 1
        else:
            return None

        new_position = (next_r, next_c)
        if not self.check_valid_position(new_position):
            return None

        new_food = self.food.copy()
        new_score = self.score

        if new_position in new_food:
            new_food.remove(new_position)
            new_score = new_score + 10

        cloned_ghosts = list(self.ghost_positions)
        next_state = GameState(new_position, cloned_ghosts, new_food, new_score, self.game_map)
        return next_state

    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False

        is_same_pacman = (self.pacman_position == other.pacman_position)
        is_same_ghosts = (self.ghost_positions == other.ghost_positions)
        is_same_food = (self.food == other.food)
        return is_same_pacman and is_same_ghosts and is_same_food

    def __hash__(self):
        ghosts_tuple = tuple(self.ghost_positions)
        food_frozen = frozenset(self.food)
        state_signature = (self.pacman_position, ghosts_tuple, food_frozen)
        return hash(state_signature)

    def move_ghost(self, ghost_index, action):
        ghost_pos = self.ghost_positions[ghost_index]
        ghost_agent = Ghost(ghost_pos)
        new_ghost_pos = ghost_agent.get_next_position(action, self.game_map)

        if new_ghost_pos is None:
            return None

        new_ghost_positions = list(self.ghost_positions)
        new_ghost_positions[ghost_index] = new_ghost_pos
        cloned_food = self.food.copy()

        new_state = GameState(self.pacman_position, new_ghost_positions, cloned_food, self.score, self.game_map)
        return new_state

    def get_pacman_successors(self):
        successors = []
        possible_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']

        for action in possible_actions:
            next_state = self.move(action)
            if next_state is not None:
                successors.append((next_state, action))

        return successors

    def get_ghost_successors(self, ghost_index):
        successors = []
        ghost_pos = self.ghost_positions[ghost_index]
        ghost_agent = Ghost(ghost_pos)
        valid_actions = ghost_agent.get_valid_actions(self.game_map)

        for action in valid_actions:
            next_state = self.move_ghost(ghost_index, action)
            if next_state is not None:
                successors.append((next_state, action))

        return successors

    def check_pacman_caught(self):
        is_caught = (self.pacman_position in self.ghost_positions)
        return is_caught

    def step(self, pacman_action, target, is_final_goal=False):
        next_state = self.move(pacman_action)
        if next_state is None:
            return None

        if next_state.pacman_position in next_state.ghost_positions:
            next_state.status = 'LOSE'
            return next_state

        is_at_target = (next_state.pacman_position == target)
        is_food_cleared = (len(next_state.food) == 0)

        if is_at_target and (is_final_goal or is_food_cleared):
            next_state.status = 'WIN'
            return next_state

        total_ghosts = len(next_state.ghost_positions)

        for ghost_index in range(total_ghosts):
            current_ghost_pos = next_state.ghost_positions[ghost_index]
            ghost_agent = Ghost(current_ghost_pos)

            other_ghosts = []
            for idx in range(total_ghosts):
                if idx != ghost_index:
                    other_ghosts.append(next_state.ghost_positions[idx])

            ghost_action = ghost_agent.choose_action(
                next_state.game_map,
                next_state.pacman_position,
                other_ghost_positions=other_ghosts
            )

            if ghost_action is None:
                continue

            next_state = next_state.move_ghost(ghost_index, ghost_action)
            if next_state is None:
                return None

            if next_state.pacman_position in next_state.ghost_positions:
                next_state.status = 'LOSE'
                return next_state

        return next_state
