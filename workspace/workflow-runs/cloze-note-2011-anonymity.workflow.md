---
workflow_id: cloze-note-generation
workflow_name: Cloze Note Generation
workflow_version: 1
state_file_type: workflow-run
run_id: "cloze-2011-anonymity-20261028"
task: "2011 完形（网络匿名与可信身份）精读笔记"
created_from: ".claude/workflows/cloze-note-generation/state-template.md"
created_at: "2026-10-28"
last_updated: "2026-10-28"
current_phase: P6
current_status: in_progress
mode: guided
blocked_reason: ""
year: "2011"
cloze_slug: "anonymity"
topic: "网络匿名与可信身份"
blank_count: "20"
source_path: "英语阅读资料/2011阅读/完形填空.md"
material_path: "完形填空/素材/2011-cloze-anonymity-原文.md"
answer_key: "official"
user_answer_source: "套卷照片手写答案（红笔为订正）+ 用户逐空确认（20 空全部作答，无漏答）"
intermediate_dir: "intermediate/2011-cloze-anonymity/"
output_path: "完形填空/2011-cloze-anonymity-精读笔记.md"
error_list_path: "完形错因清单.md"
---

# Cloze Note Generation - Workflow Run

> 工作流：cloze-note-generation
> 任务：2011 完形（网络匿名与可信身份）精读笔记
> 运行标识：cloze-2011-anonymity-20261028
> 创建时间：2026-10-28
> 当前阶段：阶段 6
> 状态图例：⬜ 未开始 | 🔲 进行中 | ✅ 已完成 | ⏭️ 跳过

---

## 阶段 0：输入收集与状态初始化

- [ ] 已读取 `.learnings/` 经验库和 `.claude/rules/workflow-routing.md`
- [ ] 已确认完形原文文本或源文件路径
- [ ] 已确认空格数为 20（或已明确报告实际数量）
- [ ] 已确认 20 组选项（A-D）
- [ ] 已确认官方答案，并记录 `answer_key` 来源
- [ ] 已逐空确认用户作答，含哪些空为漏答
- [ ] 已确认 year、cloze_slug、topic
- [ ] 已确认 intermediate 目录
- [ ] 已确认最终输出路径
- [ ] 已确认 `完形错因清单.md` 路径

> [P0] ✅ 已完成 {complete}

---

## 阶段 1：原文与选项固化

- [ ] 已调用 `format-article`
- [ ] 已生成或更新 `formatted-article.md`
- [ ] 已生成或更新素材原文 `完形填空/素材/2011-cloze-anonymity-原文.md`
- [ ] 已核验空格数与选项数
- [ ] 已确认英文正文未删改
- [ ] 已确认标题格式适合 Obsidian

> [P1] ✅ 已完成 {complete}

---

## 阶段 2：逐段中英翻译

- [ ] 已调用 `translate`
- [ ] 已生成或更新 `translation.md`
- [ ] 英文行内已用 `【n 答案】` 标出正确选项
- [ ] 段落与 `formatted-article.md` 一一对应
- [ ] 已补充 `## 全篇译文要点`

> [P2] ✅ 已完成 {complete}

---

## 阶段 3：语法整理

- [ ] 已调用 `organize-grammar`
- [ ] 已生成或更新 `grammar-notes.md`
- [ ] 只保留与空格或陷阱直接相关的结构
- [ ] 每个 `###` 标题已标注对应空号
- [ ] 未做全文句法标注

> [P3] ✅ 已完成 {complete}

---

## 阶段 4：固定搭配整理

- [ ] 已调用 `organize-grammar`
- [ ] 已生成或更新 `固定搭配与词组笔记.md`
- [ ] 已包含主题词、高频固定搭配、动词搭配与干扰项、速记卡片四块
- [ ] 本篇考点已用 📌 标注
- [ ] 纯语法未混入本文件，已用 wikilink 指向 `语法总结笔记`
- [ ] 每个以固定搭配为答案的空已列出并说明干扰项

> [P4] ✅ 已完成 {complete}

---

## 阶段 5：逐空分析与错因归类

- [ ] 已生成或更新 `逐空分析.md`
- [ ] 20 行齐全：空、你的答案、正确、判断依据、干扰项为何错、错因标签
- [ ] 已按五类标签归类，每空只归一类
- [ ] 标签计数与失分空数一致
- [ ] 漏答空未被记为正确
- [ ] 已写出 5-8 个重点错题深挖
- [ ] 结构性失败的空已用 `analyze-sentence` 分析并留存

> [P5] ✅ 已完成 {complete}

---

## 阶段 6：综合笔记整合

- [ ] 已调用 `compile-note`
- [ ] 已使用 P0 确认的最终输出路径
- [ ] 十个章节齐全且顺序为 一 到 十
- [ ] 章节一为完整 20 行作答记录 + 统计
- [ ] 章节二含 `> [!quote]- 文章原文`
- [ ] 章节三含 20 行六列表 + `### 重点错题深挖`
- [ ] 章节四含信号词表、全篇逻辑链、`> [!tip] 完形读法`
- [ ] 已插入词汇占位符 `<!-- VOCABULARY_SLOT -->`
- [ ] 表格前、`---` 前均有空行
- [ ] 已做可见文本差集，无英文整段或整句丢失

> [P6] 🔲 进行中 {in_progress}

---

## 阶段 7：生词表与练习

- [ ] 已调用 `extract-vocabulary`
- [ ] 已生成或更新 `## 生词表`
- [ ] 已生成或更新 `### 生词练习`
- [ ] 已补充短语内重要独立词条
- [ ] 词汇占位符已消失

> [P7] ⬜ 未开始 {not_started}

---

## 阶段 8：错因清单更新

- [ ] 已在 `完形错因清单.md` 追加 `### 2011 完形（网络匿名与可信身份）`
- [ ] 已写失分点明细、本篇统计、本篇结论、沉淀的防错规则
- [ ] 已更新 frontmatter：`updated`、`total_sources`、`processed`
- [ ] 已更新「按标签汇总」计数表
- [ ] 未把逐空详解重复抄进清单

> [P8] ⬜ 未开始 {not_started}

---

## 阶段 9：全局汇总

- [ ] 已调用 `summarize-grammar`
- [ ] 源发现已同时覆盖 `intermediate/**/grammar-notes.md` 与 `intermediate/**/固定搭配与词组笔记.md`
- [ ] 新增前已用 `grep` 去重，未重复已覆盖的语法点
- [ ] 新 section 追加在文件末尾，未插入既有 section 中间
- [ ] 已合并进根目录 `语法总结笔记.md`
- [ ] 已合并进根目录 `固定搭配与词组笔记.md`
- [ ] 已更新两个根文件的 frontmatter（updated / total_sources / processed_sources / categories）
- [ ] 已更新两个根文件的快速索引表
- [ ] 已通过差集核验（`语法总结笔记.md` 差集必须为空）
- [ ] 已向用户报告两个根文件的更新内容

> [P9] ⬜ 未开始 {not_started}

---

## 异常记录

| 时间 | 阶段 | 问题描述 | 处理方式 |
|------|------|---------|---------|

---

## 最终产出

- **素材原文**：`完形填空/素材/2011-cloze-anonymity-原文.md`
- **中间目录**：`intermediate/2011-cloze-anonymity/`
- **最终笔记**：`完形填空/2011-cloze-anonymity-精读笔记.md`
- **错因清单**：`完形错因清单.md`
- **全局汇总**：`语法总结笔记.md`、`固定搭配与词组笔记.md`
- **完成状态**：
