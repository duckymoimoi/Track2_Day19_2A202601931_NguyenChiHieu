# Reflection - Lab 19

**Tên:** *Nguyễn Chí Hiếu*

**Cohort:** *K3*

**Path:** *lite*

Trên golden set 50 queries, hybrid RRF với k=60 có Precision@10 trung bình cao nhất: 78.6%, so với BM25 77.8% và semantic 73.2%.

BM25 phù hợp nhất với exact queries, đạt 96.7% vì query chứa đúng tên kỹ thuật trong tài liệu. Paraphrase queries khó hơn: semantic đạt khoảng 24%, còn BM25 đạt 33.3%. Đây là giới hạn của bge-small-en-v1.5 với tiếng Việt, không phải lỗi của RRF. Mixed queries cho thấy hybrid hữu ích nhất, đạt 100%, cao hơn BM25 97% và semantic 98.5%.

Tôi không dùng hybrid cho log search hoặc tra lỗi khi query luôn có exact keyword. BM25 lúc đó nhanh và dễ debug. Với recommendation hoặc paraphrase đa ngôn ngữ, tôi sẽ chọn vector search cùng model multilingual mạnh hơn.

Điều bất ngờ nhất là embedding model có thể quan trọng hơn retrieval strategy. Hybrid không bù hoàn toàn được embedding tiếng Việt yếu.

## Bonus challenge

- [x] Đã làm bonus (xem `bonus/`)
- [ ] Pair work với: _<tên đồng đội nếu có>_
