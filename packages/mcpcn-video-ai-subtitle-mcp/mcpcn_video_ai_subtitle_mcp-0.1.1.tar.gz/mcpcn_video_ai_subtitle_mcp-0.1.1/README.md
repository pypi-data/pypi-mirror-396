# 视频-AI加字幕 MCP Server

MCP server for AI-powered video subtitle generation and merging using Volcano Engine speech recognition.

## Features

- **generate_subtitle**: Generate SRT subtitle file from video URL using AI speech recognition
- **merge_subtitle**: Burn subtitles into video with customizable styling (color, size, position)

## Installation

```bash
pip install mcpcn-video-ai-subtitle-mcp
```

## Environment Variables

- `VOLCANO_APPID`: Volcano Engine App ID
- `VOLCANO_ACCESS_TOKEN`: Volcano Engine Access Token
- `FFMPEG_BINARY`: (Optional) Path to ffmpeg binary
- `FFPROBE_BINARY`: (Optional) Path to ffprobe binary

## Usage

### MCP Configuration

```json
{
  "mcpServers": {
    "video-ai-subtitle": {
      "command": "uvx",
      "args": ["mcpcn-video-ai-subtitle-mcp"],
      "env": {
        "VOLCANO_APPID": "your-app-id",
        "VOLCANO_ACCESS_TOKEN": "your-access-token"
      }
    }
  }
}
```

## License

MIT


# 音视频字幕 API（简化版）

## 概述
- 功能：提交音/视频生成字幕任务，并查询字幕结果
- 扣费：在“查询成功返回”时按时长扣积分（VIP也扣）
- 去重：同一 `volcano_task_id` 仅扣一次

## 鉴权
- Header：`x-token: <用户登录令牌>`
- 所有接口需登录态

## 计费与积分
- 换算：`1分钱 = 2积分` → `1元 = 200积分`
- 阶梯单价（按当月累计小时数选择单价）：
  - 0～300 小时：6.5 元/小时 → 1300 积分/小时
  - 301～1000 小时：6 元/小时 → 1200 积分/小时
  - 1001～3000 小时：5.6 元/小时 → 1120 积分/小时
  - 3001～5000 小时：5 元/小时 → 1000 积分/小时
  - 5001+ 小时：4 元/小时 → 800 积分/小时
- 扣费时机：查询成功（`code=0`/`message=Success`）且解析到时长后扣费
- 时长解析顺序：
  - `data.duration`（单位秒，优先）
  - `data.utterances` 的 `start_time`/`end_time`（单位毫秒，取整段范围，换算为秒）
  - 兼容旧格式：`result.duration`、`result.segments`、`result.subtitles`
- 扣减优先级：`FreePoints` → `VipPoints` → `Points`
- 去重规则：积分流水 `reason` 前缀为 `视频字幕生成 volcano_task_id=<id>` 的记录存在即视为已扣

## 接口列表

### 1) 提交任务
- Method：`POST`
- URL：`/api/translate/videoCaption/submit`
- Header：`x-token: <用户登录令牌>`
- Body（JSON）：
  - `url` 必填，媒体地址
  - `words_per_line` 可选，默认 `46`
  - `max_lines` 可选，默认 `1`
  - `language` 可选，默认 `zh-CN`
  - `caption_type` 可选，默认 `auto`
  - `use_itn`、`use_punc`、`use_ddc`、`with_speaker_info` 可选，默认 `false`
- Response（JSON）：
  - 成功：`{"code":0,"data":{"id":"<taskId>"}}`
  - 失败：`{"code":非0,"msg":"提交失败: <原因>"}`

示例：
```json
POST /api/translate/videoCaption/submit
{
  "url": "https://example.com/media.mp4",
  "language": "zh-CN",
  "caption_type": "auto"
}
```

### 2) 查询结果并扣费
- Method：`GET`
- URL：`/api/translate/videoCaption/query?id=<taskId>&blocking=1`
- Header：`x-token: <用户登录令牌>`
- Query：
  - `id` 必填，任务 ID
  - `blocking` 可选，`1` 表示阻塞等待（建议）
- Response（JSON）：
  - 成功：返回第三方原始数据（含 `data.duration` 或 `data.utterances`）
  - 失败：`{"code":非0,"msg":"查询失败: <原因>"}`

示例返回（节选）：
```json
{
  "code": 0,
  "data": {
    "code": 0,
    "message": "Success",
    "duration": 18.13575,
    "id": "88620edc-9be1-432b-8476-8a84986c578e",
    "utterances": [
      { "start_time": 1200, "end_time": 2020, "text": "飞书，" },
      { "start_time": 12120, "end_time": 13420, "text": "打开飞书，" }
    ]
  },
  "msg": "成功"
}
```

## 扣费示例（积分流水）
- 记录格式：
  - `Type`: `translate`
  - `Reason`: `视频字幕生成 volcano_task_id=<id> duration_seconds=<秒> price_per_hour=<单价>`
  - `Remark`: `扣减明细：<免费+VIP+普通>`
- 示例（实际库中记录）：
```sql
INSERT INTO `sys_user_points`
(`id`,`created_at`,`updated_at`,`deleted_at`,`user_id`,`change`,`reason`,`project_id`,`project_tool_id`,`type`,`model_id`,`usage_log_id`,`order_id`,`remark`,`task_id`,`user_task_id`,`redeem_code_id`,`membership_id`)
VALUES
(15504,'2025-12-11 17:31:37.242','2025-12-11 17:31:37.242',NULL,49,-7,'视频字幕生成 volcano_task_id=88620edc-9be1-432b-8476-8a84986c578e duration_seconds=18 price_per_hour=6.5',0,0,'translate',0,0,0,'扣减明细：7（VIP）',0,0,0,0);
```

## 注意事项
- 返回成功且可解析到时长才扣费；否则不扣
- 同一任务仅扣一次；重复查询不重复扣费
- `blocking=1` 推荐使用，以便拿到完整结果和及时扣费