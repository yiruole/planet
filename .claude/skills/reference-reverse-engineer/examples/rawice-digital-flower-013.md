# 案例:RAWICE《DIGITAL FLOWER #_013》重瓣牡丹开花

来源:小红书视频(2026-07,10.1s 1280×720 24fps 单镜头)。本案例已实际执行完整闭环:逆向 → Houdini 复刻 → 预览渲染。工程见 `~/Desktop/Digital Art/Houdini/bloom/`。

## OBSERVED(出处:contact sheet 12 格 + 逐 shot 代表帧)

- 单连续镜头,无剪辑(scene detection 0 cuts @threshold 0.3)
- 花苞→全开的连续开花,全程约 10s;t≈0–3.4s 花苞期(绿萼包裹),t≈3.4–7s 外瓣快速展开,t≈7–10s 花芯缓慢舒展
- 淡粉紫外瓣(大、光滑、波浪边),奶油白花芯(密集小卷瓣,尖端微黄),基部绿色萼片
- 黑背景,单侧主光(右上),花瓣有透光感(边缘亮)
- 机位缓慢推近+轻微环绕,浅景深(前后花瓣虚化)
- 画面有轻微颗粒和柔和 bloom,标题字排版(数字系列作品)

## INFERRED

- 3D 渲染而非实拍延时:开花速度均匀无生物节律、花瓣运动过于连续、高光滚动完美 (high)
- 程序化花瓣系统:各层花瓣形态统计一致、逐层错峰开放有明确时序函数特征 (high)
- 离线渲染:SSS 质量、微距景深、无实时渲染的 GI 妥协痕迹 (medium)
- 具体软件 UNKNOWN 偏 Houdini/Blender 类 DCC;"Flower Gen" 水印暗示自建生成器 (low)

## UNKNOWN

- 花瓣是否有布料/碰撞模拟(可能纯变形驱动)
- 材质细节贴图来源(程序化 or 扫描)
- 调色/合成在哪一步完成

## Pipeline 候选

1. **Houdini Python SOP 程序化花瓣 + 时序函数**(选用):完全可控、参数化迭代快;缺点是写形态代码工作量大
2. Blender Geometry Nodes:节点化直观;但分层时序逻辑在 GN 里表达繁琐
3. 实拍延时 + AI 生成:不可控,放弃

## 复刻要点(实测得出)

- 开花缓动:先快弹后慢展(`bloom_ease`:t<0.18 快速段到 0.42,之后 2.8 次幂缓出)
- 分层时序:外层 delay 小先开,花芯 delay 0.45+ 且 open_cap≈0.5–0.74(永不全开,保持团簇)
- 每瓣 ±0.06 错峰 + 倾角/半径抖动,消除机械感
- 叶脉位移要 0.055–0.09×scale 才能扛住 1 次 Catmull-Clark 细分
- SSS 别超 0.35,否则点色被冲灰;透光感主要靠背面轮廓光
- 坑:`(1-s)**幂` 的 s 必须 clamp [0,1],浮点误差会产生复数 crash cook

## 验证证据

- 预览:`bloom/render/peony_bloom_preview.mp4`(30 帧,f1 花苞/f61 半开/f117 全开三态确认)
- 分析产物:media_inspect 输出 metadata.json / shots.json / contact_sheet.jpg
