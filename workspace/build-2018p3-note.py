#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io, os, re

BASE = "/Users/zhqznc/Documents/考研英语阅读"
DIR = os.path.join(BASE, "intermediate/2018-passage3-digital-giants")
OUT = os.path.join(BASE, "2018阅读/2018-passage3-digital-giants-精读笔记.md")

def body(path):
    s = io.open(path, encoding="utf-8").read()
    s = re.sub(r"(?s)^---\n.*?\n---\n", "", s, count=1)
    return s.strip("\n")

FRONT = """---
title: "数字经济巨头 精读笔记"
type: study-note
topic: "2018-passage3-digital-giants"
tags:
  - english-reading
  - intensive-reading
  - study-note
  - exam-prep
difficulty: intermediate
created: 2026-10-08
updated: 2026-10-08
sources:
  - "2018 考研英语（一）Text 3（数字经济巨头 / digital giants）"
  - "intermediate/2018-passage3-digital-giants/formatted-article.md"
  - "intermediate/2018-passage3-digital-giants/translation.md"
  - "intermediate/2018-passage3-digital-giants/grammar-notes.md"
  - "intermediate/2018-passage3-digital-giants/固定搭配与词组笔记.md"
---

# 数字经济巨头 精读笔记

---

## 背景

本文是 **2018 年考研英语（一）Text 3**（第 31—35 题），主题是**数字经济巨头对数据的垄断，与竞争法应对乏力之间的张力**。文章从"**数字经济巨头的实力与野心令人震惊**"这一**开篇定调句**切入——亚马逊以 135 亿美元收购高端连锁超市 Whole Foods，而 Facebook 更早以更高代价买下没有任何实体产品的通讯服务 WhatsApp，随即亮出全文的题眼：**WhatsApp 真正的价值不在产品，而在用户之间那张"友谊与社交生活的网"**。

结构上，全文是**"巨头攫取数据 → 承诺与背弃 → 竞争法的两重困境 → 数据即商品、用户被'圈养'"**的四层递进链，而**第 31 题的问点恰在第一段的落点**：`Facebook acquired WhatsApp for its ____` → **[B] user information**（`a web of its users' friendships and social lives`、`doesn't have any physical product at all`）。**第二段以"承诺—背弃"坐实数据的政治价值**：Facebook 曾向**欧盟委员会**（`the European commission`）承诺不把电话号码与账号**关联**（`link phone numbers to Facebook identities`），却在交易完成后**立刻背弃**（`broke the promise almost as soon as the deal went through`）；作者随即以**修辞性反问**扣住要害——`What political journalist, what party whip, would not want to know the makeup of the WhatsApp groups in which Theresa May's enemies are currently plotting?`，**第 32 题的答案正在此**（把手机号与账号关联会对用户构成风险 → **[C] pose a risk to Facebook users**），而段末 `the records of which customers have purchased what` 又把 Whole Foods 的价值引回**数据**。

**第三段转入竞争法的两重困境，是本篇的论证核心**：作者先承认 `Competition law appears to be the only way to address these imbalances of power`（竞争法似乎是唯一办法），随即用 `But` 接连反转——一是**太慢**（`it is very slow compared to the pace of change within the digital economy`；`By the time a problem has been addressed and remedied it may have vanished … to be replaced by new abuses of power`），二是**更深的概念性缺陷**（`there is a deeper conceptual problem, too`）：竞争法处理的是"**消费者的经济不利**（`financial disadvantage to consumers`）"，可这些服务的用户**并不付费**，因而并非法律意义上的**"顾客"**（`The users of their services are not their customers`）。**第 33 题**问作者对竞争法的态度 → **[D] cannot keep pace with the changing market**（`very slow compared to the pace of change`）；**第 34 题**问竞争法为何难以保护用户 → **[A] they are not defined as customers**（`The users of their services are not their customers`，与下句 `That would be the people who buy advertising from them` 互为定义）。

**末段以"蚂蚁—蚜虫—蜜露"的类比收束全文，既是点睛也是第 35 题的考点**：`Just as some ants farm the bugs called aphids for the honeydew they produce when they feed, so Google farms us for the data that our digital lives yield`——蚂蚁"饲养"蚜虫、为的是蜜露，Google"圈养"用户、为的是数据；`Ants keep predatory insects away …; Gmail keeps the spammers out of our inboxes` 又把"保护"这一互利面补齐，最终以 `It doesn't feel like a human or democratic relationship, even if both sides benefit` 揭示这层关系**不对等的本质**——**第 35 题**即问此类比意在说明什么 → **[D] the relationship between digital giants and their users**。**一句话概括**：这篇文章要表达的是**"数字经济巨头以'服务'为名攫取用户数据（WhatsApp 的价值是用户关系网，而非产品），它们曾承诺保护却随即背弃；作为唯一制衡手段的竞争法又太慢、且因'用户并非付费顾客'而难以适用；最终，用户与巨头的关系被比作'被饲养的蚜虫与饲养它们的蚂蚁'——即便互利，也谈不上人道与民主"**。

---

## 文章原文

"""

MID_QUESTIONS = """
---

## 题目

### 31. According to Paragraph 1, Facebook acquired WhatsApp for its ____.

- [A] digital products
- [B] user information
- [C] physical assets
- [D] quality service

### 32. Linking phone numbers to Facebook identities may ____.

- [A] worsen political disputes
- [B] mess up customer records
- [C] pose a risk to Facebook users
- [D] mislead the European commission

### 33. According to the author, competition law ____.

- [A] should serve the new market powers
- [B] may worsen the economic imbalance
- [C] should not provide just one legal solution
- [D] cannot keep pace with the changing market

### 34. Competition law as presently interpreted can hardly protect Facebook users because ____.

- [A] they are not defined as customers
- [B] they are not financially reliable
- [C] the services are generally digital
- [D] the services are paid for by advertisers

### 35. The ants analogy is used to illustrate ____.

- [A] a win-win business model between digital giants
- [B] a typical competition pattern among digital giants
- [C] the benefits provided for digital giants' customers
- [D] the relationship between digital giants and their users

---

## 翻译对照

"""

MID_TRANS_Q = """
## 题目翻译

### 31. 根据第 1 段，Facebook 收购 WhatsApp 是为了它的 ____。

- [A] 数字产品
- [B] 用户信息
- [C] 实体资产
- [D] 优质服务

### 32. 把电话号码与 Facebook 账号关联起来可能会 ____。

- [A] 加剧政治纷争
- [B] 弄乱顾客记录
- [C] 给 Facebook 用户带来风险
- [D] 误导欧盟委员会

### 33. 作者认为，竞争法 ____。

- [A] 应当服务于新的市场势力
- [B] 可能加剧经济失衡
- [C] 不应只提供一种法律解决方案
- [D] 无法跟上市场变化的步伐

### 34. 按目前解释的竞争法很难保护 Facebook 用户，因为 ____。

- [A] 他们不被界定为顾客
- [B] 他们在经济上不可靠
- [C] 这些服务通常是数字化的
- [D] 这些服务由广告商付费

### 35. 蚂蚁的类比用来说明 ____。

- [A] 数字巨头之间双赢的商业模式
- [B] 数字巨头之间典型的竞争格局
- [C] 为数字巨头的顾客提供的好处
- [D] 数字巨头与其用户之间的关系

---

## 语法要点

"""

TAIL = """
---

<!-- VOCABULARY_SLOT -->

---

## 心得

> [!tip] 主旨把握
> 全文回答的是**"数字经济巨头为何能攫取数据、竞争法为何制衡乏力、用户与巨头究竟是怎样的关系"**，行文是一条**"巨头攫取数据 → 承诺与背弃 → 竞争法两重困境 → 数据即商品、用户被圈养"**的递进链。
> 第一层**以惊人的收购案切入并点破数据的价值**：亚马逊以 135 亿美元买下高端连锁超市 Whole Foods，Facebook 更早以更高代价买下**毫无实体产品**的 WhatsApp（`which doesn't have any physical product at all`），而 WhatsApp 真正给 Facebook 的，是 `an intricate and finely detailed web of its users' friendships and social lives`（**一张由用户友谊与社交生活织成的网**，P1）。
> 第二层**以"承诺—背弃"坐实数据的政治价值**：Facebook 曾向**欧盟委员会**承诺不把电话号码与账号**关联**（`would not link phone numbers to Facebook identities`），却在交易完成后**几乎立刻背弃**（`broke the promise almost as soon as the deal went through`）；作者以**修辞性反问**强调这类数据的可怕价值——`What political journalist, what party whip, would not want to know the makeup of the WhatsApp groups in which Theresa May's enemies are currently plotting?`（P2）。
> 第三层**转入竞争法的两重困境，是全文论证核心**：先承认 `Competition law appears to be the only way to address these imbalances of power`，随即用两个 `But` 层层反转——一是**太慢**（`it is very slow compared to the pace of change within the digital economy`），二是**概念上的错位**（`a deeper conceptual problem`）：竞争法只管"**消费者的经济不利**（`financial disadvantage to consumers`）"，可用户**并不付费**，因而不是**"顾客"**（`The users of their services are not their customers`）；真正的顾客是那些**向它们购买广告投放的人**（`the people who buy advertising from them`），而 Facebook、Google **主导数字广告**、令其他媒体不利（`dominate digital advertising to the disadvantage of all other media and entertainment companies`，P3）。
> 第四层**以"蚂蚁—蚜虫—蜜露"类比收束**：`Just as some ants farm the bugs called aphids for the honeydew they produce when they feed, so Google farms us for the data that our digital lives yield`——蚂蚁"饲养"蚜虫为的是蜜露，Google"圈养"我们为的是数据；`Ants keep predatory insects away …; Gmail keeps the spammers out of our inboxes` 补上"保护"这一互利面，末句则以 `It doesn't feel like a human or democratic relationship, even if both sides benefit` 揭示这层关系**不对等的本质**（P4）。
> **一句话概括**：这篇文章真正的意思是**"数字经济巨头以'服务'之名攫取数据——WhatsApp 的价值是用户关系网而非产品；它们承诺保护却随即背弃；唯一可用的竞争法又太慢、且因'用户并非付费顾客'而难以适用；于是用户与巨头的关系，被比作被饲养的蚜虫与饲养它们的蚂蚁——即便互利，也谈不上人道与民主"**。最能定性的是三处：`What WhatsApp offered Facebook was an intricate and finely detailed web of its users' friendships and social lives`（**数据的价值在用户关系**）、`The users of their services are not their customers`（**用户不是顾客**）、`It doesn't feel like a human or democratic relationship, even if both sides benefit`（**互利但不对等**）。

> [!tip] 命题线索
> - **细节题（第 31 题）**：题干 `Paragraph 1` + `Facebook acquired WhatsApp for its ____`。P1 明确 WhatsApp `doesn't have any physical product at all`，其价值是 `a web of its users' friendships and social lives`——**用户关系网即"用户信息"** → **[B] user information**。[A] `digital products`、[C] `physical assets` 与"没有实体产品"**相反**或**无据**；[D] `quality service` 是**字面陷阱**。**对策：抓住否定信号 `doesn't have any physical product at all`，反推"价值不在产品，而在信息"。**
> - **细节题（第 32 题）**：题干 `Linking phone numbers to Facebook identities may ____`。P2 说明这类关联能让"谁知道谁给谁发了消息"变得 `enormously revealing`，对用户隐私构成威胁 → **[C] pose a risk to Facebook users**。[A] `worsen political disputes` **主体错位**（数据被政客利用 ≠ 加剧政治纷争）；[B] `mess up customer records` 无据；[D] `mislead the European commission` **是 Facebook 误导欧委会**，而非"关联动作误导"，属**偷换**。**对策：问"某动作会带来什么后果"，回原文找该动作的直接后果，勿被表面相关的名词干扰。**
> - **态度题（第 33 题）**：题干 `According to the author, competition law ____`。P3 作者称其 `very slow compared to the pace of change within the digital economy`，且问题常在处理完毕前已 `vanished` → **[D] cannot keep pace with the changing market**（`very slow compared to the pace of change` ↔ `cannot keep pace with`，**同义复现**）。[A]、[B] 与作者立场**相反**；[C] `should not provide just one legal solution` **无中生有**（作者并未主张"多种法律方案"）。**对策：态度题盯住评价词（`clumsy`、`very slow`）与让步后的转折（两个 `But`）。**
> - **细节题（第 34 题）**：题干 `Competition law as presently interpreted can hardly protect Facebook users because ____`。P3 原句 `The users of their services are not their customers`，紧接下句 `That would be the people who buy advertising from them` 给出"顾客"定义 → **[A] they are not defined as customers**。[B] `financially reliable` **曲解**（原文是 `financial disadvantage`，非"可靠"）；[C]、[D] 均为**因果错位**（"服务是数字化的""广告商付费"都不是"难以保护"的直接原因）。**对策：because 题须锁定"直接因果句"，本句的因果就是"用户不是顾客，所以法律保护落空"。**
> - **例证题（第 35 题）**：题干 `The ants analogy is used to illustrate ____`。P4 类比落点在末句 `It doesn't feel like a human or democratic relationship`，主句主语是 Google 与 us → 说明的是**巨头与用户之间的关系** → **[D] the relationship between digital giants and their users**。[A] `win-win business model` 是**作者明确的让步而非论点**（`even if both sides benefit`）；[B] `competition pattern among digital giants` **主体错位**；[C] `benefits provided for digital giants' customers` **对象错位**（用户不是顾客）。**对策：例证题问"例子说明什么"，答案在例子前后的**论点句**，尤其注意 `even if …` 让步从句——**让步是"不是论点"的信号**。**

> [!warning] 易错点
> - **一个句子里 `while`/`but` 与"数据"的反复出现**：本篇第 2 段 `but` 转折频繁，须分清**哪一层是作者主张**——政治记者"想知道"是**事实**，Facebook"背弃承诺"是**评判**。
> - **`link A to B` 的搭配**：`link phone numbers to Facebook identities`——介词固定用 `to`（非 with/of），考研常考。
> - **`as soon as` 与 `as long as` 之别**：本篇是 `as soon as the deal went through`（**一……就**），不同于 `as long as`（只要/只要……之久）。
> - **`By the time` 从句的时态**：`By the time a problem has been addressed and remedied` 用**现在完成时**替代将来完成时，主句用 `may have vanished`（情态 + 完成）。
> - **不定式作结果状语 vs 目的状语**：`it may have vanished …, to be replaced by new abuses of power` 是**结果**（`to be replaced` 说明"消失"的后果），切勿读成"为了被取代"。
> - **`when` 表"条件"而非"时间"**：`this is not obvious when the users of these services don't pay for them` 中 `when` ≈ if / considering that。
> - **`not so much A but B` 是变体**：标准形式为 `not so much A as B`，本篇用 `but`（= but rather），译"与其说是 A，不如说是 B"，**重在肯定 B**。
> - **`it may be that …` 的 `that` 不可省**：此处 `it` 是**形式主语**，`that` 从句是真主语，与可省 `that` 的宾语从句不同。
> - **`farm` 的一词双关**：蚂蚁"**饲养**"蚜虫、Google"**圈养**"用户——同一动词带出"用户被当作资源"的贬义，是第 35 题的**态度线索**。
> - **修辞性反问 = 强肯定**：`What political journalist, what party whip, would not want to know …?` 实义是"**任何**政治记者、**任何**党鞭都会想知道"，切勿按字面读成"没人想知道"。
> - **`to the disadvantage of` 是固定搭配**："对……不利"，`disadvantage` 此处是名词（非动词）。
> - **`That would be the people who …` 的指代**：`That` 指代上句的"顾客"概念，`would be` 表**推断性判断**（"那才（应该）是……"）。

### 论证结构

```mermaid
graph TD
    A[P1 巨头攫取数据: 亚马逊 135 亿美元收购 Whole Foods；Facebook 更高价买下无实体产品的 WhatsApp，真正价值是用户友谊与社交生活之网 —— Amazon has just announced the purchase of the upmarket grocery chain Whole Foods for 13.5bn；WhatsApp doesnt have any physical product at all；an intricate and finely detailed web of its users friendships and social lives] --> B[P2 承诺与背弃: 向欧盟委员会承诺不关联手机号与账号，交易完成即背弃；反问强调数据的政治价值 —— Facebook promised the European commission that it would not link phone numbers to Facebook identities；it broke the promise almost as soon as the deal went through；What political journalist, what party whip, would not want to know the makeup of the WhatsApp groups in which Theresa Mays enemies are currently plotting]
    B --> C[P3 竞争法两重困境: 太慢（跟不上数字化变化）+ 概念错位（只管付费消费者的经济不利，而用户并非顾客） —— Competition law appears to be the only way to address these imbalances of power；it is very slow compared to the pace of change within the digital economy；By the time a problem has been addressed and remedied it may have vanished；The users of their services are not their customers；Facebook and Google dominate digital advertising to the disadvantage of all other media and entertainment companies]
    C --> D[P4 数据即商品、用户被圈养: 蚂蚁饲养蚜虫取蜜露，Google 圈养用户取数据；即便互利也不人道不民主 —— Just as some ants farm the bugs called aphids for the honeydew they produce when they feed, so Google farms us for the data that our digital lives yield；Ants keep predatory insects away；Gmail keeps the spammers out of our inboxes；It doesnt feel like a human or democratic relationship, even if both sides benefit]
```

---

## 延伸

- **语体背景**：本篇是**观点评述 / 批判性分析（commentary / critical analysis）**，与同卷相邻的 [[2018阅读/2018-passage1-vocational-education-精读笔记]]（为被轻视的职业教育辩护）与 [[2018阅读/2018-passage2-renewable-energy-精读笔记]]（为势头正盛的可再生能源作证）恰好构成一组"**议题—句法**"对照：那两篇一为"翻案"、一为"作证"，本篇则是**批判与揭露**——**"看似厉害的数字巨头，实则在用'服务'换取我们的数据；唯一能制衡它们的竞争法，又太慢、且根本管不到'不付费的用户'"**。其句法特征是**"让步—转折 + 修辞反问 + 类比论证 + 形式主语"四件套**：用 `Competition law appears to be the only way … But it is clumsy`（**让步—转折**）开题批驳、用 `What political journalist … would not want to know …?`（**修辞反问**）放大论点、用 `Just as some ants farm … so Google farms us`（**类比**）收束点题、用 `It may be that …`（**形式主语**）引出谨慎判断。**"文章靠什么说话"决定了它的句法选择**：一篇"揭露不对等关系"的评述，必然向"**让步后转折**"与"**反问 + 类比**"倾斜。
- **读法建议**：本篇的**命题坐标是"一段一个功能"**——P1 点破数据价值（第 31 题）、P2 承诺与背弃（第 32 题）、P3 竞争法两重困境（第 33、34 题）、P4 蚂蚁类比收束（第 35 题）。考研阅读的惯例是**"题干问什么，就回哪一段找"**。三个好习惯：① **遇 `But`、`while` 就标"让步/转折点"**——作者真正的主张常在其后（`But it is clumsy`、`But there is a deeper conceptual problem, too`）；② **遇"引述与承诺"（`promised … that …`）要盯住它是否被兑现**——`broke the promise almost as soon as …` 是**关键评判**；③ **遇类比（`Just as …, so …`）先找"被比作什么"**——把 `ants : aphids :: Google : us` 的对应关系列出来，第 35 题即迎刃而解。
- **概念延伸**：**"数据即商品"（data as commodity）** 与 **"注意力经济"（attention economy）** 是当代数字经济批评的核心议题：平台以"免费服务"为名，把用户的**社交关系、行为记录、偏好**转化为可出售的**广告定向资产**；于是**用户不是顾客，而是被出售的商品**（`The users of their services are not their customers`）——这正是"**如果你不为产品付费，你就是产品**"的经济学版本。与之相伴的是**竞争法（competition law / antitrust）的滞后**：传统反垄断以"**消费者福利—价格**"为标尺，可当服务"免费"时，这套标尺**失灵**（`this is not obvious when the users of these services don't pay for them`），于是欧盟、美国近年反复讨论如何把**数据与隐私**纳入竞争分析。文中 **`imbalances of power` / `abuses of power` / `to the disadvantage of`** 揭示了一条更深的线索：**当市场权力高度集中，法律工具的"慢"本身就是一种结构性劣势**。可与 [[2017阅读/2017-passage4-wildfire-精读笔记]]（治理与责任的争议）、[[2016阅读/2016-passage2-prairie-chicken-精读笔记]]（利益与管制的博弈）并读——**几篇都在追问"谁掌握权力、规则能否跟上现实"。**
- **对比阅读**：**"强大的新主体 vs 滞后的旧规则"这一母题在题库中反复出现**——本篇用"**竞争法太慢、用户不是顾客**"揭穿制衡的失效，与 [[2017阅读/2017-passage2-screen-time-精读笔记]]（为屏幕时间"翻案"、反对简单的有害论）**形异而神同**：**都主张拒绝非黑即白的流行判断，转而在"事实与结构"上重新审视问题**。**串起来读，可以看到考研阅读如何围绕"主流叙事 vs 被忽略的真相"反复命题**：本篇是**鲜明的"揭露式评述"**——读者须紧盯让步从句之后的转折（`But it is clumsy` / `But there is a deeper conceptual problem, too`），切勿把作者承认的那句"竞争法是唯一办法"误当成主旨。
- **词汇复习**：`digital economy / the giants of / upmarket / grocery chain / physical product / European commission / link A to B / go through / party whip / the makeup of / competition law / imbalances of power / for one thing / by the time / abuse of power / to the disadvantage of / virtual giants / dominate / for the benefit of / convert A to B / farm / aphids / honeydew / yield / predatory insects / spammers / keep A away from B / keep A out of B / even if / as soon as / not so much A but B / enormously revealing / clumsy / remedy`。
- **联动复习**：语法结构见 [[语法总结笔记]]，固定搭配与辨析见 [[固定搭配与词组笔记]]；建议用 `By the time …, it may have vanished …, to be replaced by …`（时间状语从句 + 结果状语，标注"不定式不表目的"）、`Competition law as presently interpreted deals with … and this is not obvious when …`（as + 过去分词定语 + when 条件从句）、`Just as some ants farm …, so Google farms us for the data that …`（类比 + 双重定语从句）各写一句，以巩固本篇最核心的三组结构。

---

## 思考题

1. P1 的 `The power and ambition of the giants of the digital economy is astonishing—Amazon has just announced the purchase of the upmarket grocery chain Whole Foods for $13.5bn, but two years ago Facebook paid even more than that to acquire the WhatsApp messaging service, which doesn't have any physical product at all.` 中，主语的核心词是什么、谓语为何用**单数** `is`？破折号插入语里的两个分句各是什么、`even more than that` 中的 `that` 指代什么？`which` 引导什么从句、能否改成 `that`？再想：**这一句如何为第 31 题"Facebook 收购 WhatsApp 是为了用户信息"埋下伏笔？**
2. P2 的 `Facebook promised the European commission then that it would not link phone numbers to Facebook identities, but it broke the promise almost as soon as the deal went through.` 中，`that` 引导什么从句、能否省略？`link A to B` 的介词为何是 `to`？`as soon as` 引导什么从句、`went through` 在此是什么意思？请把 `but` 前后两个分句的主谓宾划出来。再想：**`broke the promise` 这一"背弃"如何支撑第 32 题"关联动作会给用户带来风险"的推断？**
3. P2 的 `What political journalist, what party whip, would not want to know the makeup of the WhatsApp groups in which Theresa May's enemies are currently plotting?` 中，这是什么句式、实义是肯定还是否定？`in which` 引导什么从句、先行词是什么、介词 `in` 由谁决定？`party whip` 与 `makeup` 分别是什么意思？再想：**作者为何要用"反问"而非直接陈述"这些数据很有价值"？**
4. P3 的 `By the time a problem has been addressed and remedied it may have vanished in the marketplace, to be replaced by new abuses of power.` 中，`By the time` 从句为何用**现在完成时**、主句为何用 `may have vanished`？`to be replaced by …` 是什么成分（目的还是结果）？如何验证你的判断？再想：**这一句与第 33 题 [D] `cannot keep pace with the changing market` 是何关系？**
5. P3 的 `Competition law as presently interpreted deals with financial disadvantage to consumers and this is not obvious when the users of these services don't pay for them.` 中，`as presently interpreted` 是什么成分、相当于什么从句？`when` 在此表"时间"还是"条件"、依据是什么？`this` 指代什么？再想：**这一句与 `The users of their services are not their customers.` 合起来，如何构成第 34 题 [A] `they are not defined as customers` 的完整依据？**
6. P4 的 `Just as some ants farm the bugs called aphids for the honeydew they produce when they feed, so Google farms us for the data that our digital lives yield.` 中，`Just as …, so …` 是什么结构、用于什么目的？`called aphids` 是什么成分？`they produce when they feed` 省略了什么、其中 `when they feed` 又是什么从句？`that our digital lives yield` 修饰什么？再想：**把"蚂蚁：蚜虫 = Google：用户"的对应关系列出来，第 35 题 [D] 为何正确、[A] 为何错误（提示：看末句的 `even if`）？**

---

## 相关笔记

- [[语法总结笔记]]
- [[固定搭配与词组笔记]]
- [[单词辨析]]
- [[阅读心得]]
- [[2018阅读/2018-passage1-vocational-education-精读笔记]]
- [[2018阅读/2018-passage2-renewable-energy-精读笔记]]
- [[2017阅读/2017-passage2-screen-time-精读笔记]]
- [[2017阅读/2017-passage4-wildfire-精读笔记]]
- [[2016阅读/2016-passage2-prairie-chicken-精读笔记]]
- [[2016阅读/2016-passage3-deep-reading-精读笔记]]
- [[2015阅读/2015-passage1-stress-at-home-精读笔记]]
"""

fa = body(os.path.join(DIR, "formatted-article.md"))
tr = body(os.path.join(DIR, "translation.md"))
gr = body(os.path.join(DIR, "grammar-notes.md"))
co = body(os.path.join(DIR, "固定搭配与词组笔记.md"))

note = (
    FRONT + fa + "\n" + MID_QUESTIONS + tr + "\n" + MID_TRANS_Q + gr
    + "\n\n---\n\n## 固定搭配与词组\n\n" + co + "\n" + TAIL
)

# normalize: exactly one blank line around ---, collapse 3+ blank lines
note = re.sub(r"\n{3,}", "\n\n", note)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, "w", encoding="utf-8").write(note)
print("written:", OUT, len(note.split("\n")), "lines")
