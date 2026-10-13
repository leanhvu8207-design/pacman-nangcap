# BÁO CÁO PHÂN CÔNG NHIỆM VỤ VÀ LIÊM CHÍNH HỌC THUẬT
**Học phần:** Biểu diễn tri thức và tìm kiếm nâng cao (UET.AI2014)  
**Dự án 1:** Pacman — Tìm kiếm trong không gian trạng thái và Tìm kiếm đối kháng  
**Đơn vị:** Trường Đại học Công nghệ – Đại học Quốc gia Hà Nội (VNU-UET)  
**Nhóm thực hiện:** Nhóm 07  

---

## 1. Bảng phân công nhiệm vụ và Tỷ lệ đóng góp

| STT | Họ và tên | Mã sinh viên | Vai trò / Nhiệm vụ chính | Chi tiết công việc đã thực hiện | Tỷ lệ đóng góp | Chữ ký xác nhận |
| :---: | :--- | :---: | :--- | :--- | :---: | :---: |
| 1 | **Vũ Thanh Thanh Tùng** | *(Trưởng nhóm)* | Trưởng nhóm, Thiết kế hệ thống, Đối kháng & Giao diện | - Khởi tạo kiến trúc dự án và quy chuẩn module.<br>- Cài đặt thuật toán đối kháng Minimax & Alpha-Beta Pruning.<br>- Cải tiến hàm đánh giá đối kháng `evaluate()` (né ngõ cụt, BFS cache).<br>- Phát triển giao diện Pygame Retro Arcade mượt mà, đa luồng 60 FPS.<br>- Xây dựng bộ điều khiển `GameController` và tích hợp hệ thống. | 100% | *Đã ký* |
| 2 | **Bùi Chí Thành** | 25023046 | Thành viên, Tìm kiếm có thông tin & Mở rộng Multi-Goal | - Cài đặt thuật toán Greedy Best-First Search và $A^*$ Search.<br>- Thiết kế và chứng minh toán học Heuristic Manhattan (Admissible & Consistent).<br>- Cài đặt bài toán nhiều mục tiêu `MultiGoal`.<br>- Nghiên cứu và cài đặt Heuristic Cây khung nhỏ nhất Prim MST.<br>- Viết các ca kiểm thử cho tầng tìm kiếm có thông tin. | 100% | *Đã ký* |
| 3 | **Lê Anh Vũ** | *(Thành viên)* | Thành viên, Tìm kiếm không thông tin & Tầng dữ liệu | - Cài đặt thuật toán Depth-First Search (DFS), Breadth-First Search (BFS), Uniform-Cost Search (UCS).<br>- Cài đặt module nạp và kiểm định bản đồ (`map_loader.py`, `map_check_valid.py`).<br>- Xây dựng mô hình trạng thái bất biến `GameState` và trí tuệ nhân tạo của tác tử Ghost (`ghost.py`).<br>- Khắc phục các lỗi thứ tự ưu tiên Food/Goal trong game. | 100% | *Đã ký* |
| 4 | **Thành viên Nhóm 07** | *(Thành viên)* | Thành viên, Kiểm thử, Benchmark & Báo cáo đồ án | - Thiết kế bộ 22 bản đồ kiểm nghiệm đa dạng đặc tính.<br>- Xây dựng bộ 35 Unit Tests tự động đạt tỷ lệ Pass 100%.<br>- Viết script đo lường hiệu năng `benchmark.py` và xuất số liệu vào `results/`.<br>- Tổng hợp số liệu, phân tích biểu đồ và biên soạn Báo cáo đồ án `report.pdf`.<br>- Soạn thảo tài liệu hướng dẫn `README.md` và chuẩn bị nội dung vấn đáp. | 100% | *Đã ký* |

---

## 2. Cam kết Liêm chính học thuật (Academic Integrity Statement)

Tập thể Nhóm 07 xin cam đoan:
1. **Tính độc lập và tự chủ:** Toàn bộ mã nguồn của dự án (bao gồm cấu trúc dữ liệu, các thuật toán tìm kiếm DFS, BFS, UCS, Greedy, A*, Minimax, Alpha-Beta, hàm heuristic, hàm đánh giá và giao diện Pygame) đều do các thành viên trong nhóm tự thiết kế, tự xây dựng và kiểm thử.
2. **Không sao chép mã nguồn:** Nhóm tuyệt đối không sao chép, dịch ngược hoặc sử dụng mã nguồn có sẵn từ các nguồn như GitHub, CMU 15-281, UC Berkeley CS188 hoặc bài làm của các nhóm khác. Các tài liệu từ các khóa học nói trên chỉ được sử dụng cho mục đích tham khảo lý thuyết và hiểu đề bài.
3. **Hiểu rõ toàn bộ sản phẩm:** Mọi thành viên trong nhóm đều hiểu rõ kiến trúc tổng thể của hệ thống, nguyên lý hoạt động của từng thuật toán và sẵn sàng trả lời, giải thích chi tiết trong buổi vấn đáp trực tiếp với hội đồng giảng viên.

---

## 3. Khai báo sử dụng Công cụ Trí tuệ Nhân tạo (AI Declaration)

Tuân thủ nghiêm túc quy định tại **Mục 9 của Đề bài** về liêm chính học thuật và sử dụng AI, Nhóm 07 xin công khai minh bạch việc sử dụng công cụ AI như sau:

- **Công cụ sử dụng:** Các mô hình ngôn ngữ lớn (Google Gemini / ChatGPT).
- **Mục đích sử dụng:**
  1. Hỗ trợ rà soát cú pháp, tìm kiếm lỗi tiềm ẩn (syntax check, static code analysis).
  2. Gợi ý cấu trúc dàn ý bài báo cáo khoa học theo chuẩn học thuật.
  3. Hỗ trợ tra cứu nhanh cú pháp các hàm đồ họa của thư viện `pygame` (ví dụ: cách vẽ bề mặt bán trong suốt `pygame.SRCALPHA`, xử lý sự kiện cuộn chuột).
- **Phần nội dung do nhóm tự thực hiện hoàn toàn:**
  - Toàn bộ tư duy thuật toán, cấu trúc dữ liệu state space, logic đồ thị, cơ chế hàng đợi ưu tiên min-heap.
  - Lập luận và chứng minh toán học tính Admissible & Consistent của các hàm Heuristic.
  - Thiết kế và tinh chỉnh hàm đánh giá đối kháng né ngõ cụt (`evaluate()`).
  - Toàn bộ quá trình chạy thực nghiệm, thu thập số liệu và phân tích kết quả đo đạc.

---
*Hà Nội, ngày 13 tháng 10 năm 2026*  
**Đại diện Nhóm 07**  
*(Đã ký tên và xác nhận)*
