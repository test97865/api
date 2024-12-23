import os
import sys
from pathlib import Path
import time

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# 测试用的 headers
headers = {"apikey": "test"}

def test_test_connection():
    """测试数据库连接接口"""
    response = client.get("/api/v1/assets/test-connection", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "connection" in data

def test_get_assets():
    """测试获取资产列表"""
    response = client.get("/api/v1/assets/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_create_asset():
    """测试创建资产"""
    test_asset = {
        "identifier": f"test_{int(time.time())}",
        "url": "http://test.com",
        "timestamp": "2024-03-19",
        "search_engine": "test",
        "query_statements": "test query",
        "ip": "1.1.1.1"
    }
    response = client.post("/api/v1/assets/", json=test_asset, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["identifier"] == test_asset["identifier"]

if __name__ == "__main__":
    pytest.main([__file__])