# Kiến trúc Hybrid Memory Agent

Tôi xây dựng một POC cho trợ lý tiếng Việt có hai loại bộ nhớ. Bộ nhớ sự kiện lưu những nội dung người dùng từng đọc hoặc ghi chú. Hồ sơ ổn định lưu các đặc trưng ngắn gọn, chẳng hạn chủ đề quan tâm và ngôn ngữ ưu tiên.

```text
hội thoại / ghi chú
        |
        v
 chia đoạn + embedding --------------------------+
        |                                        |
        v                                        v
 vector store -- tìm theo user_id + độ liên quan --> ghép ngữ cảnh --> LLM
        ^                                        ^
        |                                        |
 hoạt động gần đây --> feature store -------- hồ sơ + hoạt động
```



## Quyết định 1: Chia đoạn theo tin nhắn hoặc đoạn văn

Tôi chọn chia bộ nhớ theo từng tin nhắn hoặc đoạn văn ngắn. Mỗi đoạn mang theo `user_id`, thời điểm tạo và văn bản gốc. Cách đơn giản hơn là lưu cả cuộc hội thoại thành một vector. Nó giảm số lượng vector và giữ được nhiều ngữ cảnh liền nhau, nhưng kết quả tìm kiếm dễ bị loãng khi cuộc hội thoại dài. Một đoạn chứa quá nhiều chủ đề cũng chiếm nhiều context window của LLM.

Đoạn ngắn giúp tìm đúng một chi tiết cụ thể và dễ xóa khi người dùng yêu cầu. Đổi lại, hệ thống phải lưu nhiều vector hơn và có thể mất mối liên hệ giữa hai tin nhắn cạnh nhau. Nếu triển khai thật, tôi sẽ gộp các tin nhắn liền kề khi chúng cùng chủ đề, sau đó giới hạn mỗi chunk theo số token. Với POC, đoạn ngắn là lựa chọn dễ kiểm tra và ít tạo kết quả nhiễu hơn.

## Quyết định 2: Hồ sơ dạng bảng thay vì embedding hồ sơ

Hồ sơ người dùng gồm `topic_affinity`, `preferred_language`, `reading_speed_wpm` và `queries_last_hour`. Tất cả dùng entity `user_id`. `preferred_language` lấy từ cài đặt trực tiếp của người dùng. `reading_speed_wpm` được tính từ sự kiện đọc. Hai đặc trưng còn lại đến từ lịch sử truy vấn và cần cập nhật thường xuyên hơn.

Tôi chọn feature dạng bảng vì các giá trị này cần dễ lọc, dễ giải thích và dùng được trong point-in-time join. Một embedding hồ sơ có thể nắm bắt sở thích tiềm ẩn tốt hơn, nhưng khó biết vì sao nó thay đổi sau mỗi lần huấn luyện hoặc lập chỉ mục lại. Tôi vẫn có thể thêm profile embedding sau này như một tín hiệu phụ, rồi ghép điểm với kết quả episodic memory bằng RRF. Ở phiên bản đầu, dữ liệu dạng bảng ít mơ hồ hơn.

## Quyết định 3: Độ mới tùy theo loại dữ liệu

Hoạt động gần đây cần được đẩy lên online store trong vài giây. Nếu người dùng vừa đọc tài liệu Kubernetes rồi hỏi “Tôi đang quan tâm gì?”, câu trả lời không nên chờ đến ngày hôm sau. `queries_last_hour` có TTL một giờ để dữ liệu cũ không bị hiểu nhầm là sở thích hiện tại.

`topic_affinity` có thể làm mới mỗi năm phút. Mức trễ này đủ cho gợi ý tài liệu, vì một vài phút thường không làm thay đổi chất lượng đề xuất đáng kể. `reading_speed_wpm` thay đổi chậm nên materialize hằng ngày là hợp lý. `preferred_language` là cài đặt rõ ràng của người dùng và không tự hết hạn. Tôi không dùng một lịch cập nhật chung cho mọi feature vì vừa tốn tài nguyên, vừa làm mất ý nghĩa của TTL.

## Tìm kiếm và ghép ngữ cảnh

Luồng recall lọc theo `user_id` trước khi xếp hạng. Đây là điểm tôi muốn giữ thật chặt. Nếu tìm trên toàn bộ collection rồi mới post-filter, payload của người khác vẫn có thể xuất hiện trong log hoặc trace. POC dùng một collection chung có payload `user_id`. Cách tạo collection riêng cho từng người cô lập mạnh hơn, nhưng sẽ khó quản lý khi số người dùng tăng.

Trong bản đầy đủ, tôi sẽ chạy BM25 và vector search rồi ghép bằng RRF. Feature profile không được chép vào từng memory vì cách đó tạo nhiều bản sao cũ. Context builder đọc feature mới nhất một lần, sau đó ghép với ba memory phù hợp nhất. Ba kết quả là mức vừa đủ cho demo. Lấy nhiều hơn có thể tăng recall, nhưng cũng tăng chi phí token và khiến LLM trộn các chi tiết không liên quan.

## Bối cảnh tiếng Việt

Người dùng Việt Nam thường trộn tiếng Việt với thuật ngữ tiếng Anh như Kubernetes, autoscaling hoặc IAM. Khi gõ trên điện thoại, họ cũng có thể bỏ dấu. Tách từ bằng khoảng trắng dùng được cho baseline nhỏ, nhưng chưa đủ cho môi trường thật. Tôi sẽ so sánh `underthesea` hoặc `pyvi` với embedding đa ngôn ngữ, rồi đo trên tập query có cả câu đủ dấu, không dấu và code-switching.

Dữ liệu ghi chú cá nhân có thể rất nhạy cảm. Cả vector store và feature store phải dùng cùng `user_id`, có thời hạn lưu và lưu vết thao tác xóa. Thiết kế thật cũng cần mã hóa dữ liệu và cơ chế đồng ý rõ ràng, phù hợp với yêu cầu bảo vệ dữ liệu cá nhân tại Việt Nam.

## Phương án đã cân nhắc nhưng không chọn

Tôi từng cân nhắc lưu episodic embedding trực tiếp trong feature store. Tôi không chọn cách đó vì hai loại dữ liệu có vòng đời khác nhau. Memory mới có thể xuất hiện từng phút và cần nearest-neighbour search. Hồ sơ thay đổi chậm hơn và chủ yếu cần lookup theo entity. Gộp chúng vào một hệ thống làm chu kỳ cập nhật và lập chỉ mục khó kiểm soát.

POC dùng hashed vector tự cài đặt để `python bonus/demo.py` chạy được trong một checkout sạch, không cần tải model hoặc khởi động Docker. Interface `remember()` và `recall()` vẫn giữ nguyên, nên có thể thay phần bên trong bằng Qdrant và Feast mà không đổi code gọi.

Nếu feature store tạm thời lỗi, agent vẫn trả episodic memory và đánh dấu profile chưa có dữ liệu. Nếu vector search lỗi, hệ thống có thể dùng keyword search làm phương án dự phòng. Khi cả hai nguồn đều lỗi, agent không nên giả vờ rằng nó nhớ người dùng.

POC hiện chưa xử lý mã hóa dữ liệu lưu trữ, đồng bộ nhiều thiết bị, gộp memory cũ hoặc giao diện xóa dữ liệu. Đây là những phần tôi sẽ làm trước khi xem hệ thống như một trợ lý cá nhân thật sự.