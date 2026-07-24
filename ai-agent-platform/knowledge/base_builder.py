# knowledge/base_builder.py
import chromadb
import os
import yaml
from pathlib import Path

class KnowledgeBaseBuilder:
    """知識庫構建器 — 初始化 Agent 的 RAG 知識來源"""

    def __init__(self, chromadb_url: str = "http://chromadb:8000"):
        self.client = chromadb.HttpClient(host=chromadb_url)  # 連接 ChromaDB 向量數據庫

    def seed_hr_policies(self):
        """初始化 HR 政策文檔到向量數據庫"""
        collection = self.client.get_or_create_collection(
            name="hr_policies",
            metadata={"hnsw:space": "cosine"}  # 使用餘弦相似度進行語義搜索
        )

        hr_docs = [
            {
                "id": "onboarding_v1",
                "document": """# 新員工入職流程

## 流程步驟
1. HR 創建員工記錄（姓名、部門、職位、入職日期）
2. 分配員工編號（格式：EMP-YYYYMMDD-XXX）
3. 設置薪資方案（根據職位和部門）
4. IT 部門創建 AD 帳號
5. 配置相關權限組
6. 發送歡迎郵件（包含臨時密碼和入職指南）
7. 安排入職培訓

## 所需文件
- 身份證复印件
- 學歷證明
- 離職證明（如適用）
- 銀行帳號信息

## 注意事項
- 入職日期前 3 天完成所有系統配置
- 臨時密碼有效期為 7 天
- 新員工必須在 30 天內完成安全培訓""",
                "metadata": {"category": "hr", "topic": "onboarding", "version": "1.0"}
            },
            {
                "id": "leave_policy_v1",
                "document": """# 請假政策

## 假期類型
1. 年假：15 天/年（入职滿一年後）
2. 病假：帶薪病假 30 天/年
3. 事假：無薪，需提前 3 天申請
4. 婚假：10 天
5. 產假/陪產假：依當地法規

## 申請流程
1. 透過 HR 系統提交請假申請
2. 直屬主管審批
3. HR 確認並記錄
4. 超過 3 天需部門經理審批

## 注意事項
- 年假可跨年使用，但不得超過 2 天
- 病假需提供醫療證明
- 連續請假超過 5 天需提前 1 週申請""",
                "metadata": {"category": "hr", "topic": "leave", "version": "1.0"}
            }
        ]

        for doc in hr_docs:
            collection.upsert(
                ids=[doc["id"]],
                documents=[doc["document"]],
                metadatas=[doc["metadata"]]
            )
        print(f"✅ 已初始化 {len(hr_docs)} 個 HR 政策文檔")

    def seed_it_knowledge(self):
        """初始化 IT 知識庫（AD 帳號管理指南）"""
        collection = self.client.get_or_create_collection(
            name="it_knowledge",
            metadata={"hnsw:space": "cosine"}  # 餘弦相似度，適合文本語義搜索
        )

        it_docs = [
            {
                "id": "ad_account_guide",
                "document": """# AD 帳號管理指南

## 帳號創建流程
1. 檢查用戶名是否可用（格式：姓氏+名字首字母，如 zhangxm）
2. 創建 AD 帳號（ OU 根據部門自動分配）
3. 設置臨時密碼（必須包含大小寫字母和數字）
4. 配置密碼策略（90 天過期，歷史 12 次不重複）
5. 啟用 MFA（多因素認證）

## 權限組分配
- 通用用戶組：Domain Users, General Access
- 部門特定組：根據部門自動分配
- 角色特定組：根據職位分配（如經理組、主管組）

## 常見問題
1. 用戶名衝突：使用 中間名首字母 或 數字後綴
2. 密碼重置：透過 IT Service Desk 申請
3. 帳號鎖定：連續 5 次密碼錯誤後鎖定 30 分鐘""",
                "metadata": {"category": "it", "topic": "ad_account", "version": "1.0"}
            }
        ]

        for doc in it_docs:
            collection.upsert(
                ids=[doc["id"]],
                documents=[doc["document"]],
                metadatas=[doc["metadata"]]
            )
        print(f"✅ 已初始化 {len(it_docs)} 個 IT 知識文檔")

    def seed_all(self):
        """初始化所有知識庫"""
        print("🚀 開始初始化知識庫...")
        self.seed_hr_policies()
        self.seed_it_knowledge()
        print("✅ 知識庫初始化完成")


if __name__ == "__main__":
    builder = KnowledgeBaseBuilder()
    builder.seed_all()
