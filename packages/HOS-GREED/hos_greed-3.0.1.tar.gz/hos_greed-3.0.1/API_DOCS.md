# AI安全赋能平台 API 文档

## 1. 概述

AI安全赋能平台提供了一个统一的RESTful API，用于将AI能力赋能给各类安全产品与服务。平台采用轻量化设计，适合中小型企业，支持多种安全相关的智能分析功能，包括事件分析、日志解析、漏洞评估、流量检测等。

## 2. 版本说明

当前平台支持三个API版本：

- **v1**：初始版本，提供基本的智能体功能
- **v2**：增强版本，提供标准化的API接口，支持场景化应用和产品专用智能体
- **v3**：轻量化版本，采用单一端点设计，自动意图识别，适合中小型企业

推荐使用v3版本，以获得更简单的集成体验和更好的性能。

## 3. 认证方式

目前平台采用API密钥认证，在请求头中添加`Authorization`字段：

```
Authorization: Bearer <your-api-key>
```

## 4. 基本URL

```
http://<your-server>:<port>/api/v3/ai-security
```

默认端口：50000（自动顺延）

## 5. v3版本主要端点

### 5.1 单一统一接口

| 端点 | 方法 | 描述 | 适用场景 |
|------|------|------|----------|
| `/ai-security` | POST | 统一AI安全接口，处理所有安全相关请求 | 所有安全场景和产品 |

### 5.2 支持的场景

- **安全分析**：事件分析、日志解析、流量分析、攻击检测
- **安全知识**：安全问答、情报检索、概念解释
- **报告生成**：各类安全报告生成
- **产品分析**：防火墙、WAF、堡垒机、DLP等产品数据

## 6. 请求和响应格式

### 6.1 请求格式（轻量化设计）

v3版本采用极简的请求格式，自动意图识别，无需指定具体任务类型：

```json
{
  "task_type": "security_analysis",  // 可选，自动识别
  "data": "安全事件数据或问题",  // 统一数据字段
  "product_type": "firewall"  // 可选，产品类型
}
```

### 6.2 响应格式（轻量化设计）

所有API响应使用统一的简化格式：

```json
{
  "success": true,
  "result": "分析结果或回答内容",
  "task_type": "security_analysis",
  "message": "Successfully processed request"
}
```

## 7. 集成指南

### 7.1 集成步骤（轻量化设计）

1. **获取API密钥**：从平台管理员处获取API密钥
2. **选择API版本**：推荐使用v3版本
3. **简化请求格式**：只需准备数据，无需复杂参数
4. **实现API调用**：使用单一端点，简化开发
5. **处理响应结果**：解析统一格式的响应

### 7.2 代码示例（轻量化设计）

#### Python示例

```python
import requests
import json

# 配置 - 轻量化设计
BASE_URL = "http://localhost:50000/api/v3"
API_KEY = "your-api-key"

# 请求头
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 示例1：事件分析（自动识别）
event_data = {
    "data": {
        "event_id": "event_123",
        "event_type": "SQL注入攻击",
        "source": "192.168.1.1",
        "target": "10.0.0.1",
        "severity": "high"
    }
}

response = requests.post(
    f"{BASE_URL}/ai-security",
    headers=headers,
    data=json.dumps(event_data)
)

print("响应状态码:", response.status_code)
print("响应内容:", json.dumps(response.json(), indent=2, ensure_ascii=False))

# 示例2：安全知识查询（自动识别）
question_data = {
    "data": "什么是SQL注入攻击？如何防护？"
}

response = requests.post(
    f"{BASE_URL}/ai-security",
    headers=headers,
    data=json.dumps(question_data)
)

print("响应状态码:", response.status_code)
print("响应内容:", json.dumps(response.json(), indent=2, ensure_ascii=False))

# 示例3：产品数据分析（指定产品类型）
product_data = {
    "product_type": "firewall",
    "data": {
        "event_id": "event_456",
        "event_type": "XSS攻击",
        "source": "10.0.0.2",
        "target": "10.0.0.100"
    }
}

response = requests.post(
    f"{BASE_URL}/ai-security",
    headers=headers,
    data=json.dumps(product_data)
)

print("响应状态码:", response.status_code)
print("响应内容:", json.dumps(response.json(), indent=2, ensure_ascii=False))
```

#### Java示例

```java
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class AISecurityApiExample {
    public static final MediaType JSON = MediaType.get("application/json; charset=utf-8");
    
    public static void main(String[] args) throws Exception {
        OkHttpClient client = new OkHttpClient();
        
        String url = "http://localhost:50000/api/v3/ai-security";
        String apiKey = "your-api-key";
        
        // 简单的事件分析请求
        String json = "{\n" +
                "  \"data\": {\n" +
                "    \"event_id\": \"event_123\",\n" +
                "    \"event_type\": \"SQL注入攻击\",\n" +
                "    \"source\": \"192.168.1.1\",\n" +
                "    \"target\": \"10.0.0.1\"\n" +
                "  }\n" +
                "}";
        
        RequestBody body = RequestBody.create(json, JSON);
        Request request = new Request.Builder()
                .url(url)
                .addHeader("Authorization", "Bearer " + apiKey)
                .post(body)
                .build();
        
        try (Response response = client.newCall(request).execute()) {
            System.out.println("响应状态码: " + response.code());
            System.out.println("响应内容: " + response.body().string());
        }
    }
}
```

## 6. 场景化应用（简化）

v3版本无需显式调用场景，系统会根据输入数据自动识别场景和任务类型。

## 7. 轻量化设计特点

### 7.1 技术特点

- **单一端点设计**：所有请求通过一个端点处理，简化集成
- **自动意图识别**：无需指定具体任务类型，系统自动判断
- **简化请求格式**：最少只需提供数据字段
- **统一响应格式**：便于解析和处理
- **缓存机制**：减少API调用次数，降低成本
- **低资源占用**：适合部署在轻量级服务器上

### 7.2 业务优势

- **降低集成成本**：简化开发，减少学习曲线
- **降低运维成本**：单一端点，便于监控和维护
- **适合中小型企业**：无需购买昂贵的实体设备
- **快速上线**：简化的集成流程，快速部署
- **灵活扩展**：支持多种安全场景和产品

## 8. 监控接口

平台提供了监控接口，用于获取系统和服务的运行状态：

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/monitoring/metrics` | GET | 获取所有监控指标 |
| `/api/monitoring/metrics/system` | GET | 获取系统级指标 |
| `/api/monitoring/metrics/service` | GET | 获取服务级指标 |
| `/api/monitoring/metrics/reset` | GET | 重置服务级指标 |

## 9. 常见问题

### 9.1 如何选择API版本？

推荐使用v3版本，特别是对于中小型企业。v3版本提供了更简单的集成体验和更好的性能，适合快速部署和使用。

### 9.2 如何处理API调用失败？

1. 检查API密钥是否正确
2. 检查请求格式是否符合要求
3. 检查网络连接是否正常
4. 查看服务器日志获取详细错误信息
5. 联系平台管理员获取帮助

### 9.3 如何优化API调用性能？

1. 利用系统内置的缓存机制
2. 合理设置请求数据大小，避免不必要的数据传输
3. 调整超时时间，适应不同网络环境
4. 监控API调用情况，优化调用频率

### 9.4 如何获取支持？

1. 查看API文档和示例
2. 联系平台管理员
3. 发送邮件至support@example.com

## 10. 变更日志

### v3.0.0 (2025-12-11)

- 新增轻量化设计，单一端点
- 自动意图识别，无需指定任务类型
- 简化请求和响应格式
- 内置缓存机制，降低成本
- 优化性能，适合中小型企业

### v2.0.0 (2025-12-10)

- 新增标准化API接口
- 支持场景化应用
- 新增产品专用智能体
- 支持数据标准化处理
- 新增监控与管理功能

### v1.0.0 (2025-12-01)

- 初始版本
- 支持基本的智能体功能
- 支持事件分析、日志解析、漏洞评估等基本功能

## 11. 联系我们

- 平台地址：http://localhost:50000
- 文档地址：http://localhost:50000/docs
- 管理员邮箱：admin@example.com
- 技术支持：support@example.com
