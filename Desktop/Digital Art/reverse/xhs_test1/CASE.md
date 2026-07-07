# CASE:backrooms audio-relight(压力测试 1)

2026-07-07 · 参考:小红书 @by__nils 转发作品(《后室》风格,音频驱动灯光)
管线:Blender 灯光分组静帧层 → TD 三段分频 + noise 门控混合 → TD 后期 → 图像序列导出。
通用经验已反写 fidelity-rules / reference-reverse-engineer / touchdesigner-effect-builder;**本文件只存本案例私有参数与过程事实**。

## 高保真升级(3 轮,2026-07-07 晚)

- **R1 资产语义**:`build_scene_v2.py`——8 种程序化家具原型(椅/办公椅/桌/扶手椅/抽屉柜/台灯/木板/凳)+ bevel + 程序磨损材质(noise 色斑 + AO 脏 + roughness 方差)+ 天花板灯板方差与坏灯。**刚体 settle 走了 4 次失败**(互穿爆炸/穿透/ kinematic 顶穿,物体被弹到数百米外;headless Bullet 堆叠是工程黑洞),改**确定性堆叠放置**(中心密度采样+支撑高度查询+倾斜抖动+嵌入下沉),40/40 成功。另修 join 陷阱:join 保留 active 件非均匀 scale,后续覆盖 scale 会把腿拉成 8 米——join 后必须 `transform_apply(scale=True)`
- **R2 密度/构图/色调**:62 件、中心密度 u^0.5、footprint×0.6、sink 0.2、木色调暗,相机推近 (0,-5.35,1.02)
- **R3 收尾**:织物/皮革再暗、堆顶上限 3.0、墙偏黄、TD 加 HALO(bright-pass→blur→add 0.5)、fluo 阈值 0.012→0.010(重启后闪光密度掉到 6 次,调回 17 次)
- 成片 `audio_relight_v7_final.mp4`;对比图在 `compare/`(A 参考/B 旧/C 新、rounds_progression、E_hero_1440)

## 状态(截至测试 1 收束)

- 机制:层混合/音频驱动/状态闪烁成立;v5 为当前最佳(`audio_relight_v5.mp4`)
- mechanism gate #2(声画相关性)未达标:ours vs 高频段 0.17@lag10,参考 vs 整轨 RMS 0.65@lag1——lag release 延迟 + 随机门错时是主因,判据本身也需修订(应对驱动频段而非整轨)
- 保真复盘结论:资产语义/接触/材质谱系为最大差距(面板盲区),升级轮待用户决定
- proxy 升级票据(未关闭):原语堆→语义资产;无 settle→rigid body;平坦材质→bevel+磨损;天花板均匀→方差;TD 后期缺 halation

## Blender 底板(build_plates.py)

- 房间 14×10×3m,机位 (0,-6.4,1.15) lens 26mm,720×560,Eevee Next,taa 160
- 4 层:L0 暗底(world 0.06/0.075/0.09 × 0.22)/ L1 灯泡(point 160W 色 1.0,0.75,0.45 + 球 emit 60,**必须放堆外可见凹口** (-0.35,-1.35,1.72),埋进几何=全黑)/ L2 顶部柔光(area 4.5m 320W 冷)/ L3 荧光阵(6×4 panel emit 2.2 + 稀疏 area 60W;初版 200W/emit 6 过曝成白仓库)
- 墙 0.30,0.28,0.19 / 地板 0.10,0.075,0.05 / 木色 0.16-0.21 系(初版亮 2 倍→纸箱感更重)

## TD 网络(td_c1/c2/c3.py 幂等重放;audio_relight.toe)

- 分频 cutofflog:low 2.2 / band 2.9 / high 3.5;analyze=rmspower;lag:prac .08/.15,soft .06/.1,fluo .02/.25
- flick:noise CHOP random,period **0.45**(0.12 出针尖;0.45 出状态平台),seed 7
- 顺序采集的 ctrl 分位数(本音轨):prac p50 .0038/p90 .156;soft p50 .054/p95 .161;fluo p50 .004/p90 .0135/p95 .021
- 最终 opacity 表达式(v5):
  - prac = `min(1, 0.45 + 0.25*ctrl_prac)`
  - soft = `min(0.85, max(0, ctrl_soft*4 - 0.35))`
  - fluo = `(0.6 + 0.4*abs(flick)) if (ctrl_fluo > 0.012 and flick > -0.45) else 0`(阈值 0.0075 时安静段误闪)
- 后期:GRAIN(noise TOP mono,seed=absTime.frame,add @0.06)→ HSV(sat .85, val .95);L0 前置 level opacity 0.55(暗态基线 46→34,参考 32)
- 导出:逐帧 OUT.save jpg ×1260(15s)→ `ffmpeg -framerate 30 -i seq/f%05d.jpg -i ref_audio.wav -c:v libx264 -crf 18 -c:a aac -shortest`

## 迭代轨迹(证据面板驱动)

v1 针尖闪+基线过亮 → v2 重标定(乱序 scrub 统计不可信,白调一轮)→ v3 慢包络主导修正 → v4 平台化(flick 0.45 + 二值闩锁)但安静段误闪 → v5 阈值上调+电平随机化:安静段干净、亮帧占比 13.1% vs 参考 15.4%、基线对齐、平台多电平。

## 盲测比对(详见 blind_check.md)

机制四步全中(Blender 灯光分组/每灯一层/TD 三段分频/映射灯光强度+随机闪);本案路由实际不模糊(视频自带节点图 breakdown)——纯效果视频才能真正压路由,选材教训记入测试设计。
