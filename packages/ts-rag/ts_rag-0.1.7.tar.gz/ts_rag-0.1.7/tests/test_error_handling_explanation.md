# 错误处理和重试机制说明

## 重试机制的层次

### 1. LLM 层面的自动重试（在 tashan_core 内部）

**位置**: `tashan_core/internal/base/llms.py`

**机制**:
- 当调用 `litellm.acompletion()` 时，传递了 `num_retries=num_retries_failed_request`（默认 3）
- `litellm` **自动处理重试**，使用**指数回退**策略
- 重试间隔：1s → 2s → 4s → 8s（指数增长）

**触发条件**:
- API 请求失败（网络错误、超时、rate limit 等）
- 自动重试，无需 answer.py 或 visit.py 干预

**代码位置**:
```python
# tashan_core/internal/base/llms.py:4325
return await litellm.acompletion(
    ...
    num_retries=num_retries_failed_request,  # 默认 3
    ...
)
```

### 2. Visit 层面的错误处理（在 answer.py）

**位置**: `answer.py` 的 `process_single_paper()` 函数

**机制**:
- 如果 `extract_info()` 抛出异常，会被 `try-except` 捕获
- 返回 `None`，表示该论文处理失败
- **不会阻塞其他论文的处理**

**代码**:
```python
# answer.py:98-108
try:
    result = await loop.run_in_executor(None, extract_info, question, file_path)
    return {"paper_id": paper_id, "file_path": file_path, "result": result}
except Exception as e:
    print(f"  [Error] Failed to visit {paper_id}: {e}")
    return None  # 返回 None，不影响其他论文
```

### 3. 聚合阶段的容错（在 answer.py）

**位置**: `answer.py` 的 `run_pipeline()` 函数

**机制**:
- 使用 `asyncio.gather(*tasks)` 等待所有任务完成
- 过滤掉 `None` 和包含 `error` 的结果
- **只要有部分论文成功，就能继续生成答案**

**代码**:
```python
# answer.py:152-154
visit_results = await asyncio.gather(*tasks)
valid_results = [r for r in visit_results if r is not None and "error" not in r.get("result", {})]
# 只要有 valid_results，就能继续生成答案
```

## 错误场景分析

### 场景 1: 单个 API 请求失败

**流程**:
1. `visit.py` 调用 `llm.extract_all(doc)`
2. 内部调用 `litellm.acompletion()`
3. API 请求失败 → `litellm` **自动重试 3 次**（指数回退）
4. 如果 3 次重试都失败 → 抛出异常
5. `extract_info()` 捕获异常 → 返回包含 `error` 的字典
6. `process_single_paper()` 捕获异常 → 返回 `None`
7. `run_pipeline()` 过滤掉 `None` → 继续处理其他论文

**影响**:
- ✅ **不影响其他论文的处理**
- ✅ **只要有部分论文成功，就能生成答案**
- ✅ **重试是自动的，无需手动干预**

### 场景 2: 多个 API 请求同时失败

**流程**:
1. 5 个并发 visit，每个都调用 API
2. 如果多个同时失败，每个都会独立重试
3. 由于指数回退，重试时间会分散（不会同时爆发）
4. 部分成功 → 继续生成答案
5. 全部失败 → 返回错误信息

**影响**:
- ✅ **不会造成长尾效应**（指数回退分散重试时间）
- ✅ **不会造成请求堆积**（semaphore 限制并发）
- ✅ **部分失败不影响整体流程**

### 场景 3: Visit 阶段全部失败

**流程**:
1. 所有论文的 visit 都返回 `None` 或包含 `error`
2. `valid_results` 为空列表
3. 继续执行 Answer 阶段，但 `snippets_text_block` 为空
4. LLM 会根据提示词返回"无法回答"或"无相关信息"

**影响**:
- ✅ **不会崩溃**，会正常返回结果
- ✅ **答案会说明"未找到相关信息"**

## 测试用例的验证点

### 测试用例 1-2: 正常情况
- **验证**: 并发限制是否生效
- **验证**: 是否能正常处理多篇论文

### 测试用例 3: 并发限制验证
- **验证**: 不同并发限制值是否生效
- **验证**: 是否真的限制了并发数

### 测试用例 4: 边界情况
- **验证**: 没有论文时是否正常处理
- **验证**: 不会崩溃

### 测试用例 5: 部分成功场景
- **验证**: 部分论文失败时是否继续处理
- **验证**: 是否能基于成功的论文生成答案

### 测试用例 6: 性能测试
- **验证**: 并发限制对性能的影响
- **验证**: 是否在性能和稳定性之间取得平衡

## 总结

### 重试机制的位置

✅ **重试在 LLM 层面（tashan_core）**:
- `litellm` 自动重试（指数回退）
- `tashan_core` 传递重试参数
- **answer.py 和 visit.py 不需要处理重试逻辑**

✅ **错误处理在 answer.py**:
- 捕获单个论文的处理失败
- 过滤失败的结果
- 允许部分成功

### 能否应对各种情况？

✅ **能应对**:
1. **单个 API 失败**: 自动重试 3 次（指数回退）
2. **多个 API 失败**: 每个独立重试，时间分散
3. **部分成功**: 继续处理，基于成功的论文生成答案
4. **全部失败**: 正常返回，不会崩溃
5. **并发控制**: semaphore 限制并发，避免 rate limit

### 关键点

- **重试是自动的**: 在 `litellm` 层面，无需 answer.py 干预
- **错误是容错的**: 单个失败不影响整体流程
- **并发是受限的**: semaphore 防止请求堆积
- **重试是分散的**: 指数回退避免同时爆发
