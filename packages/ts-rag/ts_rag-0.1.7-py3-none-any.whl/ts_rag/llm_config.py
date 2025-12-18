import litellm


def register_qwen_models():
    """
    注册 Qwen 系列模型的参数，消除 litellm 的 'model not mapped' 警告。
    """
    # Qwen-Flash: 1M Context
    models_to_register = {
        "openai/qwen-flash": {
            "max_input_tokens": 1_000_000,  # 1M tokens
            "max_output_tokens": 32768,  # Conservative estimate
            "input_cost_per_token": 0,
            "output_cost_per_token": 0,
            "litellm_provider": "openai",
            "mode": "chat",
        }
    }

    for model, config in models_to_register.items():
        # 覆盖或者新增
        litellm.model_cost[model] = config


# 默认批次大小（段落数）
# 基于 1M context，预留安全边际后，约 600k tokens 给文档内容
# 假设平均每段落 200 tokens，则 600k / 200 = 3000 段落/批次

# Search 阶段的批次大小（段落数）
DEFAULT_MAX_PARAGRAPHS_PER_CALL_SEARCH = 1500

# Answer 阶段的批次大小（段落数）
# 暂时与 search 相同，之后可以单独调整
DEFAULT_MAX_PARAGRAPHS_PER_CALL_ANSWER = 1500

# Visit 阶段的批次大小（段落数）
# 设置为 500，使得长论文可以分成多个批次并发处理
# 约 500 × 200 = 100k tokens/批次，远小于 1M 限制
DEFAULT_MAX_PARAGRAPHS_PER_CALL_VISIT = 300
