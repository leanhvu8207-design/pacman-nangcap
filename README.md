# Dự án 1: Pacman - Tìm kiếm và trò chơi đối kháng

- **Môn học:** Biểu diễn tri thức và tìm kiếm nâng cao (UET.AI2014_5)
- **Đơn vị:** Trường Đại học Công nghệ - ĐHQGHN (UET-VNU)
- **Nhóm thực hiện:** Nhóm 07
- Chi tiết thành viên và phân công công việc xem tại [CONTRIBUTIONS.md](CONTRIBUTIONS.md).

---

## 1. Giới thiệu

Bài tập lớn mô phỏng lại trò chơi Pacman nhằm cài đặt và thử nghiệm các thuật toán tìm kiếm đường đi (Search) và tìm kiếm đối kháng (Adversarial Search):

1. **Tìm kiếm cổ điển (Classic Search):**
   - Hỗ trợ tìm đường đơn mục tiêu (Single-goal) và gom nhiều thức ăn (Multi-goal).
   - Hỗ trợ bản đồ có trọng số địa hình: Nước (`~`, chi phí 2) và Đầm lầy (`S`, chi phí 3).
   - Cài đặt 5 thuật toán: DFS, BFS, UCS, Greedy Best-First Search và A*.
   - Với bài toán gom nhiều thức ăn (Multi-goal), hàm heuristic kết hợp khoảng cách đến thức ăn gần nhất và Cây khung nhỏ nhất (MST) để đảm bảo tính admissible và tìm được đường đi tối ưu.

2. **Tìm kiếm đối kháng (Adversarial Search):**
   - Mô phỏng đối đầu giữa Pacman (MAX) và các Ghost (MIN).
   - Cài đặt thuật toán Minimax và Alpha-Beta Pruning.
   - Hàm đánh giá trạng thái (Evaluation Function) tính toán dựa trên:
     - Khoảng cách BFS thực tế trong mê cung tới thức ăn và Ghost.
     - Giữ khoảng cách an toàn trước Ghost.
     - Tránh đi vào ngõ cụt khi Ghost đang ở gần.
     - Phạt điểm khi lặp vị trí (tránh việc Pacman đứng lắc qua lắc lại).

3. **Giao diện:**
   - Giao diện đồ họa bằng Pygame: hiển thị bản đồ trực quan, cho phép chọn thuật toán, điều chỉnh tốc độ, chạy từng bước (step), tạm dừng và theo dõi log.
   - Giao diện dòng lệnh (CLI): hỗ trợ cả menu tương tác trực tiếp lẫn chạy qua tham số command-line.

---

## 2. Cấu trúc thư mục

```text
P1_Nhom07/
├── main.py                     # File chạy chính (CLI interactive, CLI có tham số, mở GUI)
├── requirements.txt            # Thư viện phụ thuộc (pygame)
├── README.md                   # Hướng dẫn sử dụng
├── CONTRIBUTIONS.md            # Bảng phân công công việc của nhóm
├── report.pdf                  # Bản báo cáo về dự án của nhóm
├── test_part.py                # Script chạy thử nhanh các thuật toán tìm kiếm
│
├── src/                        # Mã nguồn thuật toán và logic trò chơi
│   ├── search/                 # Các thuật toán tìm kiếm cổ điển
│   │   ├── pm_search_problem.py  # Không gian trạng thái bài toán đơn mục tiêu
│   │   ├── multi_goal_search.py  # Bài toán gom nhiều thức ăn (kèm MST heuristic)
│   │   ├── dfs.py              # Depth-First Search
│   │   ├── bfs.py              # Breadth-First Search
│   │   ├── ucs.py              # Uniform-Cost Search
│   │   ├── greedy.py           # Greedy Best-First Search
│   │   └── a_star.py           # A* Search
│   │
│   ├── logic_pacman_vs_ghost/  # Module tìm kiếm đối kháng
│   │   ├── adv_problem.py      # Trạng thái đối kháng & hàm đánh giá evaluate()
│   │   ├── minimax.py          # Thuật toán Minimax
│   │   └── alpha_beta.py       # Thuật toán cắt tỉa Alpha-Beta
│   │
│   ├── pacman/
│   │   └── game_state.py       # Quản lý trạng thái trò chơi (tọa độ P, Ghost, Food, điểm)
│   ├── ghost/
│   │   └── ghost.py            # Logic di chuyển của Ghost
│   └── utils/
│       ├── map_loader.py       # Đọc map từ file .txt
│       ├── map_info.py         # Trích xuất dữ liệu map (P, G, Food, Ghost, chi phí ô)
│       ├── map_check_valid.py  # Kiểm tra tính hợp lệ của map
│       └── benchmark.py        # Đo thời gian chạy và số node mở rộng
│
├── ui/                         # Giao diện đồ họa (Pygame)
│   ├── main.py                 # Vòng lặp chính của giao diện
│   ├── controller.py           # Điều khiển luồng chạy nền (threading) tránh đơ UI
│   ├── renderer.py             # Vẽ map, Pacman, Ghost
│   ├── components.py           # Các thành phần UI (nút bấm, slider, danh sách map, log box)
│   └── theme.py                # Bảng màu và font hiển thị
│
├── maps/                       # Các file map kiểm thử (.txt)
├── results/                    # Kết quả chạy benchmark (CSV, TXT)
└── tests/                      # Bộ unit tests
```

---

## 3. Quy ước bản đồ (.txt)

| Ký hiệu | Ý nghĩa | Chi phí bước vào |
|:-------:|:--------|:----------------:|
| `#` | Tường / Vật cản (không thể đi qua) | Không thể đi |
| ` ` | Đường đi trống | 1 |
| `P` | Vị trí xuất phát của Pacman | 1 |
| `.` | Thức ăn (Food) | 1 |
| `G` | Đích đến (Goal) | 1 |
| `@` | Vị trí xuất phát của Ghost | 1 |
| `~` | Vùng nước (Water) | 2 |
| `S` | Vùng đầm lầy (Swamp) | 3 |

---

## 4. Cài đặt và chạy chương trình

### 4.1. Cài đặt môi trường

Yêu cầu Python 3.10 trở lên.

```bash
# 1. Tạo môi trường ảo (tùy chọn)
python -m venv .venv

# 2. Kích hoạt môi trường ảo:
# Trên Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Trên Linux/macOS:
# source .venv/bin/activate

# 3. Cài đặt các thư viện cần thiết:
pip install -r requirements.txt
```

---

### 4.2. Chạy giao diện đồ họa (GUI)

Để mở giao diện trực quan bằng Pygame:

```bash
python main.py --ui
```
Hoặc:
```bash
python -m ui.main
```

Một số phím tắt trong giao diện:
- `Enter`: Bắt đầu chạy
- `Space`: Tạm dừng / Tiếp tục
- `S`: Đi từng bước một (Step)
- `R`: Đặt lại trạng thái ban đầu (Reset)
- `Esc`: Thoát chương trình
- `Cuộn chuột`: Cuộn xem các dòng trong ô nhật ký (Log)

---

### 4.3. Chạy giao diện dòng lệnh (CLI)

#### Cách 1: Menu tương tác
Chạy trực tiếp lệnh bên dưới và làm theo menu lựa chọn hiển thị trên terminal:
```bash
python main.py
```

#### Cách 2: Truyền tham số dòng lệnh
Phù hợp khi cần chạy nhanh hoặc kiểm thử script:

- **Các thuật toán tìm kiếm đường đi (DFS, BFS, UCS, GREEDY, ASTAR):**
  ```bash
  python main.py --map maps/cost_large_single.txt --algo ASTAR
  python main.py --map maps/multi_large_many_solvable.txt --algo BFS
  ```

- **Chế độ đối kháng Pacman vs Ghost (MINIMAX, ALPHABETA):**
  ```bash
  # Mô phỏng cả trận với độ sâu depth = 2:
  python main.py --map maps/adversarial_small.txt --algo MINIMAX --depth 2

  # Chạy thuật toán Alpha-Beta với depth = 3:
  python main.py --map maps/adversarial_small.txt --algo ALPHABETA --depth 3

  # Tính và in ra duy nhất 1 bước đi tiếp theo:
  python main.py --map maps/adversarial_small.txt --algo ALPHABETA --depth 2 --mode step
  ```

---

### 4.4. Kiểm thử và Benchmark

- **Chạy toàn bộ unit test:**
  ```bash
  python -m unittest discover tests
  ```

- **Chạy đo hiệu năng thuật toán (Benchmark):**
  ```bash
  python -m src.utils.benchmark
  ```
  Kết quả benchmark sẽ được tự động xuất ra thư mục `results/`:
  - `results/search_benchmark.csv` và `.txt`
  - `results/adversarial_benchmark.csv` và `.txt`
  - `results/heuristic_evaluation.txt`
