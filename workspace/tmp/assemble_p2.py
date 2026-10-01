import re, pathlib

root = pathlib.Path("/Users/zhqznc/Documents/考研英语阅读")
inter = root / "intermediate/2017-passage2-screen-time"

def body(path):
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        text = parts[2] if len(parts) >= 3 else text
    return text.strip("\n").strip() + "\n"

fa = body(inter / "formatted-article.md")
# drop the questions block from the article body (rendered separately as ## 题目)
i = fa.find("## Reading Comprehension Questions")
if i != -1:
    fa = fa[:i].rstrip("\n") + "\n"
tr = body(inter / "translation.md")
gr = body(inter / "grammar-notes.md")
co = body(inter / "固定搭配与词组笔记.md")

# rename questions section in translation
tr = tr.replace("## Reading Comprehension Questions", "## 题目翻译")

manual = (root / "workspace/tmp/p2-manual.md").read_text(encoding="utf-8").strip("\n") + "\n"

out = manual
for marker, content in [
    ("<!--BODY:formatted-article-->", fa),
    ("<!--BODY:translation-->", tr),
    ("<!--BODY:grammar-->", gr),
    ("<!--BODY:collocations-->", co),
]:
    assert marker in out, f"missing marker {marker}"
    out = out.replace(marker, content)

out = re.sub(r"\n{3,}", "\n\n", out)

dst = root / "2017阅读/2017-passage2-screen-time-精读笔记.md"
dst.write_text(out, encoding="utf-8")
print("written:", dst)
print("lines:", out.count("\n"))
print("vocab slots:", out.count("<!-- VOCABULARY_SLOT -->"))
print("callouts:", out.count("> [!abstract]- 长难句分析"))
for h in re.findall(r"^#+ .*$", out, flags=re.M):
    print("H:", h)
