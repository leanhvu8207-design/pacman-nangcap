from src.utils.map_loader import load_map
from src.utils.map_info import get_map_info
from src.search.pm_search_problem import PMSearchProblem
from src.search.multi_goal_search import MultiGoal
from src.search.bfs import BFS


game_map = load_map("maps/test_map.txt")

if game_map == None:
    print("Không thể load map")
else:
    spawn, goals = get_map_info(game_map)

    print("Spawn:", spawn)
    print("Goals:", goals)
    
if len(goals) == 1:
    goal = goals[0]
    problem = PMSearchProblem(spawn,goal,game_map)
else:
    problem = MultiGoal(spawn,tuple(goals),game_map)

bfs = BFS(problem)
actions = bfs.search()
print("Actions",actions)