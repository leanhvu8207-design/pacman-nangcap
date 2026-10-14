from src.search.pm_search_problem import PMSearchProblem
from src.search.dfs import DFS
from src.utils.map_loader import load_map
from src.search.bfs import BFS
from src.search.ucs import UCS
from src.search.a_star import AStar

game_map = load_map("maps/test_map.txt")

for row in game_map:
    print(row)
    
problem = PMSearchProblem(
    (1,1),
    (7,13),
    game_map
)

dfs = DFS(problem)
print("\n--- DFS ---")
actions = dfs.search()
print(f"Steps: {len(actions) if actions else None}, Expanded: {dfs.expanded_count}")

bfs = BFS(problem)
print("\n--- BFS ---")
actions_bfs = bfs.search()
print(f"Steps: {len(actions_bfs) if actions_bfs else None}, Expanded: {bfs.expanded_count}")

ucs = UCS(problem)
print("\n--- UCS ---")
actions_ucs = ucs.search()
print(f"Steps: {len(actions_ucs) if actions_ucs else None}, Expanded: {ucs.expanded_count}")

astar = AStar(problem)
print("\n--- AStar ---")
actions_astar = astar.search()
print(f"Steps: {len(actions_astar) if actions_astar else None}, Expanded: {astar.expanded_count}")

