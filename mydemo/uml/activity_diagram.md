# Mandala框架活动图

## 1. 栈回放完整流程活动图

```mermaid
flowchart TD
    START([开始栈回放演示]) --> INIT[初始化StackReplayDemo]
    INIT --> CREATE_HISTORY[创建计算历史]
    
    CREATE_HISTORY --> PREPARE_DATA[准备测试数据]
    PREPARE_DATA --> EXEC_ORIGINAL[执行原始计算]
    
    EXEC_ORIGINAL --> BATCH_CALC[批量计算函数]
    BATCH_CALC --> LOOP_START{遍历输入列表}
    
    LOOP_START -->|有更多数据| DATA_PROCESS[调用数据处理函数]
    DATA_PROCESS --> MULTIPLY[数据乘以乘数]
    MULTIPLY --> COLLECT_RESULT[收集处理结果]
    COLLECT_RESULT --> LOOP_START
    
    LOOP_START -->|处理完成| AGGREGATE[聚合所有结果]
    AGGREGATE --> CREATE_CF[创建ComputationFrame]
    CREATE_CF --> EXPAND_CF[扩展CF(recursive=True)]
    
    EXPAND_CF --> FIND_FUNC[查找目标函数]
    FIND_FUNC --> CHECK_FUNC{函数存在?}
    
    CHECK_FUNC -->|是| GET_CALLS[获取函数调用列表]
    CHECK_FUNC -->|否| ERROR[记录错误信息]
    ERROR --> END
    
    GET_CALLS --> EXTRACT_PARAMS[提取原始参数]
    EXTRACT_PARAMS --> MODIFY_PARAMS[修改参数]
    MODIFY_PARAMS --> RE_EXECUTE[重新执行函数]
    
    RE_EXECUTE --> NEW_RESULT[生成新结果]
    NEW_RESULT --> CREATE_NEW_CF[创建新的ComputationFrame]
    CREATE_NEW_CF --> EXPAND_NEW_CF[扩展新CF]
    
    EXPAND_NEW_CF --> MERGE_CF[合并ComputationFrame]
    MERGE_CF --> MERGE_SUCCESS{合并成功?}
    
    MERGE_SUCCESS -->|是| VISUALIZE[可视化结果]
    MERGE_SUCCESS -->|否| USE_NEW_CF[使用新CF]
    USE_NEW_CF --> VISUALIZE
    
    VISUALIZE --> GENERATE_SVG[生成SVG文件]
    GENERATE_SVG --> ANALYZE_RESULTS[分析结果]
    ANALYZE_RESULTS --> COMPARE[比较原始和新结果]
    COMPARE --> GENERATE_REPORT[生成分析报告]
    GENERATE_REPORT --> END([演示完成])
```

## 2. ComputationFrame扩展活动图

```mermaid
flowchart TD
    START([开始扩展CF]) --> CHECK_DIRECTION{扩展方向}
    
    CHECK_DIRECTION -->|向后扩展| EXPAND_BACK[expand_back]
    CHECK_DIRECTION -->|向前扩展| EXPAND_FORWARD[expand_forward]
    CHECK_DIRECTION -->|全部扩展| EXPAND_ALL[expand_all]
    
    EXPAND_BACK --> FIND_CREATORS[查找创建者调用]
    EXPAND_FORWARD --> FIND_CONSUMERS[查找消费者调用]
    EXPAND_ALL --> EXPAND_BACK_FIRST[先向后扩展]
    
    EXPAND_BACK_FIRST --> EXPAND_FORWARD_THEN[再向前扩展]
    EXPAND_FORWARD_THEN --> CHECK_FIXED_POINT{达到固定点?}
    CHECK_FIXED_POINT -->|否| EXPAND_BACK_FIRST
    CHECK_FIXED_POINT -->|是| COMPLETE
    
    FIND_CREATORS --> QUERY_STORAGE[查询存储]
    FIND_CONSUMERS --> QUERY_STORAGE
    
    QUERY_STORAGE --> GET_CALLS[获取相关调用]
    GET_CALLS --> CHECK_CALLS{有新调用?}
    
    CHECK_CALLS -->|否| COMPLETE[扩展完成]
    CHECK_CALLS -->|是| GROUP_CALLS[按输入/输出分组调用]
    
    GROUP_CALLS --> CREATE_NODES[创建新节点]
    CREATE_NODES --> ADD_VARS[添加变量节点]
    ADD_VARS --> ADD_FUNCS[添加函数节点]
    ADD_FUNCS --> ADD_EDGES[添加边关系]
    ADD_EDGES --> ADD_REFS[添加引用]
    ADD_REFS --> ADD_CALLS[添加调用]
    ADD_CALLS --> UPDATE_MAPPINGS[更新映射关系]
    
    UPDATE_MAPPINGS --> CHECK_RECURSIVE{递归模式?}
    CHECK_RECURSIVE -->|是| FIND_CREATORS
    CHECK_RECURSIVE -->|否| COMPLETE
    
    COMPLETE --> VALIDATE[验证图结构]
    VALIDATE --> END([扩展结束])
```

## 3. 函数执行和缓存活动图

```mermaid
flowchart TD
    START([函数调用开始]) --> CHECK_STORAGE{在Storage上下文中?}
    
    CHECK_STORAGE -->|否| DIRECT_EXEC[直接执行函数]
    CHECK_STORAGE -->|是| COMPUTE_HASH[计算参数哈希]
    
    DIRECT_EXEC --> RETURN_RESULT[返回结果]
    RETURN_RESULT --> END
    
    COMPUTE_HASH --> CHECK_CACHE{缓存中存在?}
    
    CHECK_CACHE -->|是| CACHE_HIT[缓存命中]
    CHECK_CACHE -->|否| CACHE_MISS[缓存未命中]
    
    CACHE_HIT --> GET_CACHED[获取缓存结果]
    GET_CACHED --> RETURN_CACHED[返回缓存结果]
    RETURN_CACHED --> END
    
    CACHE_MISS --> CREATE_INPUT_REFS[创建输入引用]
    CREATE_INPUT_REFS --> EXECUTE_FUNC[执行原始函数]
    EXECUTE_FUNC --> CREATE_OUTPUT_REFS[创建输出引用]
    CREATE_OUTPUT_REFS --> CREATE_CALL[创建Call对象]
    CREATE_CALL --> STORE_CALL[存储调用记录]
    STORE_CALL --> STORE_REFS[存储引用]
    STORE_REFS --> UPDATE_CACHE[更新缓存]
    UPDATE_CACHE --> RETURN_RESULT
    
    END([函数调用结束])
```

## 4. 图操作活动图

```mermaid
flowchart TD
    START([开始图操作]) --> CHECK_OP{操作类型}
    
    CHECK_OP -->|合并| UNION_OP[Union操作]
    CHECK_OP -->|交集| INTERSECT_OP[Intersection操作]
    CHECK_OP -->|差集| DIFF_OP[Difference操作]
    
    UNION_OP --> MERGE_TOPOLOGY[合并拓扑结构]
    INTERSECT_OP --> INTERSECT_TOPOLOGY[求交拓扑结构]
    DIFF_OP --> DIFF_TOPOLOGY[差集拓扑结构]
    
    MERGE_TOPOLOGY --> MERGE_ADJACENCY[合并邻接表]
    INTERSECT_TOPOLOGY --> INTERSECT_ADJACENCY[求交邻接表]
    DIFF_TOPOLOGY --> DIFF_ADJACENCY[差集邻接表]
    
    MERGE_ADJACENCY --> MERGE_NODES[合并节点集合]
    INTERSECT_ADJACENCY --> INTERSECT_NODES[求交节点集合]
    DIFF_ADJACENCY --> DIFF_NODES[差集节点集合]
    
    MERGE_NODES --> MERGE_REFS[合并引用]
    INTERSECT_NODES --> INTERSECT_REFS[求交引用]
    DIFF_NODES --> DIFF_REFS[差集引用]
    
    MERGE_REFS --> MERGE_CALLS[合并调用]
    INTERSECT_REFS --> INTERSECT_CALLS[求交调用]
    DIFF_REFS --> DIFF_CALLS[差集调用]
    
    MERGE_CALLS --> CREATE_RESULT_CF[创建结果CF]
    INTERSECT_CALLS --> CREATE_RESULT_CF
    DIFF_CALLS --> ENFORCE_INVARIANTS[强制不变量]
    
    ENFORCE_INVARIANTS --> DROP_UNREACHABLE[删除不可达元素]
    DROP_UNREACHABLE --> CLEANUP[清理空节点]
    CLEANUP --> CREATE_RESULT_CF
    
    CREATE_RESULT_CF --> VALIDATE_CF[验证CF结构]
    VALIDATE_CF --> CHECK_VALID{结构有效?}
    
    CHECK_VALID -->|是| RETURN_CF[返回结果CF]
    CHECK_VALID -->|否| ERROR[抛出错误]
    
    RETURN_CF --> END([操作完成])
    ERROR --> END
```

## 5. 可视化生成活动图

```mermaid
flowchart TD
    START([开始可视化]) --> CHECK_FORMAT{输出格式}
    
    CHECK_FORMAT -->|SVG| SVG_PATH[SVG路径]
    CHECK_FORMAT -->|内联| INLINE_PATH[内联显示]
    
    SVG_PATH --> GENERATE_DOT[生成DOT格式]
    INLINE_PATH --> GENERATE_DOT
    
    GENERATE_DOT --> CREATE_GRAPH_DESC[创建图描述]
    CREATE_GRAPH_DESC --> ADD_NODES[添加节点]
    
    ADD_NODES --> LOOP_VARS{遍历变量节点}
    LOOP_VARS -->|有更多| ADD_VAR_NODE[添加变量节点]
    ADD_VAR_NODE --> FORMAT_VAR[格式化变量显示]
    FORMAT_VAR --> LOOP_VARS
    
    LOOP_VARS -->|完成| LOOP_FUNCS{遍历函数节点}
    LOOP_FUNCS -->|有更多| ADD_FUNC_NODE[添加函数节点]
    ADD_FUNC_NODE --> FORMAT_FUNC[格式化函数显示]
    FORMAT_FUNC --> LOOP_FUNCS
    
    LOOP_FUNCS -->|完成| ADD_EDGES[添加边]
    ADD_EDGES --> LOOP_EDGES{遍历边}
    
    LOOP_EDGES -->|有更多| ADD_EDGE[添加边]
    ADD_EDGE --> FORMAT_EDGE[格式化边显示]
    FORMAT_EDGE --> LOOP_EDGES
    
    LOOP_EDGES -->|完成| SET_ORIENTATION[设置方向]
    SET_ORIENTATION --> CHECK_ORIENTATION{方向类型}
    
    CHECK_ORIENTATION -->|TB| TOP_BOTTOM[上下布局]
    CHECK_ORIENTATION -->|LR| LEFT_RIGHT[左右布局]
    
    TOP_BOTTOM --> RENDER_DOT[渲染DOT]
    LEFT_RIGHT --> RENDER_DOT
    
    RENDER_DOT --> CHECK_OUTPUT{输出类型}
    CHECK_OUTPUT -->|文件| SAVE_FILE[保存到文件]
    CHECK_OUTPUT -->|内联| DISPLAY_INLINE[内联显示]
    
    SAVE_FILE --> LOG_SUCCESS[记录成功日志]
    DISPLAY_INLINE --> LOG_SUCCESS
    
    LOG_SUCCESS --> END([可视化完成])
```