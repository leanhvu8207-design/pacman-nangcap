"""Chương trình chính Pacman: Giao diện dòng lệnh chạy tìm kiếm và đối kháng."""

import sys
import time
import argparse
from collections import deque
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
from src.logic_ghost.adv_problem import AdvProblem
from src.logic_ghost.minimax import Minimax
from src.logic_ghost.alpha_beta import AlphaBeta


def find_nearest_food(pos, food_set, game_map):
    if len(food_set) == 0:
        return None
    queue = deque()
    queue.append(pos)
    visited = set()
    visited.add(pos)
    move_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while len(queue) > 0:
        current_coord = queue.popleft()
        if current_coord in food_set:
            return current_coord
        curr_r = current_coord[0]
        curr_c = current_coord[1]

        for dr, dc in move_directions:
            nr = curr_r + dr
            nc = curr_c + dc
            if nr >= 0 and nr < len(game_map):
                if nc >= 0 and nc < len(game_map[nr]):
                    neighbor_coord = (nr, nc)
                    cell_char = game_map[nr][nc]
                    is_not_wall = cell_char != '#'
                    is_unvisited = neighbor_coord not in visited
                    if is_not_wall and is_unvisited:
                        visited.add(neighbor_coord)
                        queue.append(neighbor_coord)
    best_food = None
    min_manhattan_dist = float('inf')
    pacman_r = pos[0]
    pacman_c = pos[1]

    for food_pos in food_set:
        fr = food_pos[0]
        fc = food_pos[1]
        dist = abs(pacman_r - fr) + abs(pacman_c - fc)
        if dist < min_manhattan_dist:
            min_manhattan_dist = dist
            best_food = food_pos
    return best_food


def plan_multi_food_path(algo_name, spawn, foods, game_map, final_goal=None):
    remaining_foods = set(foods)
    current_position = spawn
    remaining_foods.discard(current_position)
    all_actions = []
    total_expanded_nodes = 0
    start_time = time.time()

    while len(remaining_foods) > 0:
        next_food_target = None
        min_dist = float('inf')
        curr_r = current_position[0]
        curr_c = current_position[1]

        for food_pos in remaining_foods:
            fr = food_pos[0]
            fc = food_pos[1]
            dist = abs(curr_r - fr) + abs(curr_c - fc)
            if dist < min_dist:
                min_dist = dist
                next_food_target = food_pos
        if current_position == next_food_target:
            remaining_foods.discard(current_position)
            continue
        sub_problem = PMSearchProblem(current_position, next_food_target, game_map)
        if algo_name == 'DFS':
            searcher = DFS(sub_problem)
        elif algo_name == 'BFS':
            searcher = BFS(sub_problem)
        elif algo_name == 'UCS':
            searcher = UCS(sub_problem)
        elif algo_name == 'GREEDY':
            searcher = Greedy(sub_problem)
        else:
            searcher = AStar(sub_problem)
        sub_actions = searcher.search()
        if sub_actions is None:
            break
        all_actions.extend(sub_actions)
        total_expanded_nodes = total_expanded_nodes + searcher.expanded_count
        track_r = current_position[0]
        track_c = current_position[1]
        remaining_foods.discard((track_r, track_c))

        for act in sub_actions:
            if act == 'UP':
                track_r = track_r - 1
            elif act == 'DOWN':
                track_r = track_r + 1
            elif act == 'LEFT':
                track_c = track_c - 1
            elif act == 'RIGHT':
                track_c = track_c + 1
            remaining_foods.discard((track_r, track_c))
        current_position = (track_r, track_c)
        remaining_foods.discard(current_position)
    if final_goal is not None and current_position != final_goal:
        sub_problem = PMSearchProblem(current_position, final_goal, game_map)
        if algo_name == 'DFS':
            searcher = DFS(sub_problem)
        elif algo_name == 'BFS':
            searcher = BFS(sub_problem)
        elif algo_name == 'UCS':
            searcher = UCS(sub_problem)
        elif algo_name == 'GREEDY':
            searcher = Greedy(sub_problem)
        else:
            searcher = AStar(sub_problem)
        sub_actions = searcher.search()
        if sub_actions is not None:
            all_actions.extend(sub_actions)
            total_expanded_nodes = total_expanded_nodes + searcher.expanded_count
    elapsed_time = time.time() - start_time
    return (all_actions, total_expanded_nodes, elapsed_time)


def in_ban_do(game_map, pacman_pos, ghost_positions, target_pos, remaining_food=None):
    total_rows = len(game_map)

    for r in range(total_rows):
        row_str = ''
        total_cols = len(game_map[r])

        for c in range(total_cols):
            pos = (r, c)
            if pos == pacman_pos:
                row_str = row_str + 'P '
            elif pos in ghost_positions:
                row_str = row_str + '@ '
            elif pos == target_pos:
                row_str = row_str + 'G '
            elif remaining_food is not None:
                if pos in remaining_food:
                    row_str = row_str + '. '
                else:
                    char_in_map = game_map[r][c]
                    if char_in_map in ['P', '@', 'G', '.']:
                        row_str = row_str + '  '
                    else:
                        row_str = row_str + char_in_map + ' '
            else:
                char_in_map = game_map[r][c]
                if char_in_map in ['P', '@', 'G']:
                    row_str = row_str + '  '
                else:
                    row_str = row_str + char_in_map + ' '
        print('  ' + row_str)


def main():
    print('=========================================')
    print('   DO AN PACMAN AI SEARCH - NHOM 07      ')
    print('=========================================')
    print('\n--- CHON BAN DO ---')
    print('1. maps/test_map.txt (Map chuan co 2 Ghost)')
    print('2. maps/adversarial_small.txt (Map nho co 1 Ghost)')
    print('3. maps/multi_goal_test.txt (Map nhieu Goal Food)')
    print('4. maps/multi_food_and_final_goal.txt (Map nhieu Food va Goal cuoi)')
    print('5. maps/large_map.txt (Map lon 19x22 danh gia mo rong)')
    print('6. maps/adversarial_dead_end_trap.txt (Map bay ngo cut)')
    print('7. maps/no_solution_map.txt (Map khong co loi giai)')
    print('8. maps/bad_map.txt (Map loi de test kiem dinh)')
    print('9. Tu nhap duong dan file map khac (.txt)')
    chon_map = input('Nhap lua chon ban do (1-9): ').strip()
    file_map = 'maps/test_map.txt'
    game_map = None
    if chon_map == '1':
        file_map = 'maps/test_map.txt'
        game_map = load_map(file_map)
    elif chon_map == '2':
        file_map = 'maps/adversarial_small.txt'
        game_map = load_map(file_map)
    elif chon_map == '3':
        file_map = 'maps/multi_goal_test.txt'
        game_map = load_map(file_map)
    elif chon_map == '4':
        file_map = 'maps/multi_food_and_final_goal.txt'
        game_map = load_map(file_map)
    elif chon_map == '5':
        file_map = 'maps/large_map.txt'
        game_map = load_map(file_map)
    elif chon_map == '6':
        file_map = 'maps/adversarial_dead_end_trap.txt'
        game_map = load_map(file_map)
    elif chon_map == '7':
        file_map = 'maps/no_solution_map.txt'
        game_map = load_map(file_map)
    elif chon_map == '8':
        file_map = 'maps/bad_map.txt'
        game_map = load_map(file_map)
    elif chon_map == '9':
        file_map = input('Nhap duong dan file map (.txt): ').strip()
        game_map = load_map(file_map)
    else:
        print('Nhap sai, tu dong chon maps/test_map.txt')
        file_map = 'maps/test_map.txt'
        game_map = load_map(file_map)
    if game_map is None:
        print('\n[LOI] Khong the load duoc map tu file:', file_map)
        return
    spawn, goals, ghosts, foods = get_map_info(game_map, return_foods=True)
    print('\nThong tin ban do:')
    print('  File:', file_map)
    print('  Pacman Spawn (P):', spawn)
    print('  Goals (G):', goals if len(goals) > 0 else 'Khong co (hoac Food la muc tieu)')
    print('  Foods (.):', foods if len(foods) > 0 else 'Khong co')
    print('  Ghosts (@):', ghosts if len(ghosts) > 0 else 'Khong co')
    print('\n--- CHON THUAT TOAN ---')
    print('1. DFS')
    print('2. BFS')
    print('3. UCS')
    print('4. Greedy Best-First')
    print('5. A*')
    print('6. Minimax')
    print('7. Alpha-Beta')
    thuat_toan = input('Chon thuat toan (1-7): ').strip()
    if thuat_toan in ['1', '2', '3', '4', '5']:
        if len(goals) == 0 and len(foods) == 0:
            print('[LOI] Map nay khong co Goal hay Food nao de tim duong!')
            return

        if thuat_toan == '1':
            ten_tt = 'DFS'
        elif thuat_toan == '2':
            ten_tt = 'BFS'
        elif thuat_toan == '3':
            ten_tt = 'UCS'
        elif thuat_toan == '4':
            ten_tt = 'GREEDY'
        else:
            ten_tt = 'A*'
        actions = None
        exp_count = 0
        time_cost = 0.0
        path_cost = 0
        if len(foods) > 0:
            if len(goals) > 0:
                final_goal = goals[0]
            else:
                final_goal = None
            if final_goal is not None:
                msg_goal = f' va ve Goal tai {final_goal}'
            else:
                msg_goal = ''
            print(f'\n[Che do Multi-Food] An het toan bo {len(foods)} vien Food (.){msg_goal} la chien thang!')
            if len(foods) <= 12:
                problem = MultiGoal(spawn, tuple(foods), game_map, goal=final_goal)

                if thuat_toan == '1':
                    searcher = DFS(problem)
                elif thuat_toan == '2':
                    searcher = BFS(problem)
                elif thuat_toan == '3':
                    searcher = UCS(problem)
                elif thuat_toan == '4':
                    searcher = Greedy(problem)
                else:
                    searcher = AStar(problem)
                print('\nDang chay thuat toan:', ten_tt, '...')
                actions = searcher.search()
                exp_count = searcher.expanded_count
                time_cost = searcher.time_used
                if actions is not None:
                    path_cost = problem.measure_path_cost(actions)
            else:
                print(f'\nDang lap ke hoach an sach {len(foods)} vien Food (.) voi {ten_tt}...')
                actions, exp_count, time_cost = plan_multi_food_path(ten_tt, spawn, foods, game_map, final_goal=final_goal)
                if actions is not None:
                    path_cost = len(actions)
                else:
                    path_cost = 0
        elif len(goals) > 1:
            problem = MultiGoal(spawn, tuple(goals), game_map, goal=None)
            print(f'\n[Che do Multi-Goal] Di qua tat ca {len(goals)} vi tri Goal (G)!')

            if thuat_toan == '1':
                searcher = DFS(problem)
            elif thuat_toan == '2':
                searcher = BFS(problem)
            elif thuat_toan == '3':
                searcher = UCS(problem)
            elif thuat_toan == '4':
                searcher = Greedy(problem)
            else:
                searcher = AStar(problem)
            print('\nDang chay thuat toan:', ten_tt, '...')
            actions = searcher.search()
            exp_count = searcher.expanded_count
            time_cost = searcher.time_used
            if actions is not None:
                path_cost = problem.measure_path_cost(actions)
        else:
            problem = PMSearchProblem(spawn, goals[0], game_map)
            print(f'\n[Che do Single-Goal] Tim duong toi Goal (G) tai {goals[0]}!')

            if thuat_toan == '1':
                searcher = DFS(problem)
            elif thuat_toan == '2':
                searcher = BFS(problem)
            elif thuat_toan == '3':
                searcher = UCS(problem)
            elif thuat_toan == '4':
                searcher = Greedy(problem)
            else:
                searcher = AStar(problem)
            print('\nDang chay thuat toan:', ten_tt, '...')
            actions = searcher.search()
            exp_count = searcher.expanded_count
            time_cost = searcher.time_used
            if actions is not None:
                path_cost = problem.measure_path_cost(actions)
        print('\n=== KET QUA TIM KIEM ===')
        print('Thuat toan:', ten_tt)
        if actions is not None:
            print('Trang thai: Tim thay duong di thanh cong!')
            print('So buoc di:', len(actions))
            print('Tong chi phi (Path Cost):', path_cost)
            print('Chuoi hanh dong:', actions)
        else:
            print('Trang thai: Khong tim thay duong di toi dich!')
        print('So node da duyet (expanded_count):', exp_count)
        print('Thoi gian chay (time_used):', round(time_cost, 6), 'giay')
    elif thuat_toan in ['6', '7']:
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

        if thuat_toan == '6':
            ten_tt = 'Minimax'
        else:
            ten_tt = 'Alpha-Beta'
        if len(ghosts) >= 2:
            default_depth = 3
        else:
            default_depth = 2
        depth_input = input(f'\nNhap do sau tim kiem depth (mac dinh {default_depth}): ').strip()
        if depth_input.isdigit() and int(depth_input) >= 1:
            depth_limit = int(depth_input)
        else:
            depth_limit = default_depth
        print('\nChon che do:')
        print('  1. Chi tinh nuoc di tot nhat o buoc dau tien (Step)')
        print('  2. Chay mo phong tran dau tung buoc (Match Simulation)')
        che_do = input('Chon che do (1 hoac 2, mac dinh 2): ').strip()
        if che_do == '1':
            prob = AdvProblem(spawn, ghosts, target, game_map)

            if thuat_toan == '6':
                ai = Minimax(prob, depth_limit)
            else:
                ai = AlphaBeta(prob, depth_limit)
            action = ai.search()
            print('\n=== KET QUA QUYET DINH BUOC DAU ===')
            print('Thuat toan:', ten_tt)
            print('Do sau (depth):', depth_limit)
            print('Hanh dong tot nhat:', action)
            print('Gia tri danh gia (last_value):', ai.last_value)
            print('So node da duyet:', ai.expanded_count)
            print('Thoi gian tinh:', round(ai.time_used, 6), 'giay')
            return
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
        if len(foods) > 0:
            max_steps = max(100, len(foods) * 4)
        else:
            max_steps = 60

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
            buoc = buoc + 1
            prob = AdvProblem(state.pacman_position, state.ghost_positions, target, game_map)
            recent = lich_su_positions[-8:]

            if thuat_toan == '6':
                ai = Minimax(prob, depth_limit, recent_positions=recent)
            else:
                ai = AlphaBeta(prob, depth_limit, recent_positions=recent)
            act = ai.search()
            tong_nodes = tong_nodes + ai.expanded_count
            tong_time = tong_time + ai.time_used
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
            if len(foods) > 0:
                info_score = f' | Score: {state.score}'
                info_food = f' | Food con lai: {len(state.food)}'
            else:
                info_score = ''
                info_food = ''
            print(f'  Diem eval: {ai.last_value}{info_score}{info_food} | Nodes: {ai.expanded_count} | Time: {round(ai.time_used, 5)}s')
            in_ban_do(game_map, state.pacman_position, state.ghost_positions, target, state.food)
            if len(state.food) < prev_food_count:
                print(f'  [+] Da an Food tai {state.pacman_position}! Con lai {len(state.food)} Food')
            if state.pacman_position in remaining_goals:
                remaining_goals.remove(state.pacman_position)
                state.score = state.score + 20
                print(f'  [+] Da thu thap Goal! Con {len(remaining_goals)} Goal')
            if state.status == 'LOSE':
                print('\n>>> THUA CUOC: PACMAN DA BI GHOST BAT! <<<')
                break
            da_het_goal = len(remaining_goals) == 0
            da_het_food = len(state.food) == 0
            if da_het_goal and da_het_food:
                print('\n>>> CHIEN THANG: PACMAN DA HOAN THANH TAT CA MUC TIEU! <<<')
                state.status = 'WIN'
                break
            else:
                state.status = 'PLAYING'
            time.sleep(0.04)
        print('\n================ TONG KET MO PHONG ================')
        print('Thuat toan:', ten_tt)
        print('Ket qua:', state.status)
        print('Tong so buoc di:', len(lich_su_actions))
        print('Chuoi hanh dong:', lich_su_actions)
        print('Tong so node da mo rong:', tong_nodes)
        print('Tong thoi gian tinh toan AI:', round(tong_time, 5), 'giay')
        print('====================================================')
    else:
        print('Lua chon khong hop le!')


def run_cli(map_path, algo_name, depth=2, mode='match'):
    game_map = load_map(map_path)
    if game_map is None:
        print(f'[LOI] Khong the load duoc map tu file: {map_path}')
        return
    spawn, goals, ghosts, foods = get_map_info(game_map, return_foods=True)
    algo = algo_name.upper()
    if algo == 'ASTAR':
        algo = 'A*'
    elif algo == 'ALPHABETA' or algo == 'ALPHA_BETA':
        algo = 'ALPHA-BETA'
    if algo in ['DFS', 'BFS', 'UCS', 'GREEDY', 'A*']:
        if len(goals) == 0 and len(foods) == 0:
            print('[LOI] Map nay khong co Goal hay Food nao de tim duong!')
            return
        if len(goals) > 0:
            final_goal = goals[0]
        else:
            final_goal = None
        if len(foods) > 0:
            if len(foods) <= 12:
                problem = MultiGoal(spawn, tuple(foods), game_map, goal=final_goal)
                if algo == 'DFS':
                    searcher = DFS(problem)
                elif algo == 'BFS':
                    searcher = BFS(problem)
                elif algo == 'UCS':
                    searcher = UCS(problem)
                elif algo == 'GREEDY':
                    searcher = Greedy(problem)
                else:
                    searcher = AStar(problem)
                actions = searcher.search()
                exp_count = searcher.expanded_count
                time_cost = searcher.time_used
                if actions is not None:
                    path_cost = problem.measure_path_cost(actions)
                else:
                    path_cost = 0
            else:
                actions, exp_count, time_cost = plan_multi_food_path(algo, spawn, foods, game_map, final_goal=final_goal)
                if actions is not None:
                    path_cost = len(actions)
                else:
                    path_cost = 0
        elif len(goals) > 1:
            problem = MultiGoal(spawn, tuple(goals), game_map, goal=None)
            if algo == 'DFS':
                searcher = DFS(problem)
            elif algo == 'BFS':
                searcher = BFS(problem)
            elif algo == 'UCS':
                searcher = UCS(problem)
            elif algo == 'GREEDY':
                searcher = Greedy(problem)
            else:
                searcher = AStar(problem)
            actions = searcher.search()
            exp_count = searcher.expanded_count
            time_cost = searcher.time_used
            if actions is not None:
                path_cost = problem.measure_path_cost(actions)
            else:
                path_cost = 0
        else:
            problem = PMSearchProblem(spawn, goals[0], game_map)
            if algo == 'DFS':
                searcher = DFS(problem)
            elif algo == 'BFS':
                searcher = BFS(problem)
            elif algo == 'UCS':
                searcher = UCS(problem)
            elif algo == 'GREEDY':
                searcher = Greedy(problem)
            else:
                searcher = AStar(problem)
            actions = searcher.search()
            exp_count = searcher.expanded_count
            time_cost = searcher.time_used
            if actions is not None:
                path_cost = problem.measure_path_cost(actions)
            else:
                path_cost = 0
        print('\n=== KET QUA TIM KIEM (CLI) ===')
        print(f'Map: {map_path}')
        print(f'Thuat toan: {algo}')
        if actions is not None:
            print(f'Trang thai: Tim thay duong di thanh cong!')
            print(f'So buoc di: {len(actions)}')
            print(f'Tong chi phi (Path Cost): {path_cost}')
            print(f'Chuoi hanh dong: {actions}')
        else:
            print(f'Trang thai: Khong tim thay duong di toi dich!')
        print(f'So node da duyet (expanded_count): {exp_count}')
        print(f'Thoi gian chay (time_used): {round(time_cost, 6)} giay')
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
            if algo == 'MINIMAX':
                ai = Minimax(prob, depth)
            else:
                ai = AlphaBeta(prob, depth)
            action = ai.search()
            print('\n=== KET QUA QUYET DINH BUOC DAU (CLI) ===')
            print(f'Map: {map_path}')
            print(f'Thuat toan: {algo}')
            print(f'Do sau (depth): {depth}')
            print(f'Hanh dong tot nhat: {action}')
            print(f'Gia tri danh gia (last_value): {ai.last_value}')
            print(f'So node da duyet: {ai.expanded_count}')
            print(f'Thoi gian tinh: {round(ai.time_used, 6)} giay')
        else:
            ghosts_copy = list(ghosts)
            foods_copy = set(foods)
            state = GameState(spawn, ghosts_copy, foods_copy, 0, game_map)
            buoc = 0
            tong_nodes = 0
            tong_time = 0.0
            lich_su_actions = []
            lich_su_positions = [state.pacman_position]
            if len(foods) > 0:
                max_steps = max(100, len(foods) * 4)
            else:
                max_steps = 60

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
                buoc = buoc + 1
                prob = AdvProblem(state.pacman_position, state.ghost_positions, target, game_map)
                recent = lich_su_positions[-8:]
                if algo == 'MINIMAX':
                    ai = Minimax(prob, depth, recent_positions=recent)
                else:
                    ai = AlphaBeta(prob, depth, recent_positions=recent)
                act = ai.search()
                tong_nodes = tong_nodes + ai.expanded_count
                tong_time = tong_time + ai.time_used
                if act is None:
                    break
                lich_su_actions.append(act)
                is_final = len(state.food) == 0 and len(remaining_goals) <= 1
                state = state.step(act, target, is_final_goal=is_final)
                lich_su_positions.append(state.pacman_position)
                if state.pacman_position in remaining_goals:
                    remaining_goals.remove(state.pacman_position)
                    state.score = state.score + 20
                if state.status == 'LOSE':
                    break
                if len(remaining_goals) == 0 and len(state.food) == 0:
                    state.status = 'WIN'
                    break
                else:
                    state.status = 'PLAYING'
            print('\n=== TONG KET MO PHONG DOI KHANG (CLI) ===')
            print(f'Map: {map_path}')
            print(f'Thuat toan: {algo}')
            print(f'Do sau (depth): {depth}')
            print(f'Ket qua: {state.status}')
            print(f'Tong so buoc di: {len(lich_su_actions)}')
            print(f'Chuoi hanh dong: {lich_su_actions}')
            print(f'Tong so node da mo rong: {tong_nodes}')
            print(f'Tong thoi gian tinh toan AI: {round(tong_time, 5)} giay')
    else:
        print(f'[LOI] Thuat toan khong hop le: {algo_name}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pacman AI Search - Nhom 07')
    parser.add_argument('--ui', action='store_true', help='Chay giao dien do hoa Vintage Arcade (Pygame)')
    parser.add_argument('--map', type=str, default=None, help='Duong dan toi file ban do .txt (vd: maps/test_map.txt)')
    parser.add_argument('--algo', type=str, default=None, help='Thuat toan: DFS, BFS, UCS, GREEDY, ASTAR, MINIMAX, ALPHABETA')
    parser.add_argument('--depth', type=int, default=2, help='Do sau tim kiem cho Minimax / Alpha-Beta (mac dinh: 2)')
    parser.add_argument('--mode', type=str, default='match', choices=['step', 'match'], help='Che do doi khang: step (1 buoc) hoac match (mo phong tran)')
    args = parser.parse_args()
    if args.ui:
        from ui.main import run_ui
        run_ui()
    elif args.map and args.algo:
        run_cli(args.map, args.algo, args.depth, args.mode)
    else:
        main()
