"""Tự động chạy thực nghiệm và xuất bảng so sánh hiệu năng thuật toán."""

import os
import sys
import time
import csv

# Dam bao import duoc src khi chay file truc tiep
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.map_loader import load_map
from src.utils.map_info import get_map_info
from src.search.pm_search_problem import PMSearchProblem
from src.search.multi_goal_search import MultiGoal
from src.search.dfs import DFS
from src.search.bfs import BFS
from src.search.ucs import UCS
from src.search.greedy import Greedy
from src.search.a_star import AStar
from src.logic_pacman_vs_ghost.adv_problem import AdvProblem
from src.logic_pacman_vs_ghost.minimax import Minimax
from src.logic_pacman_vs_ghost.alpha_beta import AlphaBeta


def run_search_benchmark():
    maps = [
        ('test_map', 'maps/test_map.txt'),
        ('large_map', 'maps/large_map.txt'),
        ('multi_food_and_final_goal', 'maps/multi_food_and_final_goal.txt'),
        ('multi_goal_test', 'maps/multi_goal_test.txt'),
        ('no_solution_map', 'maps/no_solution_map.txt'),
        ('terrain_cost_map', 'maps/terrain_cost_map.txt')
    ]
    algos = [('DFS', DFS), ('BFS', BFS), ('UCS', UCS), ('Greedy', Greedy), ('A*', AStar)]
    results = []

    print('=================================================================')
    print('      THUC NGHIEM SO SANH THUAT TOAN TIM KIEM (CLASSIC SEARCH)   ')
    print('=================================================================')

    for map_name, map_path in maps:
        gmap = load_map(map_path)
        if not gmap:
            continue

        spawn, goals, ghosts, foods = get_map_info(gmap, return_foods=True)
        final_goal = goals[0] if len(goals) > 0 else None

        for algo_name, algo_class in algos:
            if len(foods) > 0:
                problem = MultiGoal(spawn, tuple(foods), gmap, goal=final_goal)
            elif len(goals) > 1:
                problem = MultiGoal(spawn, tuple(goals), gmap, goal=None)
            else:
                target = goals[0] if goals else None
                problem = PMSearchProblem(spawn, target, gmap)

            searcher = algo_class(problem)
            actions = searcher.search()

            found = (actions is not None)
            steps = len(actions) if found else -1
            cost = problem.measure_path_cost(actions) if found else -1
            nodes = searcher.expanded_count
            time_ms = searcher.time_used * 1000.0

            results.append({
                'map': map_name,
                'algo': algo_name,
                'found': found,
                'steps': steps,
                'cost': cost,
                'nodes': nodes,
                'time_ms': round(time_ms, 3)
            })

            found_str = 'YES' if found else 'NO'
            steps_str = str(steps) if found else 'N/A'
            cost_str = str(cost) if found else 'N/A'
            print(f'[{map_name:17}] {algo_name:7} | Found: {found_str:3} | Steps: {steps_str:>4} | Cost: {cost_str:>4} | Nodes: {nodes:>5} | Time: {time_ms:>7.2f}ms')

    os.makedirs('results', exist_ok=True)
    csv_file = 'results/search_benchmark.csv'

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['map', 'algo', 'found', 'steps', 'cost', 'nodes', 'time_ms'])
        writer.writeheader()
        writer.writerows(results)

    txt_file = 'results/search_benchmark.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write('=' * 80 + '\n')
        f.write('BANG KET QUA THUC NGHIEM SO SANH THUAT TOAN TIM KIEM\n')
        f.write('=' * 80 + '\n')
        f.write(f"{'Map':<20} | {'Algorithm':<10} | {'Found':<6} | {'Steps':<7} | {'Cost':<7} | {'Nodes':<7} | {'Time (ms)':<10}\n")
        f.write('-' * 80 + '\n')
        for r in results:
            found_s = 'YES' if r['found'] else 'NO'
            steps_s = str(r['steps']) if r['found'] else 'N/A'
            cost_s = str(r['cost']) if r['found'] else 'N/A'
            f.write(f"{r['map']:<20} | {r['algo']:<10} | {found_s:<6} | {steps_s:<7} | {cost_s:<7} | {r['nodes']:<7} | {r['time_ms']:<10.2f}\n")

    print(f'\n-> Da luu ket qua vao: {csv_file} va {txt_file}\n')
    return results


def run_heuristic_evaluation():
    print('=================================================================')
    print('      THUC NGHIEM DANH GIA HEURISTIC (UCS vs A*(h=0) vs A*(h))   ')
    print('=================================================================')

    test_cases = [
        ('test_map (Single-Goal)', 'maps/test_map.txt', False),
        ('large_map (Single-Goal)', 'maps/large_map.txt', False),
        ('multi_goal_test (Multi-Goal)', 'maps/multi_goal_test.txt', True)
    ]
    results = []

    for name, path, is_multi in test_cases:
        gmap = load_map(path)
        spawn, goals, ghosts, foods = get_map_info(gmap, return_foods=True)

        if is_multi:
            prob_ucs = MultiGoal(spawn, tuple(goals), gmap)
            prob_a0 = MultiGoal(spawn, tuple(goals), gmap, heuristic_fn=lambda st: 0)
            prob_ah = MultiGoal(spawn, tuple(goals), gmap)
        else:
            prob_ucs = PMSearchProblem(spawn, goals[0], gmap)
            prob_a0 = PMSearchProblem(spawn, goals[0], gmap, heuristic_fn=lambda st: 0)
            prob_ah = PMSearchProblem(spawn, goals[0], gmap)

        s_ucs = UCS(prob_ucs)
        act_ucs = s_ucs.search()

        s_a0 = AStar(prob_a0)
        act_a0 = s_a0.search()

        s_ah = AStar(prob_ah)
        act_ah = s_ah.search()

        reduction = round((1.0 - s_ah.expanded_count / s_ucs.expanded_count) * 100, 1)

        res = {
            'test_case': name,
            'ucs_nodes': s_ucs.expanded_count,
            'ucs_time_ms': round(s_ucs.time_used * 1000, 2),
            'a0_nodes': s_a0.expanded_count,
            'a0_time_ms': round(s_a0.time_used * 1000, 2),
            'ah_nodes': s_ah.expanded_count,
            'ah_time_ms': round(s_ah.time_used * 1000, 2),
            'steps': len(act_ah),
            'reduction_pct': reduction
        }
        results.append(res)

        print(f'[{name}]')
        print(f'  UCS (no info)       : Nodes = {s_ucs.expanded_count:>5} | Time = {s_ucs.time_used * 1000:>6.2f}ms')
        print(f'  A* (h = 0)          : Nodes = {s_a0.expanded_count:>5} | Time = {s_a0.time_used * 1000:>6.2f}ms')
        print(f'  A* (proposed h)     : Nodes = {s_ah.expanded_count:>5} | Time = {s_ah.time_used * 1000:>6.2f}ms  (Giam: {reduction}%)')

    txt_file = 'results/heuristic_evaluation.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write('=' * 80 + '\n')
        f.write('DANH GIA HEURISTIC: SO SANH UCS, A*(h=0) VA A* VOI HEURISTIC DE XUAT\n')
        f.write('=' * 80 + '\n')
        f.write(f"{'Test Case':<30} | {'UCS Nodes':<10} | {'A*(h=0) Nodes':<14} | {'A*(h) Nodes':<12} | {'Reduction (%)':<12}\n")
        f.write('-' * 80 + '\n')
        for r in results:
            f.write(f"{r['test_case']:<30} | {r['ucs_nodes']:<10} | {r['a0_nodes']:<14} | {r['ah_nodes']:<12} | {r['reduction_pct']:<12}%\n")

    print(f'\n-> Da luu ket qua vao: {txt_file}\n')
    return results


def run_adversarial_benchmark():
    print('=================================================================')
    print('      THUC NGHIEM SO SANH DOI KHANG (MINIMAX vs ALPHA-BETA)      ')
    print('=================================================================')

    adv_maps = [
        ('adversarial_dead_end_trap', 'maps/adversarial_dead_end_trap.txt'),
        ('adversarial_small', 'maps/adversarial_small.txt'),
        ('test_map (2 Ghosts)', 'maps/test_map.txt'),
        ('large_map (3 Ghosts)', 'maps/large_map.txt')
    ]
    depths = [1, 2, 3]
    results = []

    for map_name, map_path in adv_maps:
        gmap = load_map(map_path)
        spawn, goals, ghosts, foods = get_map_info(gmap, return_foods=True)
        target = goals[0] if goals else foods[0] if foods else None
        prob = AdvProblem(spawn, ghosts, target, gmap)

        for d in depths:
            mm = Minimax(prob, depth_limit=d)
            act_mm = mm.search()
            val_mm = mm.last_value
            nodes_mm = mm.expanded_count
            time_mm = mm.time_used * 1000.0

            ab = AlphaBeta(prob, depth_limit=d)
            act_ab = ab.search()
            val_ab = ab.last_value
            nodes_ab = ab.expanded_count
            time_ab = ab.time_used * 1000.0

            match = (act_mm == act_ab and val_mm == val_ab)
            prune_pct = round((1.0 - nodes_ab / nodes_mm) * 100, 1) if nodes_mm > 0 else 0.0

            res = {
                'map': map_name,
                'depth': d,
                'act_mm': act_mm,
                'act_ab': act_ab,
                'val_mm': val_mm,
                'val_ab': val_ab,
                'nodes_mm': nodes_mm,
                'nodes_ab': nodes_ab,
                'time_mm_ms': round(time_mm, 2),
                'time_ab_ms': round(time_ab, 2),
                'prune_pct': prune_pct,
                'match': match
            }
            results.append(res)

            match_str = 'MATCH' if match else 'MISMATCH'
            print(f'[{map_name:26}] Depth {d} | MM: {nodes_mm:>5} nodes ({time_mm:>6.2f}ms) | AB: {nodes_ab:>5} nodes ({time_ab:>6.2f}ms) | Prune: {prune_pct:>5.1f}% | {match_str} (Act: {act_ab})')

    csv_file = 'results/adversarial_benchmark.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['map', 'depth', 'act_mm', 'act_ab', 'val_mm', 'val_ab', 'nodes_mm', 'nodes_ab', 'time_mm_ms', 'time_ab_ms', 'prune_pct', 'match'])
        writer.writeheader()
        writer.writerows(results)

    txt_file = 'results/adversarial_benchmark.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write('=' * 95 + '\n')
        f.write('BANG KET QUA THUC NGHIEM SO SANH MINIMAX VA ALPHA-BETA PRUNING\n')
        f.write('=' * 95 + '\n')
        f.write(f"{'Map':<26} | {'Depth':<5} | {'Action':<6} | {'Value':<8} | {'MM Nodes':<8} | {'AB Nodes':<8} | {'Pruning %':<10} | {'Speedup':<8}\n")
        f.write('-' * 95 + '\n')
        for r in results:
            speedup = round(r['time_mm_ms'] / max(0.001, r['time_ab_ms']), 2) if r['time_ab_ms'] > 0 else 1.0
            f.write(f"{r['map']:<26} | {r['depth']:<5} | {r['act_ab']:<6} | {r['val_ab']:<8} | {r['nodes_mm']:<8} | {r['nodes_ab']:<8} | {r['prune_pct']:<9}% | {speedup:<7}x\n")

    print(f'\n-> Da luu ket qua vao: {csv_file} va {txt_file}\n')
    return results


if __name__ == '__main__':
    run_search_benchmark()
    run_heuristic_evaluation()
    run_adversarial_benchmark()
    print('>>> HOAN TAT TOAN BO THUC NGHIEM BENCHMARK! <<<')
