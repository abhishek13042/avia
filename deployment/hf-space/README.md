---
title: AVIA
emoji: 🍎
colorFrom: blue
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
short_description: Count apples on the tree from orchard video
---

AVIA counts apples in orchard video by segmenting and tracking each one across frames.
Code and documentation: https://github.com/abhishek13042/avia

This Space runs the site, API and worker in one container on CPU. Its disk is reset when
the Space restarts, so uploads last until then and the example runs are restored each time.
