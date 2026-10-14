import sys
import time
import argparse
from collections import deque

from src.utils.map_loader import load_map
from src.utils.map_info import get_map_info
from src.utils.map_info import get_tile_cost

from src.search.pm_search_problem import PMSearchProblem
from src.search.multi_goal_search import MultiGoal
from src.search.bfs import BFS
from src.search.dfs import DFS
from src.search.ucs import UCS
from src.search.greedy import Greedy
from src.search.a_star import AStar

from src.pacman.game_state import GameState
from src.logic_pacman_vs_ghost.adv_problem import AdvProblem
from src.logic_pacman_vs_ghost.minimax import Minimax
from src.logic_pacman_vs_ghost.alpha_beta import AlphaBeta


def find_nearest_food(pos, food_set, game_map):
    """
    Tim vien thuc an gan nhat bang BFS theo khoang cach me cung thuc te.
    """
    if not food_set:
        return None
    queue = deque([pos])
    visited = {pos}
    while queue:
        curr = queue.popleft()
        if curr in food_set:
            return curr
        r, c = curr
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(game_map) and 0 <= nc < len(game_map[nr]):
                if game_map[nr][nc] != "#" and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
    return min(food_set, key=lambda f: abs(pos[0] - f[0]) + abs(pos[1] - f[1]))


def plan_multi_food_path(algo_name, spawn, foods, game_map, final_goal=None):
    """
    Lap ke hoach an sach toan bo thuc an bang cach tim duong lien tiep toi vien gan nhat.
    Tu dong loai bo cac vien thuc an ma Pacman di qua tren duong di.
    """
    remaining = set(foods)
    curr = spawn
    all_actions = []
    total_nodes = 0
    t0 = time.time()

    while remaining:
        next_food = min(remaining, key=lambda f: abs(curr[0] - f[0]) + abs(curr[1] - f[1]))
        prob = PMSearchProblem(curr, next_food, game_map)
        if algo_name == "DFS": searcher = DFS(prob)
        elif algo_name == "BFS": searcher = BFS(prob)
        elif algo_name == "UCS": searcher = UCS(prob)
        elif algo_name == "GREEDY": searcher = Greedy(prob)
        else: searcher = AStar(prob)

        sub_acts = searcher.search()
        if not sub_acts:
            break
        all_actions.extend(sub_acts)
        total_nodes += searcher.expanded_count

        # Mo phong tung buoc de loai bo cac vien thuc an bi an doc duong
        tr, tc = curr
        for act in sub_acts:
            if act == "UP": tr -= 1
            elif act == "DOWN": tr += 1
            elif act == "LEFT": tc -= 1
            elif act == "RIGHT": tc += 1
            remaining.discard((tr, tc))
        curr = (tr, tc)

    # Neu co Goal cuoi cung sau khi da an het thuc an
    if final_goal is not None and curr != final_goal:
        prob = PMSearchProblem(curr, final_goal, game_map)
        if algo_name == "DFS": searcher = DFS(prob)
        elif algo_name == "BFS": searcher = BFS(prob)
        elif algo_name == "UCS": searcher = UCS(prob)
        elif algo_name == "GREEDY": searcher = Greedy(prob)
        else: searcher = AStar(prob)
        sub_acts = searcher.search()
        if sub_acts:
            all_actions.extend(sub_acts)
            total_nodes += searcher.expanded_count

    time_used = time.time() - t0
    # tính tổng chi phí thực tế đi qua các địa hình
    total_path_cost = 0
    curr_pos = spawn
    moves = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
    for act in all_actions:
        curr_pos = (curr_pos[0] + moves[act][0], curr_pos[1] + moves[act][1])
        total_path_cost += get_tile_cost(curr_pos, game_map)
    return all_actions, total_nodes, time_used, total_path_cost



# ham in ban do ra terminal cho de nhin
def in_ban_do(game_map, pacman_pos, ghost_positions, target_pos, remaining_food=None):
    for r in range(len(game_map)):
        dong = ""
        for c in range(len(game_map[r])):
            pos = (r, c)
            if pos == pacman_pos:
                dong += "P "
            elif pos in ghost_positions:
                dong += "@ "
            elif pos == target_pos:
                dong += "G "
            elif remaining_food is not None:
                if pos in remaining_food:
                    dong += ". "
                else:
                    ky_tu = game_map[r][c]
                    if ky_tu in ["P", "@", "G", "."]:
                        dong += "  "
                    else:
                        dong += ky_tu + " "
            else:
                ky_tu = game_map[r][c]
                if ky_tu in ["P", "@", "G"]:
                    dong += "  "
                else:
                    dong += ky_tu + " "
        print("  " + dong)


def main():
    print("=========================================")
    print("   DO AN PACMAN AI SEARCH - NHOM 07      ")
    print("=========================================")

    # 1. Chon ban do
    print("\n--- CHON BAN DO ---")
    print("1. maps/adversarial_small.txt (Map nho co 1 Ghost)")
    print("2. maps/test_map.txt (Map chuan co 2 Ghost)")
    print("3. maps/multi_goal_test.txt (Map nhieu Goal Food)")
    print("4. maps/large_map.txt (Map lon 19x31 danh gia mo rong)")
    print("5. maps/dead_end_maze.txt (Map ngo cut va chu trinh)")
    print("6. maps/no_solution_map.txt (Map khong co loi giai)")
    print("7. maps/bad_map.txt (Map loi de test)")
    print("8. maps/weighted_swamp_shortcut_dilemma.txt (Bay duong tat dam lay)")
    print("9. maps/weighted_river_crossing_maze.txt (Me cung vuot song & dam lay)")
    print("10. maps/weighted_multi_food_wetlands.txt (Vung ngap man gom 8 Food)")
    print("11. maps/weighted_adversarial_quagmire.txt (Doi khang dam lay 2 Ghost)")
    print("12. Tu nhap duong dan file map khac (.txt)")

    chon_map = input("Nhap lua chon ban do (1-12): ").strip()

    file_map = "maps/test_map.txt"
    game_map = None

    if chon_map == "1":
        file_map = "maps/adversarial_small.txt"
        game_map = load_map(file_map)
    elif chon_map == "2":
        file_map = "maps/test_map.txt"
        game_map = load_map(file_map)
    elif chon_map == "3":
        file_map = "maps/multi_goal_test.txt"
        game_map = load_map(file_map)
    elif chon_map == "4":
        file_map = "maps/large_map.txt"
        game_map = load_map(file_map)
    elif chon_map == "5":
        file_map = "maps/dead_end_maze.txt"
        game_map = load_map(file_map)
    elif chon_map == "6":
        file_map = "maps/no_solution_map.txt"
        game_map = load_map(file_map)
    elif chon_map == "7":
        file_map = "maps/bad_map.txt"
        game_map = load_map(file_map)
    elif chon_map == "8":
        file_map = "maps/weighted_swamp_shortcut_dilemma.txt"
        game_map = load_map(file_map)
    elif chon_map == "9":
        file_map = "maps/weighted_river_crossing_maze.txt"
        game_map = load_map(file_map)
    elif chon_map == "10":
        file_map = "maps/weighted_multi_food_wetlands.txt"
        game_map = load_map(file_map)
    elif chon_map == "11":
        file_map = "maps/weighted_adversarial_quagmire.txt"
        game_map = load_map(file_map)
    elif chon_map == "12":
        file_map = input("Nhap duong dan file map (.txt): ").strip()
        game_map = load_map(file_map)
    else:
        print("Nhap sai, tu dong chon maps/test_map.txt")
        file_map = "maps/test_map.txt"
        game_map = load_map(file_map)

    # Kiem tra neu khong load duoc map
    if game_map is None:
        print("\n[LOI] Khong the load duoc map tu file:", file_map)
        return

    # Lay thong tin spawn, goal, ghost, food
    spawn, goals, ghosts, foods = get_map_info(game_map, return_foods=True)

    print("\nThong tin ban do:")
    print("  File:", file_map)
    print("  Pacman Spawn (P):", spawn)
    print("  Goals (G):", goals if len(goals) > 0 else "Khong co (hoac Food la muc tieu)")
    print("  Foods (.):", foods if len(foods) > 0 else "Khong co")
    print("  Ghosts (@):", ghosts if len(ghosts) > 0 else "Khong co")

    # 2. Chon thuat toan
    print("\n--- CHON THUAT TOAN ---")
    print("1. DFS")
    print("2. BFS")
    print("3. UCS")
    print("4. Greedy Best-First")
    print("5. A*")
    print("6. Minimax")
    print("7. Alpha-Beta")

    thuat_toan = input("Chon thuat toan (1-7): ").strip()

    # Nhom 1: Cac thuat toan tim kiem co dien don tac tu
    if thuat_toan in ["1", "2", "3", "4", "5"]:
        if len(goals) == 0 and len(foods) == 0:
            print("[LOI] Map nay khong co Goal hay Food nao de tim duong!")
            return

        ten_tt = "DFS" if thuat_toan == "1" else ("BFS" if thuat_toan == "2" else ("UCS" if thuat_toan == "3" else ("GREEDY" if thuat_toan == "4" else "A*")))
        actions = None
        exp_count = 0
        time_cost = 0.0
        path_cost = 0

        # 1. Che do Multi-Food: An het toan bo thuc an (va ve Goal neu co)
        if len(foods) > 0:
            final_goal = goals[0] if len(goals) > 0 else None
            msg_goal = f" va ve Goal tai {final_goal}" if final_goal else ""
            print(f"\n[Che do Multi-Food] An het toan bo {len(foods)} vien Food (.){msg_goal} la chien thang!")
            if len(foods) <= 12:
                problem = MultiGoal(spawn, tuple(foods), game_map, goal=final_goal)
                if thuat_toan == "1": searcher = DFS(problem)
                elif thuat_toan == "2": searcher = BFS(problem)
                elif thuat_toan == "3": searcher = UCS(problem)
                elif thuat_toan == "4": searcher = Greedy(problem)
                else: searcher = AStar(problem)

                print("\nDang chay thuat toan:", ten_tt, "...")
                actions = searcher.search()
                exp_count = searcher.expanded_count
                time_cost = searcher.time_used
                if actions:
                    path_cost = problem.measure_path_cost(actions)
            else:
                print(f"\nDang lap ke hoach an sach {len(foods)} vien Food (.) voi {ten_tt}...")
                actions, exp_count, time_cost, path_cost = plan_multi_food_path(ten_tt, spawn, foods, game_map, final_goal=final_goal)

        # 2. Che do Multi-Goal: Di qua tat ca cac Goal (G)
        elif len(goals) > 1:
            problem = MultiGoal(spawn, tuple(goals), game_map, goal=None)
            print(f"\n[Che do Multi-Goal] Di qua tat ca {len(goals)} vi tri Goal (G)!")
            if thuat_toan == "1": searcher = DFS(problem)
            elif thuat_toan == "2": searcher = BFS(problem)
            elif thuat_toan == "3": searcher = UCS(problem)
            elif thuat_toan == "4": searcher = Greedy(problem)
            else: searcher = AStar(problem)

            print("\nDang chay thuat toan:", ten_tt, "...")
            actions = searcher.search()
            exp_count = searcher.expanded_count
            time_cost = searcher.time_used
            if actions:
                path_cost = problem.measure_path_cost(actions)

        # 3. Che do Single-Goal: Tim duong toi 1 Goal (G)
        else:
            problem = PMSearchProblem(spawn, goals[0], game_map)
            print(f"\n[Che do Single-Goal] Tim duong toi Goal (G) tai {goals[0]}!")
            if thuat_toan == "1": searcher = DFS(problem)
            elif thuat_toan == "2": searcher = BFS(problem)
            elif thuat_toan == "3": searcher = UCS(problem)
            elif thuat_toan == "4": searcher = Greedy(problem)
            else: searcher = AStar(problem)

            print("\nDang chay thuat toan:", ten_tt, "...")
            actions = searcher.search()
            exp_count = searcher.expanded_count
            time_cost = searcher.time_used
            if actions:
                path_cost = problem.measure_path_cost(actions)

        print("\n=== KET QUA TIM KIEM ===")
        print("Thuat toan:", ten_tt)
        if actions is not None:
            print("Trang thai: Tim thay duong di thanh cong!")
            print("So buoc di:", len(actions))
            print("Tong chi phi (Path Cost):", path_cost)
            print("Chuoi hanh dong:", actions)
        else:
            print("Trang thai: Khong tim thay duong di toi dich!")

        print("So node da duyet (expanded_count):", exp_count)
        print("Thoi gian chay (time_used):", round(time_cost, 6), "giay")

    # Nhom 2: Thuat toan doi khang co Ghost
    elif thuat_toan in ["6", "7"]:
        if len(goals) == 0 and len(foods) == 0:
            print("[LOI] Map doi khang can co it nhat 1 Goal dich hoac Food!")
            return

        remaining_goals = list(goals)
        if len(foods) > 0:
            target = find_nearest_food(spawn, set(foods), game_map)
        elif len(remaining_goals) > 0:
            target = find_nearest_food(spawn, set(remaining_goals), game_map)
        else:
            target = None

        ten_tt = "Minimax" if thuat_toan == "6" else "Alpha-Beta"

        # Nhap do sau tim kiem
        default_depth = 3 if len(ghosts) >= 2 else 2
        depth_input = input(f"\nNhap do sau tim kiem depth (mac dinh {default_depth}): ").strip()
        if depth_input.isdigit() and int(depth_input) >= 1:
            depth_limit = int(depth_input)
        else:
            depth_limit = default_depth

        print("\nChon che do:")
        print("  1. Chi tinh nuoc di tot nhat o buoc dau tien")
        print("  2. Chay mo phong tran dau tung buoc (Simulation)")
        che_do = input("Chon che do (1 hoac 2, mac dinh 2): ").strip()

        # Che do 1: Chi tinh nuoc dau
        if che_do == "1":
            prob = AdvProblem(spawn, ghosts, target, game_map)
            if thuat_toan == "6":
                ai = Minimax(prob, depth_limit)
            else:
                ai = AlphaBeta(prob, depth_limit)

            action = ai.search()
            print("\n=== KET QUA QUYET DINH BUOC DAU ===")
            print("Thuat toan:", ten_tt)
            print("Do sau (depth):", depth_limit)
            print("Hanh dong tot nhat:", action)
            print("Gia tri danh gia (last_value):", ai.last_value)
            print("So node da duyet:", ai.expanded_count)
            print("Thoi gian tinh:", round(ai.time_used, 6), "giay")
            return

        # Che do 2: Mo phong tran dau
        state = GameState(spawn, ghosts.copy(), set(foods), 0, game_map)
        buoc = 0
        tong_nodes = 0
        tong_time = 0.0
        lich_su_actions = []
        lich_su_positions = [state.pacman_position]

        print("\n--- BAT DAU MO PHONG TRAN DAU PACMAN VS GHOST ---")
        print("Ban do khoi dau:")
        in_ban_do(game_map, state.pacman_position, state.ghost_positions, target, state.food)

        max_steps = max(100, len(foods) * 4 if len(foods) > 0 else 60)
        huong_nguoc_lai = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}

        while buoc < max_steps:
            if len(state.food) > 0:
                target = find_nearest_food(state.pacman_position, state.food, game_map)
            elif len(remaining_goals) > 0:
                target = find_nearest_food(state.pacman_position, set(remaining_goals), game_map)
            else:
                target = None

            if target is None:
                print("\n>>> CHIEN THANG: PACMAN DA HOAN THANH TAT CA MUC TIEU! <<<")
                state.status = "WIN"
                break

            buoc += 1

            # Tai moi buoc tao bai toan voi vi tri hien tai
            prob = AdvProblem(state.pacman_position, state.ghost_positions, target, game_map)
            recent = lich_su_positions[-8:]

            if thuat_toan == "6":
                ai = Minimax(prob, depth_limit, recent_positions=recent)
            else:
                ai = AlphaBeta(prob, depth_limit, recent_positions=recent)

            act = ai.search()

            tong_nodes += ai.expanded_count
            tong_time += ai.time_used

            if act is None:
                print(f"Buoc {buoc}: Pacman khong con nuoc di hop le!")
                break

            lich_su_actions.append(act)

            # Cho Pacman va Ghost di chuyen
            prev_food_count = len(state.food)
            is_final = (len(state.food) == 0 and len(remaining_goals) <= 1)
            state = state.step(act, target, is_final_goal=is_final)
            lich_su_positions.append(state.pacman_position)

            print(f"\n[Buoc {buoc}] Pacman di: {act}")
            print(f"  Pacman o: {state.pacman_position} | Ghosts o: {state.ghost_positions}")
            info_score = f" | Score: {state.score}" if len(foods) > 0 else ""
            info_food = f" | Food con lai: {len(state.food)}" if len(foods) > 0 else ""
            print(f"  Diem eval: {ai.last_value}{info_score}{info_food} | Nodes: {ai.expanded_count} | Time: {round(ai.time_used, 5)}s")
            in_ban_do(game_map, state.pacman_position, state.ghost_positions, target, state.food)

            if len(state.food) < prev_food_count:
                print(f"  [+] Da an Food tai {state.pacman_position}! Con lai {len(state.food)} Food")

            if state.pacman_position in remaining_goals:
                remaining_goals.remove(state.pacman_position)
                state.score += 20
                print(f"  [+] Da thu thap Goal! Con {len(remaining_goals)} Goal")

            if state.status == "LOSE":
                print("\n>>> THUA CUOC: PACMAN DA BI GHOST BAT! <<<")
                break

            da_het_goal = len(remaining_goals) == 0
            da_het_food = len(state.food) == 0
            if da_het_goal and da_het_food:
                print("\n>>> CHIEN THANG: PACMAN DA HOAN THANH TAT CA MUC TIEU! <<<")
                state.status = "WIN"
                break
            else:
                state.status = "PLAYING"

            time.sleep(0.04)

        print("\n================ TONG KET MO PHONG ================")
        print("Thuat toan:", ten_tt)
        print("Ket qua:", state.status)
        print("Tong so buoc di:", len(lich_su_actions))
        print("Chuoi hanh dong:", lich_su_actions)
        print("Tong so node da mo rong:", tong_nodes)
        print("Tong thoi gian tinh toan AI:", round(tong_time, 5), "giay")
        print("====================================================")

    else:
        print("Lua chon khong hop le!")


def run_cli(map_path, algo_name, depth=2, mode="match"):
    """
    Chay thuat toan truc tiep tu command-line khong can tuong tac ban phim.
    Ho tro kiem thu tu dong va tai tao ket qua bao cao.
    """
    game_map = load_map(map_path)
    if game_map is None:
        print(f"[LOI] Khong the load duoc map tu file: {map_path}")
        return

    spawn, goals, ghosts, foods = get_map_info(game_map, return_foods=True)
    algo = algo_name.upper()
    if algo == "ASTAR": algo = "A*"
    elif algo in ["ALPHABETA", "ALPHA_BETA"]: algo = "ALPHA-BETA"

    if algo in ["DFS", "BFS", "UCS", "GREEDY", "A*"]:
        if len(goals) == 0 and len(foods) == 0:
            print("[LOI] Map nay khong co Goal hay Food nao de tim duong!")
            return

        final_goal = goals[0] if len(goals) > 0 else None
        if len(foods) > 0:
            if len(foods) <= 12:
                problem = MultiGoal(spawn, tuple(foods), game_map, goal=final_goal)
                if algo == "DFS": searcher = DFS(problem)
                elif algo == "BFS": searcher = BFS(problem)
                elif algo == "UCS": searcher = UCS(problem)
                elif algo == "GREEDY": searcher = Greedy(problem)
                else: searcher = AStar(problem)
                actions = searcher.search()
                exp_count = searcher.expanded_count
                time_cost = searcher.time_used
                path_cost = problem.measure_path_cost(actions) if actions else 0
            else:
                actions, exp_count, time_cost, path_cost = plan_multi_food_path(algo, spawn, foods, game_map, final_goal=final_goal)
        elif len(goals) > 1:
            problem = MultiGoal(spawn, tuple(goals), game_map, goal=None)
            if algo == "DFS": searcher = DFS(problem)
            elif algo == "BFS": searcher = BFS(problem)
            elif algo == "UCS": searcher = UCS(problem)
            elif algo == "GREEDY": searcher = Greedy(problem)
            else: searcher = AStar(problem)
            actions = searcher.search()
            exp_count = searcher.expanded_count
            time_cost = searcher.time_used
            path_cost = problem.measure_path_cost(actions) if actions else 0
        else:
            problem = PMSearchProblem(spawn, goals[0], game_map)
            if algo == "DFS": searcher = DFS(problem)
            elif algo == "BFS": searcher = BFS(problem)
            elif algo == "UCS": searcher = UCS(problem)
            elif algo == "GREEDY": searcher = Greedy(problem)
            else: searcher = AStar(problem)
            actions = searcher.search()
            exp_count = searcher.expanded_count
            time_cost = searcher.time_used
            path_cost = problem.measure_path_cost(actions) if actions else 0

        print("\n=== KET QUA TIM KIEM (CLI) ===")
        print(f"Map: {map_path}")
        print(f"Thuat toan: {algo}")
        if actions is not None:
            print(f"Trang thai: Tim thay duong di thanh cong!")
            print(f"So buoc di: {len(actions)}")
            print(f"Tong chi phi (Path Cost): {path_cost}")
            print(f"Chuoi hanh dong: {actions}")
        else:
            print(f"Trang thai: Khong tim thay duong di toi dich!")
        print(f"So node da duyet (expanded_count): {exp_count}")
        print(f"Thoi gian chay (time_used): {round(time_cost, 6)} giay")

    elif algo in ["MINIMAX", "ALPHA-BETA"]:
        if len(goals) == 0 and len(foods) == 0:
            print("[LOI] Map doi khang can co it nhat 1 Goal dich hoac Food!")
            return

        remaining_goals = list(goals)
        if len(foods) > 0:
            target = find_nearest_food(spawn, set(foods), game_map)
        elif len(remaining_goals) > 0:
            target = find_nearest_food(spawn, set(remaining_goals), game_map)
        else:
            target = None

        if mode == "step":
            prob = AdvProblem(spawn, ghosts, target, game_map)
            ai = Minimax(prob, depth) if algo == "MINIMAX" else AlphaBeta(prob, depth)
            action = ai.search()
            print("\n=== KET QUA QUYET DINH BUOC DAU (CLI) ===")
            print(f"Map: {map_path}")
            print(f"Thuat toan: {algo}")
            print(f"Do sau (depth): {depth}")
            print(f"Hanh dong tot nhat: {action}")
            print(f"Gia tri danh gia (last_value): {ai.last_value}")
            print(f"So node da duyet: {ai.expanded_count}")
            print(f"Thoi gian tinh: {round(ai.time_used, 6)} giay")
        else:
            state = GameState(spawn, ghosts.copy(), set(foods), 0, game_map)
            buoc = 0
            tong_nodes = 0
            tong_time = 0.0
            lich_su_actions = []
            lich_su_positions = [state.pacman_position]
            max_steps = max(100, len(foods) * 4 if len(foods) > 0 else 60)

            while buoc < max_steps:
                if len(state.food) > 0:
                    target = find_nearest_food(state.pacman_position, state.food, game_map)
                elif len(remaining_goals) > 0:
                    target = find_nearest_food(state.pacman_position, set(remaining_goals), game_map)
                else:
                    target = None

                if target is None:
                    state.status = "WIN"
                    break

                buoc += 1
                prob = AdvProblem(state.pacman_position, state.ghost_positions, target, game_map)
                recent = lich_su_positions[-8:]
                ai = Minimax(prob, depth, recent_positions=recent) if algo == "MINIMAX" else AlphaBeta(prob, depth, recent_positions=recent)
                act = ai.search()
                tong_nodes += ai.expanded_count
                tong_time += ai.time_used
                if act is None:
                    break
                lich_su_actions.append(act)
                is_final = (len(state.food) == 0 and len(remaining_goals) <= 1)
                state = state.step(act, target, is_final_goal=is_final)
                lich_su_positions.append(state.pacman_position)
                if state.pacman_position in remaining_goals:
                    remaining_goals.remove(state.pacman_position)
                    state.score += 20
                if state.status == "LOSE":
                    break
                if len(remaining_goals) == 0 and len(state.food) == 0:
                    state.status = "WIN"
                    break
                else:
                    state.status = "PLAYING"

            print("\n=== TONG KET MO PHONG DOI KHANG (CLI) ===")
            print(f"Map: {map_path}")
            print(f"Thuat toan: {algo}")
            print(f"Do sau (depth): {depth}")
            print(f"Ket qua: {state.status}")
            print(f"Tong so buoc di: {len(lich_su_actions)}")
            print(f"Chuoi hanh dong: {lich_su_actions}")
            print(f"Tong so node da mo rong: {tong_nodes}")
            print(f"Tong thoi gian tinh toan AI: {round(tong_time, 5)} giay")
    else:
        print(f"[LOI] Thuat toan khong hop le: {algo_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pacman AI Search - Nhom 07")
    parser.add_argument("--ui", action="store_true", help="Chay giao dien do hoa Vintage Arcade (Pygame)")
    parser.add_argument("--map", type=str, default=None, help="Duong dan toi file ban do .txt (vd: maps/test_map.txt)")
    parser.add_argument("--algo", type=str, default=None, help="Thuat toan: DFS, BFS, UCS, GREEDY, ASTAR, MINIMAX, ALPHABETA")
    parser.add_argument("--depth", type=int, default=2, help="Do sau tim kiem cho Minimax / Alpha-Beta (mac dinh: 2)")
    parser.add_argument("--mode", type=str, default="match", choices=["step", "match"], help="Che do doi khang: step (1 buoc) hoac match (mo phong tran)")

    args = parser.parse_args()

    if args.ui:
        from ui.main import run_ui
        run_ui()
    elif args.map and args.algo:
        run_cli(args.map, args.algo, args.depth, args.mode)
    else:
        main()

# ========================================================
# CÁCH CHẠY CHƯƠNG TRÌNH:
# 1. Chạy trên Terminal (dòng lệnh giao diện văn bản):
#    python main.py
#
# 2. Chạy giao diện đồ họa Vintage Arcade (UI):
#    python main.py --ui
#    (Hoặc chạy trực tiếp: python -m ui.main)
# ========================================================