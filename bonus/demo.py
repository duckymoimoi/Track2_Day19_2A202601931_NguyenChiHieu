import sys

from agent import HybridMemoryAgent

def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    agent = HybridMemoryAgent()
    for note in ["Tôi đã đọc về Kubernetes autoscaling và HPA.", "Tôi quan tâm đến bảo mật cloud, IAM và quản lý secret.", "Tôi thích tài liệu tiếng Việt có ví dụ ngắn.", "Gần đây tôi đang so sánh serverless với container."]:
        agent.remember(note)
    for i, query in enumerate(["Tôi đã đọc gì về Kubernetes?", "Recommend đọc gì tiếp", "Tôi đang quan tâm gì gần đây?", "Tài liệu về tự động mở rộng hạ tầng?", "Cho tôi summary cloud security"], 1):
        print(f"\n[{i}] {query}\n{agent.recall(query)}")

if __name__ == "__main__":
    main()
