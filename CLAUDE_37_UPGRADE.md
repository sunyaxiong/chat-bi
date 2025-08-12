# Claude 3.7 升级指南

## 升级步骤

### 1. 创建Inference Profile

运行创建脚本：
```bash
python create_inference_profile.py
```

或者手动在AWS控制台创建：
1. 登录AWS控制台 → Amazon Bedrock
2. 左侧菜单 → "Inference" → "Inference profiles"
3. 点击 "Create inference profile"
4. 配置：
   - 名称：`chatbi-claude-3-7-profile`
   - 模型：`anthropic.claude-3-7-sonnet-20250109-v1:0`
   - 描述：ChatBI Claude 3.7 Profile

### 2. 更新配置

将获得的inference profile ID更新到`.env`文件：
```bash
MODEL_ID=your-actual-inference-profile-id
```

### 3. 更新IAM权限

确保IAM用户/角色有以下权限：
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:GetInferenceProfile",
                "bedrock:ListInferenceProfiles",
                "bedrock:CreateInferenceProfile"
            ],
            "Resource": [
                "arn:aws:bedrock:*:*:inference-profile/*",
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-7-sonnet-20250109-v1:0"
            ]
        }
    ]
}
```

### 4. 重启服务

```bash
# 如果使用Docker
docker-compose down
docker-compose up --build -d

# 如果直接运行
python main.py
```

## 主要变化

### 1. 参数格式更新
- **Claude 3.5**: 支持 `top_p`, `top_k` 参数
- **Claude 3.7**: 移除了 `top_p`, `top_k` 参数

### 2. API版本更新
- **Claude 3.5**: `anthropic_version: "bedrock-2023-05-31"`
- **Claude 3.7**: `anthropic_version: "bedrock-2024-10-31"`

### 3. Token限制提升
- **Claude 3.5**: 最大 51,200 tokens
- **Claude 3.7**: 最大 200,000 tokens

## 兼容性

代码已更新为向下兼容：
- 自动检测模型类型
- 根据模型类型使用相应的参数格式
- 支持Claude 3.5和3.7同时使用

## 测试验证

升级后测试以下功能：
1. 基本查询：`查询所有电站的基本信息`
2. 复杂查询：`统计2024年各电站类型的发电量`
3. 错误处理：输入无效查询测试错误处理

## 回滚方案

如需回滚到Claude 3.5：
```bash
# 在.env文件中改回
MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

## 故障排除

### 常见错误

1. **权限错误**
   ```
   AccessDeniedException: User is not authorized to perform: bedrock:InvokeModelWithResponseStream
   ```
   解决：更新IAM权限，添加inference profile相关权限

2. **模型不可用**
   ```
   ValidationException: The specified model is not available
   ```
   解决：确认Claude 3.7在当前区域可用，检查inference profile状态

3. **参数错误**
   ```
   ValidationException: Malformed input request
   ```
   解决：检查MODEL_ID是否为正确的inference profile ID

### 调试命令

```bash
# 检查inference profiles
aws bedrock list-inference-profiles --region us-east-1

# 测试模型调用
python -c "
from server import aws, llm
bedrock = aws.get('bedrock-runtime')
result = llm.query([{'role': 'user', 'content': 'Hello'}], bedrock)
print(result)
"
```