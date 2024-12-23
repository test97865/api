import requests
import json
import argparse
import os

# 从环境变量中读取 API 令牌和区域 ID，这是最佳实践，避免硬编码敏感信息
API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
ZONE_ID = os.environ.get("CLOUDFLARE_ZONE_ID")

API_TOKEN='FL8FPH_1a9G6RAgJ4fchiWIRVUvq_4DVv28toNkv'
ZONE_ID='7be6d35774d4bb5ad8fe30945d255f35'




if not API_TOKEN or not ZONE_ID:
    print("请设置 CLOUDFLARE_API_TOKEN 和 CLOUDFLARE_ZONE_ID 环境变量")
    exit(1)

API_BASE_URL = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def list_dns_records():
    """列出 DNS 记录"""
    try:
        response = requests.get(API_BASE_URL, headers=HEADERS)
        response.raise_for_status()  # 检查 HTTP 错误
        records = response.json().get("result", [])
        print(json.dumps(records, indent=2)) # 格式化输出
        return records
    except requests.exceptions.RequestException as e:
        print(f"列出 DNS 记录失败：{e}")
        return None

def create_dns_record(record_type, name, content, ttl=3600, proxied=True):
    """创建 DNS 记录"""
    data = {
        "type": record_type,
        "name": name,
        "content": content,
        "ttl": ttl,
        "proxied": proxied
    }
    try:
        response = requests.post(API_BASE_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        print("DNS 记录创建成功：", response.json())
    except requests.exceptions.RequestException as e:
        print(f"创建 DNS 记录失败：{e}")

def update_dns_record(record_id, record_type, name, content, ttl=3600, proxied=True):
  """更新 DNS 记录"""
  url = f"{API_BASE_URL}/{record_id}"
  data = {
        "type": record_type,
        "name": name,
        "content": content,
        "ttl": ttl,
        "proxied": proxied
    }
  try:
      response = requests.put(url, headers=HEADERS, json=data)
      response.raise_for_status()
      print("DNS 记录更新成功：", response.json())
  except requests.exceptions.RequestException as e:
      print(f"更新 DNS 记录失败：{e}")

def delete_dns_record(record_id):
    """删除 DNS 记录"""
    url = f"{API_BASE_URL}/{record_id}"
    try:
        response = requests.delete(url, headers=HEADERS)
        response.raise_for_status()
        print("DNS 记录删除成功")
    except requests.exceptions.RequestException as e:
        print(f"删除 DNS 记录失败：{e}")

def main():
    parser = argparse.ArgumentParser(description="Cloudflare DNS API 脚本")
    parser.add_argument("action", choices=["list", "create", "delete", "update"], help="操作类型：list, create, delete, update")
    parser.add_argument("-t", "--type", help="记录类型 (例如 A, CNAME, TXT)")
    parser.add_argument("-n", "--name", help="记录名称")
    parser.add_argument("-c", "--content", help="记录内容")
    parser.add_argument("-i", "--id", help="记录 ID (用于删除和更新)")
    parser.add_argument("--ttl", type=int, default=3600, help="TTL 值 (默认 3600)")
    parser.add_argument("--proxied", action="store_true", help="启用 Cloudflare 代理")
    parser.add_argument("--no-proxied", dest="proxied", action="store_false", help="禁用 Cloudflare 代理")
    parser.set_defaults(proxied=True) # 默认开启代理

    args = parser.parse_args()

    if args.action == "list":
        list_dns_records()
    elif args.action == "create":
        if not all([args.type, args.name, args.content]):
            print("创建记录需要指定类型、名称和内容")
            exit(1)
        create_dns_record(args.type, args.name, args.content, args.ttl, args.proxied)
    elif args.action == "update":
        if not all([args.id, args.type, args.name, args.content]):
            print("更新记录需要指定ID，类型、名称和内容")
            exit(1)
        update_dns_record(args.id,args.type, args.name, args.content, args.ttl, args.proxied)
    elif args.action == "delete":
        if not args.id:
            print("删除记录需要指定 ID")
            exit(1)
        delete_dns_record(args.id)

if __name__ == "__main__":
    main()