#!/usr/bin/env python3
"""
创建Claude 3.7 Inference Profile的脚本
运行此脚本来创建inference profile，然后将返回的ID更新到.env文件中
"""

import boto3
import os
import json
from server import conf

def create_claude_37_inference_profile():
    """创建Claude 3.7的inference profile"""
    
    # 加载环境变量
    conf.load_env('.env')
    
    # 获取配置
    region = os.getenv('DEFAULT_REGION', 'us-east-1')
    
    try:
        # 创建bedrock客户端
        bedrock = boto3.client('bedrock', region_name=region)
        
        # 创建inference profile
        response = bedrock.create_inference_profile(
            inferenceProfileName='chatbi-claude-3-7-profile',
            description='ChatBI Claude 3.7 Sonnet Profile for Text2SQL',
            modelSource='arn:aws:bedrock:{}::foundation-model/anthropic.claude-3-7-sonnet-20250109-v1:0'.format(region),
            tags=[
                {
                    'key': 'Project',
                    'value': 'ChatBI'
                },
                {
                    'key': 'Model',
                    'value': 'Claude-3.7-Sonnet'
                }
            ]
        )
        
        profile_arn = response['inferenceProfileArn']
        profile_id = profile_arn.split('/')[-1]  # 提取profile ID
        
        print("✅ Inference Profile创建成功!")
        print(f"Profile ARN: {profile_arn}")
        print(f"Profile ID: {profile_id}")
        print("\n📝 请将以下ID更新到.env文件中的MODEL_ID:")
        print(f"MODEL_ID={profile_id}")
        
        return profile_id
        
    except Exception as e:
        print(f"❌ 创建Inference Profile失败: {e}")
        print("\n可能的原因:")
        print("1. 权限不足 - 需要bedrock:CreateInferenceProfile权限")
        print("2. 区域不支持 - Claude 3.7可能在当前区域不可用")
        print("3. 配额限制 - 可能已达到inference profile数量限制")
        return None

def list_existing_profiles():
    """列出现有的inference profiles"""
    
    region = os.getenv('DEFAULT_REGION', 'us-east-1')
    
    try:
        bedrock = boto3.client('bedrock', region_name=region)
        response = bedrock.list_inference_profiles()
        
        profiles = response.get('inferenceProfileSummaries', [])
        
        if profiles:
            print("\n📋 现有的Inference Profiles:")
            for profile in profiles:
                print(f"  - Name: {profile['inferenceProfileName']}")
                print(f"    ID: {profile['inferenceProfileId']}")
                print(f"    Status: {profile['status']}")
                print(f"    Model: {profile.get('modelSource', 'N/A')}")
                print()
        else:
            print("\n📋 没有找到现有的Inference Profiles")
            
    except Exception as e:
        print(f"❌ 列出Inference Profiles失败: {e}")

if __name__ == "__main__":
    print("🚀 Claude 3.7 Inference Profile 创建工具")
    print("=" * 50)
    
    # 首先列出现有的profiles
    list_existing_profiles()
    
    # 询问是否创建新的profile
    create_new = input("\n是否创建新的Claude 3.7 Inference Profile? (y/n): ").lower().strip()
    
    if create_new == 'y':
        profile_id = create_claude_37_inference_profile()
        
        if profile_id:
            print("\n🎉 设置完成!")
            print("下一步:")
            print("1. 将上面的MODEL_ID更新到.env文件")
            print("2. 重启ChatBI服务")
            print("3. 测试Claude 3.7功能")
    else:
        print("取消创建。")