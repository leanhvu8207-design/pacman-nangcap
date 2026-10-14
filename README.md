# 🎮 DỰ ÁN 1: PACMAN AI SEARCH & ĐỐI KHÁNG

> **Môn học:** Biểu diễn tri thức và Tìm kiếm  
> **Đơn vị:** Trường Đại học Công nghệ – ĐHQGHN (VNU-UET)  
> **Nhóm thực hiện:** Nhóm 07

---

## 📌 1. Giới thiệu tổng quan
Dự án mô phỏng trò chơi kinh điển **Pacman**, ứng dụng các thuật toán Trí tuệ Nhân tạo trong tìm kiếm đường đi và trò chơi đối kháng nhiều tác tử (Multi-agent Game).

Dự án gồm 2 phần trọng tâm:
1. **Tìm kiếm cổ điển (Classic Search):**
   - Hỗ trợ bản đồ **Đơn mục tiêu (Single-Goal)** và **Nhiều mục tiêu (Multi-Goal / Gom toàn bộ thức ăn)**.
   - Hỗ trợ bản đồ có **trọng số địa hình (Weighted Terrains)**: Nước (`~`, chi phí 2) và Đầm lầy (`S`, chi phí 3).
   - Triển khai 5 thuật toán: **DFS, BFS, UCS, Greedy Best-First Search, A\***.
   - Heuristic tối ưu cho Multi-Goal kết hợp khoảng cách tới thức ăn gần nhất và **Cây khung nhỏ nhất (Minimum Spanning Tree - MST)**.

2. **Tìm kiếm đối kháng (Adversarial Search):**
   - Pacman (MAX agent) đối đầu với các Con ma / Ghost (MIN agents).
   - Triển khai thuật toán **Minimax** và **Alpha-Beta Pruning**.
   - Hàm đánh giá trạng thái (Evaluation Function) nâng cao:
     * Khoảng cách mê cung thực tế (BFS Maze Distance) tới mục tiêu.
     * Vùng an toàn đối với Ghost (Ghost Danger Zone).
     * Tránh ngõ cụt (Dead-end Trap avoidance).
     * Phạt lặp vị trí (Loop / Oscillation Penalty).

3. **Giao diện người dùng (Vintage Arcade UI):**
   - Đồ họa Pygame mang phong cách Cabinet Arcade thập niên 80-90.
   - Hỗ trợ tương tác chuột 100%, chọn map trực quan, điều chỉnh tốc độ, chạy từng bước (Step-by-step), xem trước mini-map.

---

## 📁 2. Cấu trúc thư mục dự án

```text
P1_Nhom07_TEST_FIX/
│
├── main.py                     # Entrypoint chính: CLI tương tác, CLI dòng lệnh, khởi chạy UI
├── requirements.txt            # Danh sách thư viện phụ thuộc (Pygame)
├── README.md                   # Tài liệu hướng dẫn chi tiết dự án
├── CONTRIBUTIONS.md            # Báo cáo phân công thành viên nhóm 07
├── test_part.py                # Script chạy thử nhanh các thuật toán tìm kiếm
│
├── src/                        # Mã nguồn backend cốt lõi
│   ├── search/                 # Module các thuật toán tìm kiếm cổ điển
│   │   ├── pm_search_problem.py  # Định nghĩa không gian trạng thái tìm kiếm (Single-Goal)
│   │   ├── multi_goal_search.py  # Bài toán tìm kiếm gom nhiều thức ăn (MST Heuristic)
│   │   ├── dfs.py              # Depth-First Search
│   │   ├── bfs.py              # Breadth-First Search
│   │   ├── ucs.py              # Uniform-Cost Search
│   │   ├── greedy.py           # Greedy Best-First Search
│   │   └── a_star.py           # A* Search
│   │
│   ├── logic_pacman_vs_ghost/  # Module tìm kiếm đối kháng (Game Theory)
│   │   ├── adv_problem.py      # Định nghĩa bài toán Pacman vs Ghost & Hàm heuristic evaluate()
│   │   ├── minimax.py          # Thuật toán Minimax
│   │   └── alpha_beta.py       # Thuật toán Alpha-Beta Pruning
│   │
│   ├── pacman/
│   │   └── game_state.py       # Biểu diễn trạng thái trò chơi (Vị trí P, Ghost, Thức ăn, Điểm)
│   ├── ghost/
│   │   └── ghost.py            # Hành vi tác tử Ghost
│   └── utils/
│       ├── map_loader.py       # Đọc và phân tích file bản đồ text (.txt)
│       ├── map_info.py         # Trích xuất tọa độ P, G, Food, Ghost & Chi phí địa hình
│       ├── map_check_valid.py  # Kiểm tra tính hợp lệ của bản đồ
│       └── benchmark.py        # Benchmark tự động đo thời gian & node mở rộng
│
├── ui/                         # Module giao diện đồ họa Vintage Arcade (Pygame)
│   ├── main.py                 # Game loop Pygame, bắt sự kiện chuột & phím
│   ├── controller.py           # Điều phối chạy nền (Threading) tránh treo UI
│   ├── renderer.py             # Vẽ mê cung, vector Pacman há miệng, Ghost nhiều màu
│   ├── components.py           # Button, Slider, Map Browser, Tabs, Log Box
│   └── theme.py                # Palette màu Retro, font chữ hiển thị
│
├── maps/                       # Các file bản đồ (.txt) kịch bản kiểm thử
├── results/                    # Kết quả đo đạc benchmark (CSV, TXT)
└── tests/                      # Bộ 30 Unit Tests tự động (unittest)
```

---

## 🗺️ 3. Quy ước ký hiệu trên Bản đồ (.txt)

| Ký hiệu | Ý nghĩa | Chi phí bước vào (Cost) |
|:-------:|:--------|:-----------------------:|
| `#` | Tường / Vật cản (Không thể đi vào) | $\infty$ |
| ` ` | Đường đi trống trải | 1 |
| `P` | Vị trí xuất phát của Pacman | 1 |
| `.` | Viên thức ăn (Food pellet) | 1 |
| `G` | Điểm đích (Goal) | 1 |
| `@` | Vị trí ban đầu của Ghost (Con ma) | 1 |
| `~` | Vùng nước ngập (Water) | **2** |
| `S` | Vùng đầm lầy (Swamp) | **3** |

---

## 🚀 4. Hướng dẫn cài đặt & Khởi chạy

### 4.1. Cài đặt môi trường
Yêu cầu: **Python 3.10+** (đã kiểm thử ổn định trên Python 3.10 - 3.13).

```bash
# 1. Tạo môi trường ảo (khuyến nghị)
python -m venv .venv

# 2. Kích hoạt môi trường ảo:
# Trên Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Trên Linux/macOS:
# source .venv/bin/activate

# 3. Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

---

### 4.2. Chạy Giao diện Đồ họa (GUI)
Để trải nghiệm trực quan toàn bộ tính năng với giao diện Vintage Arcade:

```bash
python main.py --ui
# Hoặc:
python -m ui.main
```

**Các phím tắt trên giao diện:**
- `Enter`: Bắt đầu mô phỏng (Start)
- `Space`: Tạm dừng / Tiếp tục (Pause / Resume)
- `S`: Đi duy nhất 1 bước (Step)
- `R`: Đặt lại trạng thái ban đầu (Reset)
- `Esc`: Thoát ứng dụng
- `Cuộn chuột`: Cuộn nhật ký hoạt động (Log Box)

---

### 4.3. Chạy giao diện Dòng lệnh (CLI)

#### Cách 1: Menu CLI tương tác (Interactive Terminal)
Chạy trực tiếp file `main.py` không tham số:
```bash
python main.py
```
Hệ thống sẽ hiển thị menu cho phép bạn nhập số để chọn map và chọn thuật toán.

#### Cách 2: Chạy trực tiếp 1 dòng lệnh (One-line CLI)
Hỗ trợ kiểm thử nhanh hoặc tích hợp script tự động:

* **Tìm kiếm đường đi cổ điển (DFS, BFS, UCS, GREEDY, ASTAR):**
  ```bash
  python main.py --map maps/cost_large_single.txt --algo ASTAR
  python main.py --map maps/multi_large_many_solvable.txt --algo BFS
  ```

* **Chế độ đối kháng Pacman vs Ghost (MINIMAX, ALPHABETA):**
  ```bash
  # Mô phỏng cả trận (match) với độ sâu tìm kiếm depth=2:
  python main.py --map maps/adversarial_small.txt --algo MINIMAX --depth 2

  # Tối ưu thời gian duyệt bằng cắt tỉa Alpha-Beta:
  python main.py --map maps/adversarial_small.txt --algo ALPHABETA --depth 3

  # Tính toán gợi ý duy nhất 1 nước đi tiếp theo (step):
  python main.py --map maps/adversarial_small.txt --algo ALPHABETA --depth 2 --mode step
  ```

---

### 4.4. Chạy Benchmark & Kiểm thử tự động

* **Chạy kiểm thử toàn bộ 30 Unit Tests:**
  ```bash
  python -m unittest discover tests
  ```

* **Chạy bộ Benchmark đo lường hiệu năng thuật toán:**
  ```bash
  python -m src.utils.benchmark
  ```
  Kết quả benchmark sẽ tự động xuất ra thư mục `results/` gồm các file:
  - `results/search_benchmark.csv` & `.txt`
  - `results/adversarial_benchmark.csv` & `.txt`
  - `results/heuristic_evaluation.txt`
