# 测试工具库 czo

用于快速构造测试数据与常用辅助函数（时间、随机、网络、路径、假数据）。

## 安装

```bash
pip install czo
```

## 快速上手

```python
from czo import Rand, Faker, DateTime, Net, Paths

Rand.random_str(12)              # 随机字符串
Rand.random_email()              # 随机邮箱
Rand.random_url()                # 随机 URL

DateTime.parse_iso8601("2024-01-01T00:00:00Z")  # 解析 ISO8601
DateTime.to_timezone("2024-01-01T00:00:00Z", 8) # 转换时区

Net.generate_ip_list(3)          # 生成 IPv4 列表
Net.ip_in_range("192.168.1.1", "192.168.1.0/24")

faker = Faker()
faker.profile(zh=True)           # 随机中文个人档案
```

## 开发与测试

```bash
python -m venv .venv && .\.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m pytest
```

## 目录结构

- `src/czo/utils/` 核心工具（时间、随机、网络、路径、假数据等）
- `src/czo/data/` 内置数据集（地址、学校、车牌等）
- `tests/` pytest 用例
