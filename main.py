from src.utils.map_loader import load_map
from src.utils.map_info import get_map_info

from src.pacman.game_state import GameState
from src.ghost.ghost import Ghost


game_map = load_map("maps/test_map.txt")

if game_map is None:
    print("Không thể load map")
else:
    spawn, goals, ghosts = get_map_info(game_map)

    print("Spawn:", spawn)
    print("Ghosts:", ghosts)

    state = GameState(
        spawn,
        ghosts,
        set(),
        0,
        game_map
    )

    print("\n--- TEST GHOST + GAME STATE ---")

    for ghost_index in range(len(state.ghost_positions)):
        print("\nGhost index:", ghost_index)

        ghost = Ghost(state.ghost_positions[ghost_index])

        print("Position:", ghost.position)

        valid_actions = ghost.get_valid_actions(game_map)
        print("Valid actions:", valid_actions)

        print("Successors:")

        successors = state.get_ghost_successors(ghost_index)

        for next_state, action in successors:
            print(
                action,
                "->",
                next_state.ghost_positions
            )
