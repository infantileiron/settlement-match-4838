# 长川译务 · 结算凭证勾稽

对模拟委托里程碑与入账凭证，先做含拒配节点的全局一对一匹配，再对余项搜索受限合并付款，保留整数分、原始ID、匹配口径与未配项，供人工复核。

## 场景

长川译务结算组14人原来用 `changchuan_settlement_202611.csv` 逐行人工核销。三个痛点是同额不代表同单、合并付款难找、金额精度与容差混用。上游为模拟委托/凭证底册；本项目替代候选勾稽与复核留档；下游由结算负责人逐项核准。没有银行连接、真实账本写入或自动核销。

六实体贯穿表、Python Model/Schema/Service/Controller/Route、Vue API/Store/页面：StatementBatch、SettlementItem、MatchPolicy、MatchRun、MatchReview、Report。六业务页为总览、对账批次、委托与凭证、匹配口径、运行底稿、复核归档，另有管理员审计。

## 启动

```sh
cp .env.example .env
docker compose up -d --build --wait
docker compose exec -T backend python -m scripts.seed_demo
```

前端 http://localhost:18227 ，API文档 http://localhost:19227/docs ，MySQL宿主17727。Nginx把 `/api/` 去前缀转发Python，开发代理同口径；`/health`实际检查数据库与Redis。

| 层 | 实现 |
|---|---|
| 前端 | Vue3.5.13、TypeScript5.7.2、Vite6.0.5、vue-tsc2.2.0 |
| 锁定安装 | 复用已验Vue锁，仅JSON根工程名变化，npm ci |
| 后端 | Python3.12、FastAPI0.115.6、SQLAlchemy2.0.36 |
| 匹配 | SciPy1.14.1 linear_sum_assignment、NumPy2.2.1、Python整数子集和DP |
| 金额/存储 | MySQL8.4 LTS，金额/容差/合并上限BIGINT；非货币评分参数DOUBLE |
| 后台/网关 | Redis7.4独立worker、Nginx1.28、五服务健康检查 |

恰好frontend/backend/worker/db/redis；数据库、Redis和共享心跳产物具名卷。清理 `docker compose down -v --remove-orphans`，保留数据时省略 `-v`。

目录：`backend/src/{models,schemas,services,controllers,routes}`按六实体分层；`input_records.py`校验、`compatibility.py`硬约束与非货币评分、`hungarian.py`双侧拒配、`subset_sum.py`受限组合、`reconcile.py`两阶段及输入哈希。`config,utils,middlewares`提供数据库、JWT/口令摘要、队列、审计和错误。种子在 `backend/scripts/seed_demo.py`，`migrations/001_schema.sql`说明新库基线，实际以元数据建表。

前端 `src/{api,stores,types,constants,hooks,utils,router,pages}`，MatchMetrics/MatchFlow/MatchLedger/UnmatchedTable跨总览、结果、归档复用。测试、截图、日志位于批次外层 `test-artifacts/gb-2308`，不进入本源码目录。

本地开发：安装requirements，设置可用DATABASE_URL/REDIS_URL，从backend启动 `uvicorn src.main:app --reload`，另起 `python -m src.worker`；前端 `npm ci && npm run dev`，构建 `npm run build`。默认OpenBLAS/OMP线程1。环境变量COMPOSE_PROJECT_NAME、FRONTEND_PORT、BACKEND_PORT、DB_PORT、JWT_SECRET、SEED_DEMO；Compose内部提供DATABASE_URL/REDIS_URL。`.env`忽略，演示密钥与口令仅供本地模拟，部署使用独立配置。

## 账号与权限

统一密码 `MatchDemo2026!`。PBKDF2-SHA256独立salt摘要，JWT八小时有效。

| 账号 / 角色 | 动作 | 权限 |
|---|---|---|
| admin@settlement.demo / admin | 人工复核、批准归档、审计 | 全部写入与批准归档 |
| analyst@settlement.demo / analyst | 导入/补录、口径、异步运行、提审 | 不能批准或归档 |
| viewer@settlement.demo / viewer | 只读、下载已批准CSV | 所有写入403 |

未认证401；错角色403；失败运行不可提审409；未审不可归档409。同一批准复核重复归档返回原报告。审计记录账号/路径/状态，不写密码、Token或原始上传正文。

共享枚举Role/RunStatus/ItemSide在 `backend/src/constants/enums.py`，前端roles/runStatuses/itemSides与阶段标签在 `frontend/src/constants/enums.ts`，Role类型在types/domain.ts。

## 输入与精度

CSV列 `external_id,side,party,reference,amount_cents,currency,booking_date`。side为milestone/receipt，每批1至500条。金额仅接受1至100000000的**整数分**，CSV用ASCII整数正则后直接int，JSON用StrictInt；不接受元、小数、科学计数法、负数、零、NaN或布尔值，不先经float再转整数。前端可将分格式化显示为元，金额计算始终用分。

币种只接受CNY，业务日期为有效YYYY-MM-DD。同批external_id去首尾空白后按大小写精确识别、不可重复；数据库该列使用二进制排序规则与此一致。往来方/引用比较采用Unicode NFKC、大小写归一及空白合并，原始文本仍留存。

补录仅新增同批分录，不改已保存运行和报告。分录列表支持batch_id/side过滤，单批最多500条完整返回；其他实体列表最多200条。一次运行输入完整分录快照及规范JSON的SHA256保存，CSV携带同一哈希。

## 第一阶段：含双侧拒配的全局一对一

兼容边必须同币种、同归一往来方、绝对日期距离≤max_days、绝对金额差≤amount_tolerance；require_reference开启时还须引用相同且非空。默认容差0分、日期7天、引用严格相同。

兼容边分数为：

`日期距离×date_weight + 引用不同的reference_weight + abs(金额差分)/(容差分+1)`

这是非货币排序分，不是金额。每个未配委托和未配凭证分别付reject_cost分。扩展矩阵大小M+N：真实兼容边、每项专属拒配dummy、dummy互配零分；禁配边上界大于全部拒配的可行方案，故不会强选禁配。匈牙利法在此矩阵求全局最小总分，昂贵兼容边也可被拒配。一个真实配对替代两项拒配分。

手算 `[[1,9],[8,2]]` 的最优对角总分3；单个禁配或成本50而单侧拒配6时选择双侧拒配，总分12。

## 第二阶段：整数分受限子集和

仅处理第一阶段未使用的委托/凭证。凭证按业务日期、ID顺序；候选需满足同方/同币/日期/引用硬约束，按日期距离与ID排序后保留最多max_candidates（2至20，默认16）。至少2项，最多max_group_size（2至6，默认4）。凭证和组合总额均不超过max_group_amount（默认2000000分，最大10000000分）。

DP状态为(整数金额和,项数)，每个候选只遍历一次，用状态快照更新，避免同项重复选取；保留确定性索引路径。可接受和在目标±整数分容差内，且不超过组金额上限。优先金额差小、组数少、路径字典序；组成功后立即锁定委托与凭证，下一笔不能重用。状态超过50000时明确记录state_limit且不编造组合；候选截断数与未命中原因也保存。

`[100,200,400]`目标300选前两项。两笔同额300凭证争用相同100+200，只能一笔得到组合，另一笔保持未配。第一阶段已用项同样不能再参与第二阶段。

**两阶段不保证一对多联合全局最优**：第一阶段已固定，第二阶段有顺序、候选/组大小/金额/状态限制。界面展示搜索限制；未配项不等于凭证错误或不存在真实关联。本工具只生成可复核候选，不作实际资金处置。

## 一天的模拟工作日

Seed为80委托、65凭证：50个常规一对一、10组两委托合并、同额干扰以及往来方/引用/日期不兼容和无来源反例，币种CNY。

1. 09:00 导入 `changchuan_settlement_202611.csv`，检查145条分录、整数分和唯一ID。
2. 09:05 打开委托/凭证台账，核对往来方、引用和业务日期。
3. 09:10 保存0分容差、7天、严格引用及双侧拒配40分。
4. 09:14 设置16候选/4项组合/2000000分上限，送Redisworker。
5. 09:20 查看全局一对一，检查同额干扰是否被硬约束或拒配隔离。
6. 09:25 切换合并付款，按原始委托ID核对组合；未配项保留原记录与搜索限制。
7. 09:30 分析师提交人工复核，管理员批准输入哈希、候选和结论边界。
8. 09:36 viewer下载包含匹配与未配项的CSV；不写任何银行或真实账本。

种子自然键幂等，重复执行不覆盖用户修改的批次说明。

## 已知差异

MySQL采用8.4 LTS而非8.0；Redis列表无worker崩溃自动重投/取消；新库建表无存量库版本化迁移回滚。仅CNY模拟，不做跨币种换汇、银行连接、自动核销或多币种清算。第二阶段受限且有顺序，不是混合一对一/一对多的联合最优求解。Google Fonts离线回退字体。

MIT License。真实检查见批次 `test-artifacts/gb-2308/TESTING.md`。
