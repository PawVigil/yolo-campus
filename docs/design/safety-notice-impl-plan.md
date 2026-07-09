# SafetyNotice.vue 视觉重构 — 实施计划

> 仅修改视觉/UI，不触碰 script 逻辑、API 调用、数据处理。

---

## 实施顺序

### Step 1: 新增 CSS 变量

在 `tokens.css` 中追加公告栏相关的颜色变量：

- 木板基底 `--color-board-wood`
- 木板边框 `--color-board-frame`
- 羊皮纸基底 `--color-parchment`
- 羊皮纸亮部 `--color-parchment-light`
- 羊皮纸暗部 `--color-parchment-dark`
- 羊皮纸厚度条 `--color-parchment-edge`
- 铜钉 `--color-copper-pin`
- 铜钉亮 `--color-copper-pin-light`
- 铜钉暗 `--color-copper-pin-dark`

### Step 2: 公告栏容器 (Notice Board)

修改 SafetyNotice.vue 的 template 和 style：

- 外层容器：木纹背景 + 原木边框 + 整体阴影
- 猫爪印装饰（两个伪元素 ::before / ::after）
- 内部 padding

### Step 3: 顶部横幅

- 改造现有 `.safety-banner` 为木条材质风格
- 保持原有结构，只改样式

### Step 4: 单张公告 (Notice Poster)

- 羊皮纸背景 + 径向渐变
- 毛边效果 (clip-path)
- 卷角效果 (右下角伪元素)
- 厚度条 (底部伪元素)
- 铜钉 (顶部伪元素)
- 预设旋转角度 (i % 6 循环)

### Step 5: Hover 交互

- 纸张抬起 translateY(-4px)
- 阴影加深
- z-index 提升
- 300ms ease 过渡

### Step 6: 响应式

- 桌面 2~3 列
- 平板 2 列
- 手机 1 列

---

## 不动的部分

- script 标签全部不动
- API 调用不动
- 组件导入不动（PublicNav, LocationBadge）
- 数据获取逻辑不动
- loading/error/empty 状态逻辑不动
