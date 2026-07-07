---
name: physical-phenomena-sonification
description: 把物理/生命过程(细胞分裂、扩散、裂纹、流体、振动、生物运动)变成声音:视频→结构变量提取(≤4)→数据驱动合成(pitch/rhythm/grain/timbre/空间)。触发词:sonification、声音化、把这个现象做成声音、data sonification。
---

# Physical Phenomena Sonification v0.1

前置:遵守 `~/.claude/skills/creative-rules/`。基于黑水幼鱼案例(鳍拍推进→呼吸性声响)实测。**不是科普配乐**——每个声音成分必须能指回一条数据曲线,指不回去的成分删掉。

## 1. 变量提取(视频→曲线,numpy)

- 特征帧率 = 视频 fps;黑底素材亮度阈值分割即可(黑水/显微镜/暗场都适用);复杂背景需要 ML 分割时如实标记缺口
- **变量池(挑 ≤4 个)**:面积(p5–p98 归一)/ 质心速度(帧间位移+5帧平滑)/ 边界复杂度(周长/2√(πA),圆=1)/ 分裂-合并事件(连通域计数变化)/ 周期(主变量自相关峰)/ 方向性(位移向量角稳定度)
- **先看曲线再设计映射**(variables_panel.png):周期多长、哪段是静默、哪个变量真的在动
- **数据污染检查(实测)**:屏录素材的 UI/转场帧会做出饱和→崩零的假曲线,先裁掉;文件名不可信,逐帧看内容

## 2. 映射设计

- 变量类型分工:**缓变量**(面积/复杂度)→ 音色参数(谐波数/谱宽/detune);**节律量**(周期)→ 振幅调制/脉冲;**事件量**(速度峰/分裂时刻)→ 颗粒/冲击(指数衰减 env,τ 10–50ms)
- 每条映射写"变量→声音参数+物理理由"三元组
- 现象安静时声音必须安静——稀疏是数据的形状,不要填满

## 3. numpy 合成配方(实测模板 `~/Desktop/Digital Art/test/results/phase7/sonify_creature.py`)

- 控制曲线升采样到音频率:`fidx = (t*fps).astype(int)` 逐样本查表
- 谐波堆:`sum(on_h * A^0.7 * (0.5/h) * sin(cumsum(2π f h detune/SR)))`——**频率变化用 cumsum 相位**,直接 sin(2πft) 换频会爆音
- 颗粒:噪声 × 指数衰减 env,高通用 `diff(noise)` 一行代替滤波器
- 母线:`tanh(x*1.4)` 软限幅 + 首尾 0.25s 淡入出;wave 模块写 16bit
- 声画对照视频:ffmpeg 把源画面(裁 UI)与合成音轨 mux,听画同步是最强验收

## 4. 验收

- 盲听测试问题:"声音的呼吸律动和画面的开合是不是同一件事?"——周期锁定听得出来才算成
- variables_panel.png 与成品并列交付:观众/导演能对着曲线听懂每层声音

## 5. 案例库

- **黑水幼鱼**(完整闭环):`~/Desktop/Digital Art/test/results/phase7/`(MAPPING.md + 变量面板 + wav + 声画 mp4);鳍拍 0.27s 周期→sub pulse,面积→谱宽,复杂度→谐波数,速度→颗粒
