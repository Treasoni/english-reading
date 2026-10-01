#!/usr/bin/env python3
"""P9 incremental merge for 2017-passage2-screen-time into the two root summary notes."""
import pathlib
import re

ROOT = pathlib.Path("/Users/zhqznc/Documents/考研英语阅读")
DATE = "2026-10-01"
SRC_TAG = "（来源：2017-passage2-screen-time）"

# ---------------------------------------------------------------- grammar block
g_src = (ROOT / "intermediate/2017-passage2-screen-time/grammar-notes.md").read_text(encoding="utf-8")
g_body = g_src.split("---", 2)[2]                      # drop frontmatter
i = g_body.find("## 一、从句")                          # drop the intermediate file's own title + 来源说明
assert i != -1, "找不到 ## 一、从句"
g_body = g_body[i:].strip("\n") + "\n"

lines = []
for ln in g_body.split("\n"):
    if ln.startswith("### "):
        title = ln[4:].strip()
        if title == "跨节联动复习":
            ln = "### 联动复习：2017 Passage 2 与既有语法点的交叉" + SRC_TAG
        elif not title.endswith(SRC_TAG):
            ln = "### " + title + SRC_TAG
    lines.append(ln)
g_body = "\n".join(lines)

grammar_block = (
    "## 2017 新增语法要点（2017 Passage 2）\n\n"
    "> [!abstract] 更新说明\n"
    "> 本节追加 2017 Passage 2 源笔记中的语法点，按原篇各节顺序并入本汇总；本篇**用户未提供语法源笔记**，语法点由 `formatted-article.md` 与 `translation.md` **推断提取**，只收录本篇实际出现的结构。\n"
    "> 每节标题后标注来源篇章；本篇的**固定搭配、词汇辨析与速记卡片**已并入独立笔记 [[固定搭配与词组笔记]] 的「2017 新增固定搭配与词汇」一节，建议两处对照复习。\n\n"
    "---\n\n" + g_body
)

# ---------------------------------------------------------- 语法总结笔记.md edits
gp = ROOT / "语法总结笔记.md"
g = gp.read_text(encoding="utf-8")

def sub_once(text, old, new, label):
    assert text.count(old) == 1, f"{label}: 匹配 {text.count(old)} 次，应为 1"
    return text.replace(old, new)

g = sub_once(g, "updated: 2026-09-29\n", f"updated: {DATE}\n", "grammar updated")
g = sub_once(g, "total_sources: 65\n", "total_sources: 66\n", "grammar total_sources")
g = sub_once(
    g,
    '  - "intermediate/2017-passage1-parkrun/grammar-notes.md | 2026-09-29 | processed"\n',
    '  - "intermediate/2017-passage1-parkrun/grammar-notes.md | 2026-09-29 | processed"\n'
    '  - "intermediate/2017-passage2-screen-time/grammar-notes.md | 2026-10-01 | processed"\n',
    "grammar processed_sources",
)
g = sub_once(g, "本笔记整合了 `intermediate/` 下 65 篇单篇语法笔记", "本笔记整合了 `intermediate/` 下 66 篇单篇语法笔记", "grammar 使用说明")

# 快速索引：从句 37 -> 38
g = sub_once(
    g,
    "such A as B 举例结构 | 37 | ★★★★★ |",
    "such A as B 举例结构；**2017 P2**：that 引导的宾语从句与定语从句之辨（found that … / an ideology that demands …）、who 限定性定语从句、if 条件状语从句的两处位置、as 引导的时间 / 方式状语从句之辨、when 时间状语从句的省略（when absorbed in a device）、which 指代整句的非限定性定语从句、三重 that 从句层层嵌套（concerned that … that demands that … should …）、demand that … (should) do 的虚拟语气宾语从句 | 38 | ★★★★★ |",
    "grammar 索引 从句",
)
# 非谓语动词 33 -> 34
g = sub_once(
    g,
    "分词作前置定语（an accelerating rate / a puffed-out first-timer） | 33 | ★★★★★ |",
    "分词作前置定语（an accelerating rate / a puffed-out first-timer）；**2017 P2**：过去分词短语作后置定语（devised by …）、不定式作目的状语 vs 后置定语的判别（to try to understand / time to have a shower）、不定式套不定式、动名词（含否定式 not doing）作介词宾语与并列、并列不定式的“共享 to”（to have a shower, do housework or simply have a break）、get sth out of doing sth | 34 | ★★★★★ |",
    "grammar 索引 非谓语",
)
# 介词与连词 38 -> 39
g = sub_once(
    g,
    "provide A for B | 38 | ★★★★ |",
    "provide A for B；**2017 P2**：with 复合结构作状语（With so much focus on …）、be wired to / be responsive and sensitive to / expose sb to sth / be born out of / be based on（形容词、动词 + 介词 to 的搭配群） | 39 | ★★★★ |",
    "grammar 索引 介词与连词",
)
# 补充要点 50 -> 51
g = sub_once(
    g,
    "熟词生义（lever / staff / preside over / halve / state / opposition） | 50 | ★★★ |",
    "熟词生义（lever / staff / preside over / halve / state / opposition）；**2017 P2**：构词法（bleed-over / mealtimes / nonverbal / upper-middle-class / food-testing / unresponsive）、熟词生义（present / wired / capture / bids / value / available / source / routine / focus / tension） | 51 | ★★★ |",
    "grammar 索引 补充要点",
)

g = g.rstrip("\n") + "\n\n---\n\n" + grammar_block.rstrip("\n") + "\n"
gp.write_text(g, encoding="utf-8")
print("语法总结笔记.md:", len(g.split("\n")), "行")

# ------------------------------------------------- 固定搭配与词组笔记.md edits
cp = ROOT / "固定搭配与词组笔记.md"
c = cp.read_text(encoding="utf-8")
c_block = (ROOT / "workspace/tmp/p2-colloc-append.md").read_text(encoding="utf-8").strip("\n") + "\n"

c = sub_once(c, "updated: 2026-09-29\n", f"updated: {DATE}\n", "colloc updated")
c = sub_once(c, "total_sources: 65\n", "total_sources: 66\n", "colloc total_sources")
c = sub_once(
    c,
    '  - "intermediate/2017-passage1-parkrun/固定搭配与词组笔记.md | 2026-09-29 | processed"\n',
    '  - "intermediate/2017-passage1-parkrun/固定搭配与词组笔记.md | 2026-09-29 | processed"\n'
    '  - "intermediate/2017-passage2-screen-time/固定搭配与词组笔记.md | 2026-10-01 | processed"\n',
    "colloc processed_sources",
)
c = sub_once(c, "  - 2017新增专题\n", "  - 2017新增专题\n  - 2017P2新增专题\n", "colloc categories")

# 使用说明：2017 新增专题 描述追加 Passage 2
c = sub_once(
    c,
    "速记卡片含五题定位速查与写作可迁移表达）",
    "速记卡片含五题定位速查与写作可迁移表达；**Passage 2**：screen use、digital play、maximal engagement、bleed-over into、suck sb in、promote maximal engagement、disengage、be wired to do、be absorbed in、put on a blank expression、capture one's attention、make bids for、be responsive and sensitive to、be born out of、expose sb to、neglect sb、have a break from、get some work out of the way、get a lot out of doing、be available to、be exquisitely present、there needs to be、just because … doesn't mean …；熟词生义 present / wired / capture / bids / value / available / source / routine / focus / tension；易混辨析 verbal / nonverbal、neglect / ignore、responsive / sensitive、distressed / distressing、present / absent、be born out of / be based on；速记卡片含十组搭配与一条论证链条记忆线索）",
    "colloc 使用说明",
)
# 快速索引：2017 新增专题 涉及篇章 1 -> 2
c = sub_once(
    c,
    "pride / prize / praise / price | 1 | ★★★★ |",
    "pride / prize / praise / price；**Passage 2**：screen use、digital play、maximal engagement、bleed-over into、suck sb in、promote maximal engagement、be wired to do、be absorbed in、put on a blank expression、capture one's attention、make bids for、be responsive and sensitive to、be born out of、expose sb to、have a break from、get some work out of the way、get a lot out of doing、be available to、be exquisitely present、there needs to be、just because … doesn't mean …；熟词生义 present / wired / capture / bids / value / available / source / routine / focus / tension；易混辨析 verbal / nonverbal、neglect / ignore、responsive / sensitive、distressed / distressing、be born out of / be based on | 2 | ★★★★ |",
    "colloc 索引 2017 新增专题",
)

c = c.rstrip("\n") + "\n\n" + c_block
cp.write_text(c, encoding="utf-8")
print("固定搭配与词组笔记.md:", len(c.split("\n")), "行")