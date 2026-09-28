from src.utils.map_loader import load_map
from src.utils.map_info import get_map_info
from src.search.pm_search_problem import PMSearchProblem
from src.search.multi_goal_search import MultiGoal
from src.search.bfs import BFS
from src.search.dfs import DFS
from src.search.ucs import UCS
from src.search.greedy import Greedy
from src.search.a_star import AStar


game_map = load_map("maps/test_map.txt")

if game_map == None:
    print("Không thể load map")
else:
    spawn, goals, ghosts = get_map_info(game_map)

    print("Spawn:", spawn)
    print("Goals:", goals)
    print("Ghosts:", ghosts)

    if len(goals) == 1:
        goal = goals[0]
        problem = PMSearchProblem(spawn, goal, game_map)
    else:
        problem = MultiGoal(spawn, tuple(goals), game_map)
    algorithm = "ASTAR"
    if algorithm == "DFS":
        search = DFS(problem)
    elif algorithm == "BFS":
        search = BFS(problem)
    elif algorithm == "UCS":
        search = UCS(problem)
    elif algorithm == "GREEDY":
        search = Greedy(problem)
    elif algorithm == "ASTAR":
        search = AStar(problem)

    actions = search.search()

    print("Algorithm:", algorithm)
    print("Actions:", actions)