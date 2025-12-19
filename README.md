# 天津中考英语作文评分服务

该项目提供了一个可落地的天津中考英语作文自动评分方案：
- **后端**：FastAPI 服务，结合天津新课标并参考北京中考评分体系，支持 LLM 接口输出详细扣分点、词汇/语法问题与教师视角建议。
- **前端**：微信小程序示例，供学生/教师输入英文作文并查看评分结果。

## 后端

### 启动
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

环境变量：
- `LLM_API_KEY`：大模型 API Key（OpenAI 协议兼容）。
- `LLM_BASE_URL`：可选，自定义推理网关地址。
- `LLM_MODEL`：可选，模型名称，默认为 `gpt-4o-mini`。

### API
- `POST /score`：入参 `{"essay": "..."}`，返回总分、细则分、语法/词汇问题和提升建议。
- `GET /health`：健康检查。

评分逻辑：
- 规则引擎提供内容、结构、语言、词汇、书写 5 个维度的基线分。
- 若配置了 LLM，将逐条指出语法和词汇问题，并提供资深教师视角的改进建议。

## 微信小程序

1. 使用微信开发者工具导入 `wechat-miniprogram` 目录。
2. 将 `pages/index/index.js` 中的 `API_BASE` 改为已部署的后端地址（如 `https://api.yourdomain.com`）。
3. 预览或上传后即可与后端交互获取实时评分。

## 部署提示
- 可将 FastAPI 部署在国内云厂商（如阿里云、腾讯云）并开启 HTTPS，满足小程序域名校验。
- 若使用自建/代理大模型服务，请保证 OpenAI 协议兼容并在环境变量中配置。
