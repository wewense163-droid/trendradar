#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Issue 自动分流机器人（最小版，纯规则分类，零成本）
- 输入：环境变量 ISSUE_TITLE / ISSUE_BODY，或命令行参数 title body
- 输出：JSON {"labels": [...], "comment": "..."}
分类：bug / enhancement / question / documentation / needs-triage
后续可把 classify() 换成大模型 API 调用，接口不变。
"""
import json
import os
import re
import sys

RULES = [
    ("bug", [
        "报错", "崩溃", "闪退", "白屏", "黑屏", "无法", "失败", "异常", "卡住",
        "卡死", "没反应", "不显示", "打不开", "出错", "漏洞", "bug", "error",
        "crash", "exception", "traceback", "500", "404", "stack overflow",
    ]),
    ("enhancement", [
        "希望", "建议", "能不能", "可以增加", "请求", "想要", "支持一下",
        "新功能", "feature", "enhancement", "request", "add support",
    ]),
    ("question", [
        "请问", "怎么", "如何", "为什么", "是什么", "哪里", "?", "？",
        "question", "how to", "help",
    ]),
    ("documentation", [
        "文档", "readme", "教程", "说明写错", "拼写", "typo", "documentation",
    ]),
]

COMMENTS = {
    "bug": (
        "感谢反馈！为了能快速定位问题，麻烦补充以下信息：\n\n"
        "1. **版本**：你用的是哪个版本？\n"
        "2. **环境**：操作系统 / 浏览器 / 运行方式\n"
        "3. **复现步骤**：一步步写出怎么操作出的问题\n"
        "4. **实际结果 vs 期望结果**：分别是什么？\n"
        "5. **报错截图或日志**：有的话请贴出来\n\n"
        "补齐后维护者会优先处理。本评论由自动分流机器人发送。"
    ),
    "enhancement": (
        "感谢建议！已经打上 `enhancement` 标签。\n\n"
        "为了方便评估，欢迎补充：你的使用场景是什么？现在是怎么绕过去的？\n"
        "维护者会按需求热度排期。本评论由自动分流机器人发送。"
    ),
    "question": (
        "感谢提问！已经打上 `question` 标签。\n\n"
        "在等待回复期间，可以先看看项目 README 和已有 Issue 里有没有类似问题。\n"
        "本评论由自动分流机器人发送。"
    ),
    "documentation": (
        "感谢指出文档问题！已经打上 `documentation` 标签，维护者会尽快修正。\n\n"
        "本评论由自动分流机器人发送。"
    ),
    "needs-triage": (
        "感谢提交！已经收到，维护者会尽快确认分类。\n\n"
        "本评论由自动分流机器人发送。"
    ),
}


def classify(title: str, body: str) -> str:
    text = (title + " " + (body or "")).lower()
    scores = {}
    for label, keywords in RULES:
        score = 0
        for kw in keywords:
            if kw.lower() in text:
                # 标题命中权重更高
                score += 2 if kw.lower() in title.lower() else 1
        scores[label] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "needs-triage"


def main() -> None:
    if len(sys.argv) >= 3:
        title, body = sys.argv[1], sys.argv[2]
    else:
        title = os.environ.get("ISSUE_TITLE", "")
        body = os.environ.get("ISSUE_BODY", "")
    label = classify(title, body)
    labels = [label]
    if label == "bug":
        labels.append("needs-info")
    print(json.dumps({"labels": labels, "comment": COMMENTS[label]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
