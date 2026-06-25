# QUY TRÌNH ÁP DỤNG AI TRONG DỰ ÁN

https://github\.com/obra/superpowers

> **Mã số tài liệu:** SOP\-DEV\-001
> **Phiên bản:** v1\.0\.0
> **Đối tượng áp dụng:** Toàn bộ Lập trình viên \(Developers\), Kiểm thử viên \(QA/QC\), Tech Lead và Quản lý dự án\.
> **Mục tiêu:** Loại bỏ hoàn toàn mã nguồn cẩu thả \(AI Slop\), nâng cao độ tin cậy của sản phẩm lên 100%, đồng bộ tài liệu hóa thiết kế và giảm thiểu tối đa thời gian sửa lỗi \(debugging\)\.
> 
> 

---

## 🛑 3 ĐIỀU LUẬT \(THE IRON LAWS\)

Mọi lập trình viên khi tham gia dự án **BẮT BUỘC** phải tuân thủ 3 điều luật này\. Vi phạm bất kỳ điều luật nào đồng nghĩa với việc Pull Request \(PR\) bị **từ chối lập tức**:

1. **KHÔNG CÓ SPEC, KHÔNG CÓ CODE:** Tuyệt đối không viết bất kỳ dòng code logic nào nếu chưa có file thiết kế \(Spec\) được phê duyệt bởi Tech Lead hoặc PM\.

2. **KHÔNG CÓ TEST LỖI, KHÔNG CÓ CODE PRODUCTION:** Mọi chức năng mới hoặc sửa lỗi đều phải bắt đầu bằng một test case chạy thất bại \(Red Phase\)\. Nếu bạn viết code trước khi có test, bạn phải **xóa code đó đi và làm lại**\.

3. **BẰNG CHỨNG TRƯỚC \- BÁO CÁO SAU:** Cấm sử dụng các cụm từ cảm tính như *"Em nghĩ là chạy được rồi"*, *"Hình như xong rồi"*\. Mọi tuyên bố hoàn thành phải đi kèm bằng chứng thực tế từ kết quả chạy test suite \(`0 failures`\) và linter sạch\.

---

## 🔄 QUY TRÌNH 5 BƯỚC PHÁT TRIỂN BẮT BUỘC

\[BƯỚC 1: Spec\] ──\> \[BƯỚC 2: Plan\] ──\> \[BƯỚC 3: Môi trường\] ──\> \[BƯỚC 4: TDD\] ──\> \[BƯỚC 5: Tích hợp\]

### 📝 BƯỚC 1: Động não \& Đặc tả thiết kế \(Brainstorming \& Spec\)

Trước khi làm bất kỳ task nào \(tính năng mới hoặc sửa lỗi phức tạp\):

1. **Thảo luận \& Làm rõ:** Dev phối hợp với Tech Lead/PM \(hoặc AI Agent\) để đặt câu hỏi làm rõ: Mục tiêu là gì? Giới hạn kỹ thuật? Các trường hợp biên \(edge cases\)?

2. **Viết Đặc tả \(Spec\):** Tạo file đặc tả thiết kế tại đường dẫn: `docs/superpowers/specs/YYYY-MM-DD-<ten-tinh-nang>-design.md`

3. **Nội dung Spec phải có:**

    - **Mục tiêu:** 1 câu ngắn gọn mô tả tính năng\.

    - **Kiến trúc dữ liệu:** Data flow, Database schema \(nếu có\)\.

    - **Giao diện/API:** Các endpoint, request/response payload, hoặc mô tả UI component\.

    - **Error Handling:** Cách hệ thống xử lý khi có lỗi xảy ra\.

4. **Phê duyệt:** Gửi file Spec cho Tech Lead/PM duyệt qua Git Pull Request hoặc review trực tiếp\. **Chỉ khi Spec được phê duyệt mới đi tiếp\.**

---

### 🗺️ BƯỚC 2: Lập kế hoạch thực thi chi tiết \(Implementation Plan\)

Sau khi Spec được duyệt, Dev phải lập một kế hoạch thực hiện "mịn" đến từng phút\.

1. **Tạo file Kế hoạch \(Plan\):** Tạo file tại: `docs/superpowers/plans/YYYY-MM-DD-<ten-tinh-nang>-plan.md`

2. **Phân rã thành các Task siêu nhỏ \(2\-5 phút thực hiện\):**

    - *Ví dụ không hợp lệ:* `Task 1: Code màn hình đăng nhập` \(Quá chung chung\)\.

    - *Ví dụ hợp lệ:*

        - `Task 1.1: Viết test lỗi xác thực email trống.`

        - `Task 1.2: Viết code tối thiểu để pass test email trống.`

        - `Task 1.3: Commit.`

3. **Mỗi Task bắt buộc phải chứa:**

    - Đường dẫn chính xác của file cần tạo/sửa\.

    - **Đoạn code test mẫu mong muốn\.**

    - Lệnh chạy kiểm thử cụ thể và kết quả mong đợi\.

4. **Duyệt kế hoạch:** Tech Lead/PM sẽ review nhanh qua file Plan này để đảm bảo Dev không bị đi lạc hướng\.

---

### 🛡️ BƯỚC 3: Tạo môi trường cô lập \(Isolated Workspace\)

Tránh việc code trực tiếp trên nhánh chính gây xung đột và hỏng hóc hệ thống hiện tại\.

1. **Sử dụng Git Worktree \(hoặc tạo Branch mới\):**

2. bash

# Tạo môi trường làm việc cô lập trên branch mới

1. git worktree add \.worktrees/feature\-\<ten\-tinh\-nang\> \-b feature/\<ten\-tinh\-nang\>

2. cd \.worktrees/feature\-\<ten\-tinh\-nang\>

3. **Cài đặt Dependency \& Thiết lập:** Chạy lệnh setup dự án để đảm bảo môi trường sạch\.

4. **Chạy Baseline Test:** Chạy test suite gốc của dự án để đảm bảo môi trường bắt đầu hoàn toàn sạch và không có lỗi từ trước\.

5. bash

6. npm test \# Hoặc lệnh tương đương của dự án

7. *\(Nếu baseline test lỗi, phải báo cáo ngay lập tức cho Tech Lead, không được tự ý sửa đè\)\.*

---

### 🔴🟢🔵 BƯỚC 4: Thực thi kỷ luật bằng TDD \& Xác thực lỗi \(TDD \& Verification\)

Đây là giai đoạn viết code chính\. Dev phải thực hiện theo vòng lặp **Red\-Green\-Refactor**:

🔴 RED: Viết test lỗi \-\> 🟢 GREEN: Viết code tối thiểu để pass test \-\> 🔵 REFACTOR: Tối ưu code

1. **🔴 RED Phase \(Viết test lỗi\):**

    - Viết một test case nhỏ kiểm tra hành vi mong muốn\.

    - Chạy test và **bắt buộc phải thấy test đó bị báo đỏ \(FAIL\)** do chưa có code xử lý logic\.

    - *Tại sao?* Nếu viết test xong chạy vẫn xanh \(PASS\), nghĩa là bạn đang test sai thứ hoặc test vô dụng\.

2. **🟢 GREEN Phase \(Viết code tối thiểu\):**

    - Viết đoạn code logic **đơn giản nhất, tối thiểu nhất** để test case trên chuyển sang màu xanh \(PASS\)\.

    - Cấm viết thêm các tính năng dư thừa không liên quan đến test case hiện tại \(Tuân thủ triệt để YAGNI \- You Aren't Gonna Need It\)\.

3. **🔵 REFACTOR Phase \(Tối ưu hóa\):**

    - Dọn dẹp code, tối ưu cấu trúc, xóa bỏ trùng lặp dữ liệu\.

    - Chạy lại test suite để đảm bảo code tối ưu vẫn chạy đúng \(vẫn xanh\)\.

4. **Tích xanh tiến độ:** Sau mỗi task hoàn thành, cập nhật trạng thái `- [x]` trong file `docs/superpowers/plans/YYYY-MM-DD-<ten-tinh-nang>-plan.md` và thực hiện `git commit`\.

---

### 🏁 BƯỚC 5: Hoàn thành \& Tích hợp \(Finishing \& Integration\)

Khi toàn bộ các task trong file Kế hoạch đã hoàn thành:

1. **Kiểm tra linter \& Xây dựng thử \(Build check\):**

2. bash

3. npm run lint  \# Đảm bảo code sạch lỗi format

4. npm run build \# Đảm bảo biên dịch thành công

5. **Chạy toàn bộ Test Suite toàn diện:** Đảm bảo tất cả các bài test \(cũ và mới\) đều xanh 100%\.

6. **Đẩy code \& Tạo Pull Request \(PR\):**

7. bash

8. git push \-u origin feature/\<ten\-tinh\-nang\>

    - Tạo PR trên GitHub/GitLab kèm theo mô tả ngắn gọn và liên kết tới file Spec và Plan đã duyệt\.

9. **Dọn dẹp môi trường \(Cleanup\):** Sau khi PR được merge thành công vào nhánh chính, tiến hành xóa bỏ worktree tạm thời để giải phóng dung lượng máy tính:

10. bash

11. git worktree remove \.worktrees/feature\-\<ten\-tinh\-nang\>

12. git worktree prune

---

## 🛠️ CẤU HÌNH PHỤ TRỢ CHO AI ASSISTANT \(CURSOR / VS CODE\)

Để các AI Assistant \(như Cursor, Copilot\) tự động ép dev tuân thủ quy trình này, hãy copy nội dung cấu hình sau vào tệp `.cursorrules` ở thư mục gốc của dự án:

json

\{

"name": "Superpowers SOP Rules",

"description": "Bắt buộc AI Agent tuân thủ quy trình Spec\-First, Plan\-First và TDD cực kỳ kỷ luật",

"globs": \["\*"\],

"alwaysApply": true,

"rules": \[

"1\. BẮT BUỘC KHỞI ĐỘNG BẰNG BRAINSTORMING: Khi nhận bất kỳ yêu cầu viết code nào, tuyệt đối CẤM viết code ngay lập tức\. Phải đặt câu hỏi làm rõ với người dùng, đề xuất 2\-3 giải pháp và viết file Spec vào `docs/superpowers/specs/` trước\.",

"2\. BẮT BUỘC LẬP KẾ HOẠCH BITE\-SIZED: Sau khi Spec được duyệt, viết file kế hoạch thực hiện vào `docs/superpowers/plans/` chia nhỏ thành các task 2\-5 phút\. Mỗi task bắt buộc phải ghi rõ file cần tạo/sửa và code test mong muốn\.",

"3\. BẮT BUỘC TUÂN THỦ TDD CHẶT CHẼ: Đối với mỗi task, phải viết test trước \(Red Phase\), chạy kiểm tra test lỗi, sau đó mới viết code production tối thiểu \(Green Phase\) và tối ưu \(Refactor\)\. Không viết code trước test\.",

"4\. BẰNG CHỨNG TRƯỚC \- BÁO CÁO SAU: Cấm báo cáo hoàn thành hoặc sử dụng các từ phỏng đoán như 'should', 'probably', 'seems to'\. Mọi báo cáo thành công phải đi kèm log chạy test thực tế pass 100%\."

\]

\}

---

## 📈 TIÊU CHÍ ĐÁNH GIÁ ĐỘ TUÂN THỦ \(AUDIT CHECKLIST\)

Tech Lead sẽ đánh giá chất lượng công việc của Dev dựa trên các tiêu chí sau:

- Có đầy đủ file **Spec** được phê duyệt trước ngày viết code\.

- Có đầy đủ file **Plan** được cập nhật tích xanh `- [x]` tiến độ\.

- **Test Coverage** của tính năng mới đạt tối thiểu **85%**\.

- Lịch sử commit rõ ràng, chia nhỏ theo từng task trong Plan\.

- Không chứa code thừa hoặc code giữ chỗ \(`TODO`, `TBD`, `implement later`\)\.

