"""
Chương trình chính Pacman: Giao diện dòng lệnh chạy tìm kiếm và đối kháng.
Học phần: Biểu diễn tri thức và tìm kiếm nâng cao (UET.AI2014) - Nhóm 07
"""

import os
import sys
import time
import argparse
from collections import deque

# Dam bao tuong thich ma hoa tren Windows Console
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from src.utils.map_loader import load_map
from src.utils.map_info import get_map_info
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


def get_available_maps(maps_dir="maps"):
    """Quet va lay danh sach tat ca cac ban do .txt co trong thu muc maps/."""
    if not os.path.isdir(maps_dir):
        return []
    files = [f for f in os.listdir(maps_dir) if f.endswith(".txt")]
    files.sort()
    return [os.path.join(maps_dir, f).replace("\\", "/") for f in files]


def find_nearest_food(pos, food_set, game_map):
    """Tim vien thuc an gan nhat bang BFS theo khoang cach me cung thuc te."""
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
    remaining.discard(curr)
    all_actions = []
    total_nodes = 0
    t0 = time.time()

    is_h0 = algo_name in ["ASTAR_H0", "A* (h=0)", "A*_H0"]

    while remaining:
        next_food = min(remaining, key=lambda f: abs(curr[0] - f[0]) + abs(curr[1] - f[1]))
        if curr == next_food:
            remaining.discard(curr)
            continue

        h_fn = (lambda st: 0) if is_h0 else None
        prob = PMSearchProblem(curr, next_food, game_map, heuristic_fn=h_fn)
        if algo_name == "DFS": searcher = DFS(prob)
        elif algo_name == "BFS": searcher = BFS(prob)
        elif algo_name == "UCS": searcher = UCS(prob)
        elif algo_name == "GREEDY": searcher = Greedy(prob)
        else: searcher = AStar(prob)

        sub_acts = searcher.search()
        if sub_acts is None:
            break
        all_actions.extend(sub_acts)
        total_nodes += searcher.expanded_count

        tr, tc = curr
        remaining.discard((tr, tc))
        for act in sub_acts:
            if act == "UP": tr -= 1
            elif act == "DOWN": tr += 1
            elif act == "LEFT": tc -= 1
            elif act == "RIGHT": tc += 1
            remaining.discard((tr, tc))
        curr = (tr, tc)
        remaining.discard(curr)

    if final_goal is not None and curr != final_goal:
        h_fn = (lambda st: 0) if is_h0 else None
        prob = PMSearchProblem(curr, final_goal, game_map, heuristic_fn=h_fn)
        if algo_name == "DFS": searcher = DFS(prob)
        elif algo_name == "BFS": searcher = BFS(prob)
        elif algo_name == "UCS": searcher = UCS(prob)
        elif algo_name == "GREEDY": searcher = Greedy(prob)
        else: searcher = AStar(prob)
        sub_acts = searcher.search()
        if sub_acts is not None:
            all_actions.extend(sub_acts)
            total_nodes += searcher.expanded_count

    time_used = time.time() - t0
    return all_actions, total_nodes, time_used


def in_ban_do(game_map, pacman_pos, ghost_positions, target_pos, remaining_food=None):
    """Hien thi trang thai ma tran ban do len terminal."""
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


def in_ban_do_duong_di(game_map, spawn, actions, ghosts=None):
    """
    Hien thi ban do kem dau vet duong di cua Pacman.
    P: Vi tri xuat phat
    *: Vet cac buoc Pacman da di qua
    G: Vi tri dich den cuoi cung
    @: Vi tri ma
    """
    curr = spawn
    path_cells = {curr}
    for act in actions:
        r, c = curr
        if act == "UP": curr = (r - 1, c)
        elif act == "DOWN": curr = (r + 1, c)
        elif act == "LEFT": curr = (r, c - 1)
        elif act == "RIGHT": curr = (r, c + 1)
        path_cells.add(curr)

    ghost_set = set(ghosts) if ghosts else set()
    for r in range(len(game_map)):
        dong = ""
        for c in range(len(game_map[r])):
            pos = (r, c)
            if pos == spawn:
                dong += "P "
            elif pos in ghost_set:
                dong += "@ "
            elif pos == curr and pos != spawn:
                dong += "G "
            elif pos in path_cells:
                dong += "* "
            else:
                dong += game_map[r][c] + " "
        print("  " + dong)


def chay_terminal_menu():
    """Giao dien tuong tac truc quan tung buoc tren Terminal."""
    maps_list = get_available_maps("maps")
    print('\n=========================================')
    print('   CHON BAN DO DE THUC THI THUAT TOAN   ')
    print('=========================================')
    
    map_descs = {
        "test_map.txt": "Map tieu chuan co 2 Ghost va Food",
        "adversarial_small.txt": "Map doi khang nho co 1 Ghost",
        "multi_goal_test.txt": "Map nhieu Goal Food (Danh gia MST Heuristic)",
        "multi_food_and_final_goal.txt": "Map nhieu Food va Goal cuoi",
        "large_map.txt": "Map lon 19x22 danh gia toc do mo rong",
        "adversarial_dead_end_trap.txt": "Map bay ngo cut kiem thu ham danh gia",
        "terrain_cost_map.txt": "Map chi phi dia hinh khong dong nhat (~, S)",
        "no_solution_map.txt": "Map khong co loi giai (Test Unreachability)",
        "bad_map.txt": "Map loi dinh dang (Test validation)",
    }

    for idx, mpath in enumerate(maps_list, 1):
        mname = os.path.basename(mpath)
        desc = f" ({map_descs[mname]})" if mname in map_descs else ""
        print(f"{idx}. {mpath}{desc}")
    print(f"{len(maps_list) + 1}. Tu nhap duong dan file map khac (.txt)")

    chon_map = input(f'Nhap lua chon ban do (1-{len(maps_list) + 1}, mac dinh 1): ').strip()
    file_map = maps_list[0] if maps_list else 'maps/test_map.txt'

    if chon_map.isdigit():
        val = int(chon_map)
        if 1 <= val <= len(maps_list):
            file_map = maps_list[val - 1]
        elif val == len(maps_list) + 1:
            custom_path = input('Nhap duong dan file map (.txt): ').strip()
            if custom_path:
                file_map = custom_path
        else:
            print(f'Lua chon khong ton tai, tu dong chon: {file_map}')
    elif chon_map:
        file_map = chon_map

    game_map = load_map(file_map)
    if game_map is None:
        print('\n[LOI] Khong the load duoc map tu file:', file_map)
        return

    spawn, goals, ghosts, foods = get_map_info(game_map, return_foods=True)
    print('\nThong tin ban do:')
    print('  File ban do:', file_map)
    print('  Kich thuoc:', f'{len(game_map)}x{len(game_map[0])}')
    print('  Pacman Spawn (P):', spawn)
    print('  Goals (G):', goals if len(goals) > 0 else 'Khong co (hoac Food la muc tieu)')
    print('  Foods (.):', foods if len(foods) > 0 else 'Khong co')
    print('  Ghosts (@):', ghosts if len(ghosts) > 0 else 'Khong co')

    print('\n--- CHON THUAT TOAN ---')
    print('1. DFS (Depth-First Search)')
    print('2. BFS (Breadth-First Search)')
    print('3. UCS (Uniform-Cost Search)')
    print('4. Greedy Best-First Search')
    print('5. A* Search (Heuristic MST / Manhattan)')
    print('6. A* Search voi h=0 (Baseline danh gia Heuristic - Muc 5.2)')
    print('7. Minimax (Adversarial Search)')
    print('8. Alpha-Beta Pruning (Adversarial Search)')

    thuat_toan = input('Chon thuat toan (1-8, mac dinh 5): ').strip()
    if not thuat_toan:
        thuat_toan = '5'

    # 1. NHOM THUAT TOAN TIM DUONG CLASSIC SEARCH (1-6)
    if thuat_toan in ['1', '2', '3', '4', '5', '6']:
        if len(goals) == 0 and len(foods) == 0:
            print('[LOI] Map nay khong co Goal hay Food nao de tim duong!')
            return

        is_h0 = (thuat_toan == '6')
        h_fn = (lambda st: 0) if is_h0 else None

        algo_dict = {
            '1': ('DFS', DFS),
            '2': ('BFS', BFS),
            '3': ('UCS', UCS),
            '4': ('GREEDY', Greedy),
            '5': ('A*', AStar),
            '6': ('A* (h=0)', AStar)
        }
        ten_tt, searcher_cls = algo_dict[thuat_toan]

        actions = None
        exp_count = 0
        time_cost = 0.0
        path_cost = 0

        # Truong hop 1: Co Food (Multi-Food hoac Food + Final Goal)
        if len(foods) > 0:
            final_goal = goals[0] if len(goals) > 0 else None
            msg_goal = f' va ve Goal tai {final_goal}' if final_goal else ''
            print(f'\n[Che do Multi-Food] An het toan bo {len(foods)} vien Food (.){msg_goal} la chien thang!')

            if len(foods) <= 12:
                problem = MultiGoal(spawn, tuple(foods), game_map, goal=final_goal, heuristic_fn=h_fn)
                searcher = searcher_cls(problem)
                print(f'\nDang chay thuat toan: {ten_tt} ...')
                actions = searcher.search()
                exp_count = searcher.expanded_count
                time_cost = searcher.time_used
                if actions is not None:
                    path_cost = problem.measure_path_cost(actions)
            else:
                print(f'\nDang lap ke hoach an sach {len(foods)} vien Food (.) voi {ten_tt} ...')
                actions, exp_count, time_cost = plan_multi_food_path(ten_tt, spawn, foods, game_map, final_goal=final_goal)
                if actions is not None:
                    path_cost = len(actions)
                else:
                    path_cost = 0

        # Truong hop 2: Nhieu Goal (Multi-Goal)
        elif len(goals) > 1:
            problem = MultiGoal(spawn, tuple(goals), game_map, goal=None, heuristic_fn=h_fn)
            print(f'\n[Che do Multi-Goal] Di qua tat ca {len(goals)} vi tri Goal (G)!')
            searcher = searcher_cls(problem)
            print(f'\nDang chay thuat toan: {ten_tt} ...')
            actions = searcher.search()
            exp_count = searcher.expanded_count
            time_cost = searcher.time_used
            if actions is not None:
                path_cost = problem.measure_path_cost(actions)

        # Truong hop 3: Single Goal
        else:
            problem = PMSearchProblem(spawn, goals[0], game_map, heuristic_fn=h_fn)
            print(f'\n[Che do Single-Goal] Tim duong toi Goal (G) tai {goals[0]}!')
            searcher = searcher_cls(problem)
            print(f'\nDang chay thuat toan: {ten_tt} ...')
            actions = searcher.search()
            exp_count = searcher.expanded_count
            time_cost = searcher.time_used
            if actions is not None:
                path_cost = problem.measure_path_cost(actions)

        # Hien thi ket qua day du theo Muc 4 cua de bai
        print('\n================ KET QUA TIM KIEM (MUC 4) ================')
        print('Thuat toan da su dung          :', ten_tt)
        if actions is not None:
            print('Trang thai loi giai            : TIM THAY DUONG DI THANH CONG')
            print('So buoc di (Path Length)       :', len(actions))
            print('Tong chi phi (Path Cost)       :', path_cost)
            print('So trang thai mo rong (Nodes)  :', exp_count)
            print('Thoi gian chay (Time)          :', f'{round(time_cost, 6)} giay ({round(time_cost * 1000, 2)} ms)')
            print('Chuoi hanh dong chi tiet       :', actions)
            print('\nBan do truc quan hoa duong di (* = vet buoc di cua Pacman):')
            in_ban_do_duong_di(game_map, spawn, actions, ghosts)
        else:
            print('Trang thai loi giai            : KHONG TIM THAY LOI GIAI (Unreachable)')
            print('So trang thai mo rong (Nodes)  :', exp_count)
            print('Thoi gian chay (Time)          :', f'{round(time_cost, 6)} giay ({round(time_cost * 1000, 2)} ms)')
        print('==========================================================')

    # 2. NHOM THUAT TOAN DOI KHANG ADVERSARIAL (7-8)
    elif thuat_toan in ['7', '8']:
        if len(goals) == 0 and len(foods) == 0:
            print('[LOI] Map doi khang can co it nhat 1 Goal dich hoac Food!')
            return

        remaining_goals = list(goals)
        if len(foods) > 0:
            target = find_nearest_food(spawn, set(foods), game_map)
        elif len(remaining_goals) > 0:
            target = find_nearest_food(spawn, set(remaining_goals), game_map)
        else:
            target = None

        ten_tt = 'Minimax' if thuat_toan == '7' else 'Alpha-Beta'
        default_depth = 3 if len(ghosts) >= 2 else 2

        depth_input = input(f'\nNhap do sau tim kiem depth (mac dinh {default_depth}): ').strip()
        depth_limit = int(depth_input) if depth_input.isdigit() and int(depth_input) >= 1 else default_depth

        print('\nChon che do thuc thi doi khang:')
        print('  1. Chi tinh nuoc di tot nhat o buoc dau tien (Step Mode - Theo Muc 4)')
        print('  2. Chay mo phong tran dau tung buoc (Match Simulation)')
        che_do = input('Chon che do (1 hoac 2, mac dinh 2): ').strip()

        # Che do 1 buoc (Step Mode)
        if che_do == '1':
            prob = AdvProblem(spawn, ghosts, target, game_map)
            ai = Minimax(prob, depth_limit) if thuat_toan == '7' else AlphaBeta(prob, depth_limit)
            action = ai.search()

            print('\n=== KET QUA QUYET DINH DOI KHANG BUOC DAU (MUC 4) ===')
            print('Tac tu da su dung              :', ten_tt)
            print('Do sau tim kiem (Depth)        :', depth_limit)
            print('Hanh dong duoc chon (Action)   :', action)
            print('Gia tri danh gia (Evaluation)  :', ai.last_value)
            print('So trang thai da xet (Nodes)   :', ai.expanded_count)
            print('Thoi gian ra quyet dinh (Time) :', f'{round(ai.time_used, 6)} giay ({round(ai.time_used * 1000, 2)} ms)')
            print('======================================================')
            return

        # Che do mo phong tran dau (Simulation)
        ghosts_copy = list(ghosts)
        food_set_copy = set(foods)
        state = GameState(spawn, ghosts_copy, food_set_copy, 0, game_map)
        buoc = 0
        tong_nodes = 0
        tong_time = 0.0
        lich_su_actions = []
        lich_su_positions = [state.pacman_position]

        print('\n--- BAT DAU MO PHONG TRAN DAU PACMAN VS GHOST ---')
        print('Ban do khoi dau:')
        in_ban_do(game_map, state.pacman_position, state.ghost_positions, target, state.food)
        max_steps = max(100, len(foods) * 4) if len(foods) > 0 else 60

        while buoc < max_steps:
            if len(state.food) > 0:
                target = find_nearest_food(state.pacman_position, state.food, game_map)
            elif len(remaining_goals) > 0:
                target = find_nearest_food(state.pacman_position, set(remaining_goals), game_map)
            else:
                target = None

            if target is None:
                print('\n>>> CHIEN THANG: PACMAN DA HOAN THANH TAT CA MUC TIEU! <<<')
                state.status = 'WIN'
                break

            buoc += 1
            prob = AdvProblem(state.pacman_position, state.ghost_positions, target, game_map)
            recent = lich_su_positions[-8:]

            ai = Minimax(prob, depth_limit, recent_positions=recent) if thuat_toan == '7' else AlphaBeta(prob, depth_limit, recent_positions=recent)
            act = ai.search()
            tong_nodes += ai.expanded_count
            tong_time += ai.time_used

            if act is None:
                print(f'Buoc {buoc}: Pacman khong con nuoc di hop le!')
                break

            lich_su_actions.append(act)
            prev_food_count = len(state.food)
            is_final = len(state.food) == 0 and len(remaining_goals) <= 1
            state = state.step(act, target, is_final_goal=is_final)
            lich_su_positions.append(state.pacman_position)

            print(f'\n[Buoc {buoc}] Pacman di: {act}')
            print(f'  Pacman o: {state.pacman_position} | Ghosts o: {state.ghost_positions}')
            info_score = f' | Score: {state.score}' if len(foods) > 0 else ''
            info_food = f' | Food con lai: {len(state.food)}' if len(foods) > 0 else ''
            print(f'  Diem eval: {ai.last_value}{info_score}{info_food} | Nodes: {ai.expanded_count} | Time: {round(ai.time_used, 5)}s')
            in_ban_do(game_map, state.pacman_position, state.ghost_positions, target, state.food)

            if len(state.food) < prev_food_count:
                print(f'  [+] Da an Food tai {state.pacman_position}! Con lai {len(state.food)} Food')
            if state.pacman_position in remaining_goals:
                remaining_goals.remove(state.pacman_position)
                state.score += 20
                print(f'  [+] Da thu thap Goal! Con {len(remaining_goals)} Goal')

            if state.status == 'LOSE':
                print('\n>>> THUA CUOC: PACMAN DA BI GHOST BAT! <<<')
                break

            if len(remaining_goals) == 0 and len(state.food) == 0:
                print('\n>>> CHIEN THANG: PACMAN DA HOAN THANH TAT CA MUC TIEU! <<<')
                state.status = 'WIN'
                break
            else:
                state.status = 'PLAYING'

            time.sleep(0.04)

        print('\n================ TONG KET MO PHONG DOI KHANG ================')
        print('Thuat toan da su dung          :', ten_tt)
        print('Do sau tim kiem (Depth)        :', depth_limit)
        print('Ket qua tran dau               :', state.status)
        print('Tong so buoc di chuyen         :', len(lich_su_actions))
        print('Chuoi hanh dong                :', lich_su_actions)
        print('Tong so node da mo rong        :', tong_nodes)
        print('Tong thoi gian tinh toan AI    :', f'{round(tong_time, 5)} giay')
        print('=============================================================')
    else:
        print('Lua chon khong hop le!')


def run_cli(map_path, algo_name, depth=2, mode='match'):
    """Chay truc tiep thuat toan tu tham so dong lenh (CLI)."""
    game_map = load_map(map_path)
    if game_map is None:
        print(f'[LOI] Khong the load duoc map tu file: {map_path}')
        return

    spawn, goals, ghosts, foods = get_map_info(game_map, return_foods=True)
    raw_algo = algo_name.upper().replace("-", "_")

    is_h0 = raw_algo in ['ASTAR_H0', 'A*_H0', 'A*H0']
    h_fn = (lambda st: 0) if is_h0 else None

    # Normalization
    if raw_algo in ['ASTAR', 'A*']:
        algo = 'A*'
    elif is_h0:
        algo = 'A* (h=0)'
    elif raw_algo in ['ALPHABETA', 'ALPHA_BETA']:
        algo = 'ALPHA-BETA'
    else:
        algo = raw_algo

    # 1. CLASSIC SEARCH
    if algo in ['DFS', 'BFS', 'UCS', 'GREEDY', 'A*', 'A* (h=0)']:
        if len(goals) == 0 and len(foods) == 0:
            print('[LOI] Map nay khong co Goal hay Food nao de tim duong!')
            return

        final_goal = goals[0] if len(goals) > 0 else None
        algo_cls = {
            'DFS': DFS,
            'BFS': BFS,
            'UCS': UCS,
            'GREEDY': Greedy,
            'A*': AStar,
            'A* (h=0)': AStar
        }[algo]

        if len(foods) > 0:
            if len(foods) <= 12:
                problem = MultiGoal(spawn, tuple(foods), game_map, goal=final_goal, heuristic_fn=h_fn)
                searcher = algo_cls(problem)
                actions = searcher.search()
                exp_count = searcher.expanded_count
                time_cost = searcher.time_used
                path_cost = problem.measure_path_cost(actions) if actions is not None else 0
            else:
                actions, exp_count, time_cost = plan_multi_food_path(algo, spawn, foods, game_map, final_goal=final_goal)
                path_cost = len(actions) if actions is not None else 0
        elif len(goals) > 1:
            problem = MultiGoal(spawn, tuple(goals), game_map, goal=None, heuristic_fn=h_fn)
            searcher = algo_cls(problem)
            actions = searcher.search()
            exp_count = searcher.expanded_count
            time_cost = searcher.time_used
            path_cost = problem.measure_path_cost(actions) if actions is not None else 0
        else:
            problem = PMSearchProblem(spawn, goals[0], game_map, heuristic_fn=h_fn)
            searcher = algo_cls(problem)
            actions = searcher.search()
            exp_count = searcher.expanded_count
            time_cost = searcher.time_used
            path_cost = problem.measure_path_cost(actions) if actions is not None else 0

        print('\n=== KET QUA TIM KIEM (CLI - MUC 4) ===')
        print(f'Ban do (Map)                   : {map_path}')
        print(f'Thuat toan (Algorithm)         : {algo}')
        if actions is not None:
            print(f'Trang thai loi giai            : TIM THAY DUONG DI THANH CONG')
            print(f'So buoc di (Path Length)       : {len(actions)}')
            print(f'Tong chi phi (Path Cost)       : {path_cost}')
            print(f'So trang thai mo rong (Nodes)  : {exp_count}')
            print(f'Thoi gian chay (Time)          : {round(time_cost, 6)} giay ({round(time_cost * 1000, 2)} ms)')
            print(f'Chuoi hanh dong                : {actions}')
            print('\nBan do minh hoa duong di (* = vet buoc di):')
            in_ban_do_duong_di(game_map, spawn, actions, ghosts)
        else:
            print(f'Trang thai loi giai            : KHONG TIM THAY LOI GIAI (Unreachable)')
            print(f'So trang thai mo rong (Nodes)  : {exp_count}')
            print(f'Thoi gian chay (Time)          : {round(time_cost, 6)} giay ({round(time_cost * 1000, 2)} ms)')
        print('======================================')

    # 2. ADVERSARIAL SEARCH
    elif algo in ['MINIMAX', 'ALPHA-BETA']:
        if len(goals) == 0 and len(foods) == 0:
            print('[LOI] Map doi khang can co it nhat 1 Goal dich hoac Food!')
            return

        remaining_goals = list(goals)
        if len(foods) > 0:
            target = find_nearest_food(spawn, set(foods), game_map)
        elif len(remaining_goals) > 0:
            target = find_nearest_food(spawn, set(remaining_goals), game_map)
        else:
            target = None

        if mode == 'step':
            prob = AdvProblem(spawn, ghosts, target, game_map)
            ai = Minimax(prob, depth) if algo == 'MINIMAX' else AlphaBeta(prob, depth)
            action = ai.search()

            print('\n=== KET QUA QUYET DINH DOI KHANG BUOC DAU (CLI - MUC 4) ===')
            print(f'Ban do (Map)                   : {map_path}')
            print(f'Tac tu da dung (Agent)         : {algo}')
            print(f'Do sau tim kiem (Depth)        : {depth}')
            print(f'Hanh dong duoc chon (Action)   : {action}')
            print(f'Gia tri danh gia (Evaluation)  : {ai.last_value}')
            print(f'So trang thai da xet (Nodes)   : {ai.expanded_count}')
            print(f'Thoi gian ra quyet dinh (Time) : {round(ai.time_used, 6)} giay ({round(ai.time_used * 1000, 2)} ms)')
            print('===========================================================')
        else:
            ghosts_copy = list(ghosts)
            foods_copy = set(foods)
            state = GameState(spawn, ghosts_copy, foods_copy, 0, game_map)
            buoc = 0
            tong_nodes = 0
            tong_time = 0.0
            lich_su_actions = []
            lich_su_positions = [state.pacman_position]
            max_steps = max(100, len(foods) * 4) if len(foods) > 0 else 60

            while buoc < max_steps:
                if len(state.food) > 0:
                    target = find_nearest_food(state.pacman_position, state.food, game_map)
                elif len(remaining_goals) > 0:
                    target = find_nearest_food(state.pacman_position, set(remaining_goals), game_map)
                else:
                    target = None

                if target is None:
                    state.status = 'WIN'
                    break

                buoc += 1
                prob = AdvProblem(state.pacman_position, state.ghost_positions, target, game_map)
                recent = lich_su_positions[-8:]

                ai = Minimax(prob, depth, recent_positions=recent) if algo == 'MINIMAX' else AlphaBeta(prob, depth, recent_positions=recent)
                act = ai.search()
                tong_nodes += ai.expanded_count
                tong_time += ai.time_used
                if act is None:
                    break

                lich_su_actions.append(act)
                is_final = len(state.food) == 0 and len(remaining_goals) <= 1
                state = state.step(act, target, is_final_goal=is_final)
                lich_su_positions.append(state.pacman_position)

                if state.pacman_position in remaining_goals:
                    remaining_goals.remove(state.pacman_position)
                    state.score += 20
                if state.status == 'LOSE':
                    break
                if len(remaining_goals) == 0 and len(state.food) == 0:
                    state.status = 'WIN'
                    break
                else:
                    state.status = 'PLAYING'

            print('\n=== TONG KET MO PHONG DOI KHANG (CLI - MUC 4) ===')
            print(f'Ban do (Map)                   : {map_path}')
            print(f'Thuat toan (Algorithm)         : {algo}')
            print(f'Do sau tim kiem (Depth)        : {depth}')
            print(f'Ket qua tran dau               : {state.status}')
            print(f'Tong so buoc di chuyen         : {len(lich_su_actions)}')
            print(f'Chuoi hanh dong                : {lich_su_actions}')
            print(f'Tong so node da mo rong        : {tong_nodes}')
            print(f'Tong thoi gian tinh toan AI    : {round(tong_time, 5)} giay')
            print('=================================================')
    else:
        print(f'[LOI] Thuat toan khong hop le: {algo_name}')


def main():
    while True:
        print('====================================================')
        print('     PACMAN AI SEARCH & ADVERSARIAL - NHOM 07       ')
        print('   Hoc phan: Bieu dien tri thuc & Tim kiem nang cao  ')
        print('====================================================')
        print('1. Chay thuat toan truc quan tren Terminal (Search / Adversarial)')
        print('2. Khoi dong Giao dien Do hoa Arcade (Pygame UI)')
        print('3. Chay toan bo Thuc nghiem Danh gia Benchmark (Muc 5 De bai)')
        print('4. Thoat')
        lua_chon = input('Nhap lua chon cua ban (1-4, mac dinh 1): ').strip()

        if lua_chon == '2':
            from ui.main import run_ui
            run_ui()
            break
        elif lua_chon == '3':
            from src.utils.benchmark import run_search_benchmark, run_heuristic_evaluation, run_adversarial_benchmark
            run_search_benchmark()
            run_heuristic_evaluation()
            run_adversarial_benchmark()
            print('\n>>> HOAN TAT TOAN BO THUC NGHIEM BENCHMARK! <<<')
            input('\nNhan Enter de tiep tuc...')
            continue
        elif lua_chon in ['4', 'q', 'exit']:
            print('Tam biet!')
            break
        else:
            chay_terminal_menu()
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pacman AI Search - Nhom 07')
    parser.add_argument('--ui', action='store_true', help='Chay giao dien do hoa Vintage Arcade (Pygame)')
    parser.add_argument('--benchmark', action='store_true', help='Chay toan bo thuc nghiem benchmark (Muc 5) va xuat ket qua vao results/')
    parser.add_argument('--map', type=str, default=None, help='Duong dan toi file ban do .txt (vd: maps/test_map.txt)')
    parser.add_argument('--algo', type=str, default=None, help='Thuat toan: DFS, BFS, UCS, GREEDY, ASTAR, ASTAR_H0, MINIMAX, ALPHABETA')
    parser.add_argument('--depth', type=int, default=2, help='Do sau tim kiem cho Minimax / Alpha-Beta (mac dinh: 2)')
    parser.add_argument('--mode', type=str, default='match', choices=['step', 'match'], help='Che do doi khang: step (1 buoc) hoac match (mo phong tran)')

    args = parser.parse_args()

    if args.ui:
        from ui.main import run_ui
        run_ui()
    elif args.benchmark:
        from src.utils.benchmark import run_search_benchmark, run_heuristic_evaluation, run_adversarial_benchmark
        run_search_benchmark()
        run_heuristic_evaluation()
        run_adversarial_benchmark()
    elif args.map and args.algo:
        run_cli(args.map, args.algo, args.depth, args.mode)
    else:
        main()
