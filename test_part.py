from src.search.pm_search_problem import PMSearchProblem
from src.search.dfs import DFS
from src.utils.map_loader import load_map
from src.search.bfs import BFS
from src.search.ucs import UCS
from src.search.a_star import AStar

game_map = load_map("maps/test_map.tx")

for row in game_map:
    print(row)
    
problem = PMSearchProblem(
    (1,1),
    (7,13),
    game_map
)

dfs = DFS(problem)
print("DFS")
actions = dfs.search()
print(actions)

bfs = BFS(problem)
print("BFS")
actions_bfs = bfs.search()
print(actions_bfs)

ucs = UCS(problem)
print("UCS")
actions_ucs = ucs.search()
print(actions_ucs)

astar = AStar(problem)
print("AStar")
actions_astar = astar.search()
print(actions_astar)
