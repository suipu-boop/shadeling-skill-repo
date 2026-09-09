# shadeling-skill-repo

Shadeling 技能市场官方策展源（GitHub Pages 托管）。

- 线上源根：https://suipu-boop.github.io/shadeling-skill-repo/
- 来源：`Shadeling` 仓库 `fixtures/skill_repo/` 的官方子集，线上副本独立演进。

## 环境差异约定

- 本仓库（线上真源）：技能包内 `binary_url` 一律指向 GitHub Release asset（如 `releases/download/<tag>/editor_sdk`）。
- 本地开发源（`Shadeling/fixtures/skill_repo`）：`binary_url` 可用 `http://localhost:<port>/...` 指向本地引擎服务，仅限开发态。
- 两处 JSON 除 `binary_url` 外应保持一致；改技能内容时两侧同步，改分发地址只改本仓库。
