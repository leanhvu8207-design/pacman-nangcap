"""
Script Benchmark tu dong: Thu nghiem va do dac hieu nang thuat toan
Mon hoc: Bieu dien tri thuc va tim kiem nang cao (UET.AI2014) - Nhom 07

Tu dong chay va xuat file ket qua vao thu muc results/:
- results/search_benchmark.txt & results/search_benchmark.csv
- results/weighted_benchmark.txt & results/weighted_benchmark.csv
- results/heuristic_evaluation.txt
- results/adversarial_benchmark.txt & results/adversarial_benchmark.csv
"""

import os
import time
import csv

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
from src.logic_pacman_vs_ghost.expectimax import Expectimax


# Quy uoc chi phi dia hinh: '~' = 2, 'S' = 3, con lai = 1
TERRAIN_COSTS = {
    "~": 2,
    "S": 3,
}


def apply_cost_mode(problem, gmap, spawn, cost_mode="weighted"):
    """
    Ap dung che do chi phi cho Problem:
    - 'uniform' : Moi buoc di deu co chi phi = 1 (Chi phi dong nhat)
    - 'weighted': Tinh chi phi theo dia hinh '~' = 2, 'S' = 3 (Chi phi khong dong nhat)
    """
    def cell_cost(r, c):
        if cost_mode == "uniform":
            return 1
        ch = gmap[r][c]
        return TERRAIN_COSTS.get(ch, 1)

    if cost_mode == "uniform":
        problem.cost_fn = lambda pos: 1
    else:
        problem.cost_fn = lambda pos: cell_cost(pos[0], pos[1])
    return problem


def run_search_benchmark():
    maps = [
        # 1. Don muc tieu (Chi phi dong nhat)
        ("single_small_few_solvable", "maps/single_small_few_solvable.txt", "single"),
        ("dead_end_maze", "maps/dead_end_maze.txt", "single"),
        ("large_map (Single-Goal)", "maps/large_map.txt", "single"),
        ("no_solution_map", "maps/no_solution_map.txt", "single"),

        # 2. Nhieu muc tieu (Multi-Goal Search)
        ("multi_goal_test", "maps/multi_goal_test.txt", "multi"),
        ("multi_large_many_solvable", "maps/multi_large_many_solvable.txt", "multi"),
    ]

    algos = [
        ("DFS", DFS),
        ("BFS", BFS),
        ("UCS", UCS),
        ("Greedy", Greedy),
        ("A*", AStar),
    ]

    results = []

    print("=================================================================")
    print("   1. THUC NGHIEM SO SANH THUAT TOAN TIM KIEM (CLASSIC SEARCH)   ")
    print("=================================================================")

    for label, map_path, mode in maps:
        gmap = load_map(map_path)
        if not gmap:
            continue
        spawn, goals, ghosts, foods = get_map_info(gmap, return_foods=True)
        final_goal = goals[0] if len(goals) > 0 else None

        for algo_name, algo_class in algos:
            if mode == "multi":
                if len(foods) > 0:
                    problem = MultiGoal(spawn, tuple(foods), gmap, goal=final_goal)
                else:
                    problem = MultiGoal(spawn, tuple(goals), gmap, goal=None)
            else:
                problem = PMSearchProblem(spawn, final_goal, gmap)

            searcher = algo_class(problem)
            actions = searcher.search()

            found = actions is not None
            steps = len(actions) if found else -1
            cost = problem.measure_path_cost(actions) if found else -1
            nodes = searcher.expanded_count
            time_ms = searcher.time_used * 1000.0

            results.append({
                "map": label,
                "algo": algo_name,
                "found": found,
                "steps": steps,
                "cost": cost,
                "nodes": nodes,
                "time_ms": round(time_ms, 3)
            })

            found_str = "YES" if found else "NO"
            steps_str = str(steps) if found else "N/A"
            cost_str = str(cost) if found else "N/A"
            print(f"[{label:28}] {algo_name:7} | Found: {found_str:3} | Steps: {steps_str:>4} | Cost: {cost_str:>4} | Nodes: {nodes:>5} | Time: {time_ms:>7.2f}ms")

    os.makedirs("results", exist_ok=True)
    csv_file = "results/search_benchmark.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["map", "algo", "found", "steps", "cost", "nodes", "time_ms"])
        writer.writeheader()
        writer.writerows(results)

    txt_file = "results/search_benchmark.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("=" * 90 + "\n")
        f.write("BANG KET QUA THUC NGHIEM SO SANH THUAT TOAN TIM KIEM (NHOM 07)\n")
        f.write("=" * 90 + "\n")
        f.write(f"{'Map':<30} | {'Algorithm':<10} | {'Found':<6} | {'Steps':<7} | {'Cost':<7} | {'Nodes':<7} | {'Time (ms)':<10}\n")
        f.write("-" * 90 + "\n")
        for r in results:
            found_s = "YES" if r["found"] else "NO"
            steps_s = str(r["steps"]) if r["found"] else "N/A"
            cost_s = str(r["cost"]) if r["found"] else "N/A"
            f.write(f"{r['map']:<30} | {r['algo']:<10} | {found_s:<6} | {steps_s:<7} | {cost_s:<7} | {r['nodes']:<7} | {r['time_ms']:<10.2f}\n")

    print(f"\n-> Da luu ket qua vao: {csv_file} va {txt_file}\n")
    return results


def run_uniform_vs_weighted_benchmark():
    """
    Muc rieng: So sanh Chi phi Dong nhat (moi o = 1) vs Khong dong nhat ('~' = 2, 'S' = 3)
    """
    print("=================================================================")
    print("   2. THUC NGHIEM CHI PHI DONG NHAT vs KHONG DONG NHAT (~=2, S=3)")
    print("=================================================================")

    test_configs = [
        ("swamp_shortcut (Dong nhat)", "maps/weighted_swamp_shortcut_dilemma.txt", "single", "uniform"),
        ("swamp_shortcut (Khong dong nhat)", "maps/weighted_swamp_shortcut_dilemma.txt", "single", "weighted"),
        ("multi_wetlands (Dong nhat)", "maps/weighted_multi_food_wetlands.txt", "multi", "uniform"),
        ("multi_wetlands (Khong dong nhat)", "maps/weighted_multi_food_wetlands.txt", "multi", "weighted"),
    ]

    algos = [
        ("DFS", DFS),
        ("BFS", BFS),
        ("UCS", UCS),
        ("Greedy", Greedy),
        ("A*", AStar),
    ]

    results = []

    for label, map_path, mode, cost_mode in test_configs:
        gmap = load_map(map_path)
        if not gmap:
            continue
        spawn, goals, ghosts, foods = get_map_info(gmap, return_foods=True)
        final_goal = goals[0] if len(goals) > 0 else None

        for algo_name, algo_class in algos:
            if mode == "multi":
                if len(foods) > 0:
                    problem = MultiGoal(spawn, tuple(foods), gmap, goal=final_goal)
                else:
                    problem = MultiGoal(spawn, tuple(goals), gmap, goal=None)
            else:
                problem = PMSearchProblem(spawn, final_goal, gmap)

            problem = apply_cost_mode(problem, gmap, spawn, cost_mode=cost_mode)

            searcher = algo_class(problem)
            actions = searcher.search()

            found = actions is not None
            steps = len(actions) if found else -1
            cost = problem.measure_path_cost(actions) if found else -1
            nodes = searcher.expanded_count
            time_ms = searcher.time_used * 1000.0

            results.append({
                "map": label,
                "cost_mode": "Uniform (1)" if cost_mode == "uniform" else "Weighted (~=2,S=3)",
                "algo": algo_name,
                "found": found,
                "steps": steps,
                "cost": cost,
                "nodes": nodes,
                "time_ms": round(time_ms, 3)
            })

            found_str = "YES" if found else "NO"
            steps_str = str(steps) if found else "N/A"
            cost_str = str(cost) if found else "N/A"
            print(f"[{label:32}] {algo_name:7} | Found: {found_str:3} | Steps: {steps_str:>4} | Cost: {cost_str:>4} | Nodes: {nodes:>5} | Time: {time_ms:>7.2f}ms")

    os.makedirs("results", exist_ok=True)
    csv_file = "results/weighted_benchmark.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["map", "cost_mode", "algo", "found", "steps", "cost", "nodes", "time_ms"])
        writer.writeheader()
        writer.writerows(results)

    txt_file = "results/weighted_benchmark.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("=" * 100 + "\n")
        f.write("BANG SO SANH CHI PHI DONG NHAT (COST=1) VA KHONG DONG NHAT ('~'=2, 'S'=3) - NHOM 07\n")
        f.write("=" * 100 + "\n")
        f.write(f"{'Test Case (Map & Mode)':<34} | {'Algorithm':<10} | {'Found':<6} | {'Steps':<7} | {'Cost':<7} | {'Nodes':<7} | {'Time (ms)':<10}\n")
        f.write("-" * 100 + "\n")
        for r in results:
            found_s = "YES" if r["found"] else "NO"
            steps_s = str(r["steps"]) if r["found"] else "N/A"
            cost_s = str(r["cost"]) if r["found"] else "N/A"
            f.write(f"{r['map']:<34} | {r['algo']:<10} | {found_s:<6} | {steps_s:<7} | {cost_s:<7} | {r['nodes']:<7} | {r['time_ms']:<10.2f}\n")

    print(f"\n-> Da luu ket qua vao: {csv_file} va {txt_file}\n")
    return results


def run_heuristic_evaluation():
    print("=================================================================")
    print("   3. THUC NGHIEM DANH GIA HEURISTIC (UCS vs A*(h=0) vs A*(h))   ")
    print("=================================================================")

    test_cases = [
        ("single_small_few_solvable", "maps/single_small_few_solvable.txt", "single"),
        ("dead_end_maze (Single-Goal)", "maps/dead_end_maze.txt", "single"),
        ("large_map (Single-Goal)", "maps/large_map.txt", "single"),
        ("swamp_shortcut (Weighted)", "maps/weighted_swamp_shortcut_dilemma.txt", "single"),
        ("multi_goal_test (Multi-Goal)", "maps/multi_goal_test.txt", "multi"),
        ("multi_large_many_solvable", "maps/multi_large_many_solvable.txt", "multi"),
        ("multi_wetlands (Weighted)", "maps/weighted_multi_food_wetlands.txt", "multi"),
    ]

    results = []

    for name, path, mode in test_cases:
        gmap = load_map(path)
        if not gmap:
            continue
        spawn, goals, ghosts, foods = get_map_info(gmap, return_foods=True)
        final_goal = goals[0] if len(goals) > 0 else None

        if mode == "multi":
            if len(foods) > 0:
                prob_ucs = MultiGoal(spawn, tuple(foods), gmap, goal=final_goal)
                prob_a0 = MultiGoal(spawn, tuple(foods), gmap, goal=final_goal, heuristic_fn=lambda st: 0)
                prob_ah = MultiGoal(spawn, tuple(foods), gmap, goal=final_goal)
            else:
                prob_ucs = MultiGoal(spawn, tuple(goals), gmap, goal=None)
                prob_a0 = MultiGoal(spawn, tuple(goals), gmap, goal=None, heuristic_fn=lambda st: 0)
                prob_ah = MultiGoal(spawn, tuple(goals), gmap, goal=None)
        else:
            prob_ucs = PMSearchProblem(spawn, final_goal, gmap)
            prob_a0 = PMSearchProblem(spawn, final_goal, gmap, heuristic_fn=lambda st: 0)
            prob_ah = PMSearchProblem(spawn, final_goal, gmap)

        s_ucs = UCS(prob_ucs)
        act_ucs = s_ucs.search()

        s_a0 = AStar(prob_a0)
        act_a0 = s_a0.search()

        s_ah = AStar(prob_ah)
        act_ah = s_ah.search()

        reduction = round((1.0 - s_ah.expanded_count / s_ucs.expanded_count) * 100, 1) if s_ucs.expanded_count > 0 else 0.0
        steps = len(act_ah) if act_ah is not None else -1

        res = {
            "test_case": name,
            "ucs_nodes": s_ucs.expanded_count,
            "ucs_time_ms": round(s_ucs.time_used * 1000, 2),
            "a0_nodes": s_a0.expanded_count,
            "a0_time_ms": round(s_a0.time_used * 1000, 2),
            "ah_nodes": s_ah.expanded_count,
            "ah_time_ms": round(s_ah.time_used * 1000, 2),
            "steps": steps,
            "reduction_pct": reduction
        }
        results.append(res)

        print(f"[{name}]")
        print(f"  UCS (no info)       : Nodes = {s_ucs.expanded_count:>5} | Time = {s_ucs.time_used*1000:>6.2f}ms")
        print(f"  A* (h = 0)          : Nodes = {s_a0.expanded_count:>5} | Time = {s_a0.time_used*1000:>6.2f}ms")
        print(f"  A* (proposed h)     : Nodes = {s_ah.expanded_count:>5} | Time = {s_ah.time_used*1000:>6.2f}ms  (Giam: {reduction}%)")

    os.makedirs("results", exist_ok=True)
    txt_file = "results/heuristic_evaluation.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("=" * 85 + "\n")
        f.write("DANH GIA HEURISTIC: SO SANH UCS, A*(h=0) VA A* VOI HEURISTIC DE XUAT\n")
        f.write("=" * 85 + "\n")
        f.write(f"{'Test Case':<30} | {'UCS Nodes':<10} | {'A*(h=0) Nodes':<14} | {'A*(h) Nodes':<12} | {'Reduction (%)':<12}\n")
        f.write("-" * 85 + "\n")
        for r in results:
            f.write(f"{r['test_case']:<30} | {r['ucs_nodes']:<10} | {r['a0_nodes']:<14} | {r['ah_nodes']:<12} | {r['reduction_pct']:<12}%\n")

    print(f"\n-> Da luu ket qua vao: {txt_file}\n")
    return results


def run_adversarial_benchmark():
    print("=================================================================")
    print("   4. THUC NGHIEM SO SANH DOI KHANG (MINIMAX, ALPHA-BETA, EXPECTIMAX)")
    print("=================================================================")

    adv_maps = [
        ("adversarial_small (1 Ghost)", "maps/adversarial_small.txt"),
        ("dead_end_maze (1 Ghost)", "maps/dead_end_maze.txt"),
        ("large_map (3 Ghosts)", "maps/large_map.txt"),
    ]

    depths = [1, 2, 3]
    results = []

    for map_name, map_path in adv_maps:
        gmap = load_map(map_path)
        if not gmap:
            continue
        spawn, goals, ghosts, foods = get_map_info(gmap, return_foods=True)
        if len(foods) > 0:
            target = min(foods, key=lambda f: abs(spawn[0] - f[0]) + abs(spawn[1] - f[1]))
        elif len(goals) > 0:
            target = goals[0]
        else:
            target = None

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

            ex = Expectimax(prob, depth_limit=d)
            act_ex = ex.search()
            val_ex = ex.last_value
            nodes_ex = ex.expanded_count
            time_ex = ex.time_used * 1000.0

            match = (act_mm == act_ab) and (val_mm == val_ab)
            prune_pct = round((1.0 - nodes_ab / nodes_mm) * 100, 1) if nodes_mm > 0 else 0.0

            res = {
                "map": map_name,
                "depth": d,
                "act_mm": act_mm,
                "act_ab": act_ab,
                "act_ex": act_ex,
                "val_mm": val_mm,
                "val_ab": val_ab,
                "val_ex": val_ex,
                "nodes_mm": nodes_mm,
                "nodes_ab": nodes_ab,
                "nodes_ex": nodes_ex,
                "time_mm_ms": round(time_mm, 2),
                "time_ab_ms": round(time_ab, 2),
                "time_ex_ms": round(time_ex, 2),
                "prune_pct": prune_pct,
                "match": match
            }
            results.append(res)

            match_str = "MATCH" if match else "MISMATCH"
            print(f"[{map_name:28}] Depth {d} | MM: {nodes_mm:>5} ({time_mm:>5.2f}ms) | AB: {nodes_ab:>5} ({time_ab:>5.2f}ms, -{prune_pct:>4.1f}%) | EX: {nodes_ex:>5} ({time_ex:>5.2f}ms) | {match_str}")

    os.makedirs("results", exist_ok=True)
    csv_file = "results/adversarial_benchmark.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "map", "depth", "act_mm", "act_ab", "act_ex", "val_mm", "val_ab", "val_ex",
            "nodes_mm", "nodes_ab", "nodes_ex", "time_mm_ms", "time_ab_ms", "time_ex_ms", "prune_pct", "match"
        ])
        writer.writeheader()
        writer.writerows(results)

    txt_file = "results/adversarial_benchmark.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("=" * 116 + "\n")
        f.write("BANG KET QUA THUC NGHIEM SO SANH MINIMAX, ALPHA-BETA PRUNING VA EXPECTIMAX (NHOM 07)\n")
        f.write("=" * 116 + "\n")
        f.write(f"{'Map':<28} | {'Depth':<5} | {'Action':<6} | {'Value':<8} | {'MM Nodes':<8} | {'AB Nodes':<8} | {'EX Nodes':<8} | {'AB Prune%':<10} | {'AB Speedup':<10}\n")
        f.write("-" * 116 + "\n")
        for r in results:
            speedup = round(r["time_mm_ms"] / max(0.001, r["time_ab_ms"]), 2) if r["time_ab_ms"] > 0 else 1.0
            f.write(f"{r['map']:<28} | {r['depth']:<5} | {str(r['act_ab']):<6} | {r['val_ab']:<8} | {r['nodes_mm']:<8} | {r['nodes_ab']:<8} | {r['nodes_ex']:<8} | {r['prune_pct']:<9}% | {speedup:<9}x\n")

    print(f"\n-> Da luu ket qua vao: {csv_file} va {txt_file}\n")
    return results


if __name__ == "__main__":
    run_search_benchmark()
    run_uniform_vs_weighted_benchmark()
    run_heuristic_evaluation()
    run_adversarial_benchmark()
    print(">>> HOAN TAT TOAN BO THUC NGHIEM BENCHMARK! <<<")
