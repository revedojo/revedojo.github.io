import re
JP = re.compile(r'[　-ヿ㐀-鿿＀-￯〜・]')
# segments: runs between delimiters < > ' " ` and newlines
SEG = re.compile(r"[^<>'\"`\n]+")
def segments(text):
    for m in SEG.finditer(text):
        s = m.group(0)
        if JP.search(s):
            core = s.strip()
            if core: yield core
