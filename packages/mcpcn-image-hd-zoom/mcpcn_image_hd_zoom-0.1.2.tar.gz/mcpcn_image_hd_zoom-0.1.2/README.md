# 阿里云图像超分辨率 MCP 服务器

基于阿里云视觉智能开放平台的图像超分辨率 MCP 服务器，通过 AI 算法将图像放大 2-4 倍并显著提升清晰度。

## ✨ 核心特性

- 🚀 **支持任意 URL**：无需上传到阿里云 OSS，支持任意可访问的 HTTP/HTTPS 图片链接
- 🔍 **AI 超分辨率**：智能算法放大图像同时保持细节清晰
- 📐 **灵活放大**：支持 2 倍、3 倍、4 倍放大
- 🎨 **格式支持**：输出 JPG 或 PNG 格式
- ⚙️ **质量可控**：可调节输出质量（1-100）
- ⚡ **异步处理**：后台处理，不阻塞操作

## 📦 安装

### 方式 1：使用 uvx（推荐）

无需安装，直接运行：

```bash
uvx mcp-image-super-resolution
```

### 方式 2：通过 pip 安装

```bash
pip install mcp-image-super-resolution
```

### 方式 3：从源码安装

```bash
git clone https://github.com/fengjinchao/mcp-image-super-resolution.git
cd mcp-image-super-resolution
pip install -e .
```

## 🔑 配置阿里云凭证

### 1. 获取 AccessKey

1. 访问 [阿里云 AccessKey 管理页面](https://ram.console.aliyun.com/manage/ak)
2. 创建 AccessKey ID 和 AccessKey Secret
3. 如使用 RAM 用户，需授予 `AliyunVIAPIFullAccess` 权限

### 2. 配置环境变量

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="你的 AccessKey ID"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="你的 AccessKey Secret"
```

## 🔧 在 MCP 客户端中配置

### Claude Desktop 配置示例

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "aliyun-image-super-resolution": {
      "command": "uvx",
      "args": ["mcp-image-super-resolution"],
      "env": {
        "ALIBABA_CLOUD_ACCESS_KEY_ID": "你的 AccessKey ID",
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "你的 AccessKey Secret"
      }
    }
  }
}
```

### Cline / Kiro 配置示例

在 `.cline/mcp_settings.json` 或 `.kiro/settings/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "aliyun-image-super-resolution": {
      "command": "mcp-image-super-resolution",
      "env": {
        "ALIBABA_CLOUD_ACCESS_KEY_ID": "你的 AccessKey ID",
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "你的 AccessKey Secret"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## 📖 使用指南

### 工具 1: `submit_super_resolution_task`

提交图像超分辨率处理任务。

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `image_url` | string | ✅ | - | 图片 URL（支持任意可访问的 HTTP/HTTPS 链接） |
| `scale` | int | ❌ | 2 | 放大倍数（2、3 或 4） |
| `output_format` | string | ❌ | jpg | 输出格式（jpg 或 png） |
| `output_quality` | int | ❌ | 100 | 输出质量（1-100） |

#### 示例

**对话示例：**
```
用户：帮我把这张图片放大 3 倍
https://example.com/my-photo.jpg
```

**返回结果：**
```json
{
  "success": true,
  "job_id": "ABC123-DEF456-GHI789",
  "request_id": "ABC123-DEF456-GHI789",
  "scale": 3,
  "status": "SUBMITTED",
  "message": "任务已提交，请使用 query_task_status 查询结果"
}
```

---

### 工具 2: `query_task_status`

查询异步任务的处理状态和结果。

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `job_id` | string | ✅ | 任务 ID（由 submit_super_resolution_task 返回） |

#### 示例

**对话示例：**
```
用户：查询任务 ABC123-DEF456-GHI789 的状态
```

**返回结果（处理中）：**
```json
{
  "success": true,
  "job_id": "ABC123-DEF456-GHI789",
  "status": "PROCESSING",
  "message": "任务处理中，请稍后再查询"
}
```

**返回结果（处理成功）：**
```json
{
  "success": true,
  "job_id": "ABC123-DEF456-GHI789",
  "status": "PROCESS_SUCCESS",
  "output_url": "https://viapi-cn-shanghai.oss-cn-shanghai.aliyuncs.com/...",
  "message": "任务处理成功"
}
```

**返回结果（处理失败）：**
```json
{
  "isError": true,
  "error_code": "InvalidImage.Format",
  "error_message": "图片格式不支持，请使用 JPG 或 PNG 格式"
}
```

## 📋 任务状态说明

| 状态 | 说明 |
|------|------|
| `SUBMITTED` | 任务已提交 |
| `PROCESSING` | 任务处理中 |
| `PROCESS_SUCCESS` / `SUCCESS` | 任务处理成功 |
| `PROCESS_FAILED` / `FAILED` | 任务处理失败 |

## ⚠️ 注意事项

1. **服务开通**：需要先开通[阿里云视觉智能开放平台](https://vision.aliyun.com/)服务
2. **费用说明**：API 调用会产生费用，请查看[阿里云定价文档](https://help.aliyun.com/zh/viapi/product-overview/billing)
3. **图片要求**：
   - 支持任意可访问的 HTTP/HTTPS URL（无需上传到阿里云 OSS）
   - 建议图片大小不超过 4MB
   - 图片 URL 必须可从公网访问（不支持 localhost、内网 IP 或需要认证的 URL）
4. **处理时间**：通常为 3-10 秒，视图片大小而定
5. **异步模式**：
   - 步骤 1：使用 `submit_super_resolution_task` 提交任务，获得 `job_id`
   - 步骤 2：使用 `query_task_status` 查询任务状态和结果

## 🔧 常见问题

### 问题 1：图片下载失败

**错误信息**：
```
Error: 无法下载图片: HTTP Error 403: Forbidden
```

**原因**：提供的 URL 无法访问或需要认证

**解决方案**：
- ✅ 确保图片 URL 可以从公网访问
- ✅ 在浏览器中测试 URL 是否能打开
- ✅ 避免使用 localhost、内网 IP 或需要登录的 URL
- ✅ 检查图片服务器是否允许外部访问（CORS、防盗链等）

### 问题 2：任务一直处于 PROCESSING 状态

**原因**：图片较大或服务繁忙

**解决方案**：
- 等待更长时间（最多 30 秒）
- 如果超过 1 分钟仍未完成，可能是服务异常，请重新提交

### 问题 3：凭证错误

**错误信息**：
```
Error: InvalidCredentials
```

**解决方案**：
- 检查 AccessKey ID 和 Secret 是否正确
- 确认 RAM 用户是否有 `AliyunVIAPIFullAccess` 权限
- 检查环境变量是否正确配置

## 🛠️ 技术实现

本项目使用了阿里云 SDK 的 **Advance 方法**来支持任意 URL：

1. **下载图片**：从提供的 URL 下载图片到内存
2. **上传处理**：将图片内容作为流上传到阿里云进行处理
3. **异步查询**：通过 job_id 查询处理结果

这种方式无需用户将图片上传到阿里云 OSS，大大简化了使用流程。

## 📚 相关文档

- [阿里云图像超分辨率 API 文档](https://help.aliyun.com/zh/viapi/developer-reference/api-generated-image-super-score)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [FastMCP 框架](https://github.com/jlowin/fastmcp)
- [阿里云 VIAPI 使用案例](https://help.aliyun.com/zh/viapi/use-cases/emergent-image-points-1)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 👨‍💻 作者

fengjinchao - fengjinchao@example.com

---

**💡 提示**：如果你觉得这个项目有用，请给个 ⭐ Star！