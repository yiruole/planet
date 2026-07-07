# Phase 6 — Shot specification(2026-07-08)

## Camera / lens
- 30mm(全幅等效),f/4,焦点=街角空 empty(1.2,1.2,3.0)
- 位置:(10.5,-10.5,1.7)→(6.8,-6.8,1.6)m 线性推近 10s;TRACK_TO 锁定街角
- 高度 1.7m(人眼),无摇移/无手持——运动预算全部给光照状态变化(previs camera logic)

## Lighting plan(三状态)
| 状态 | 帧 | 设定 |
|---|---|---|
| GOLD | 1–150 | Sun energy 8.0,color (1.0,0.74,0.48),elevation 22°,azimuth 25°,angle 0.02(硬影);对面遮挡楼(6×4×8m @ 11,-13.5)投对角影;world 天蓝 0.5 |
| DUSK | 150–200 | Sun→0,world→靛蓝 (0.12,0.16,0.32) 强度 0.075 |
| NIGHT | 200–300 | 壁灯点光 95W 色 (1.0,0.55,0.22) f212/f236 先后亮 + 灯罩 emission 8.0;soft size 0.25 |

## 资产清单(来源/授权记录)
| 资产 | 来源 | 授权 | 格式 | 面数 | 贴图 |
|---|---|---|---|---|---|
| 全部建筑/道具(立面、拱门、招牌、灯柱、壁灯、遮挡楼) | 程序化原语(本脚本) | 自有 | blend 内 mesh | <10k 总计 | 无贴图,noise bump 程序化 |
| 参考照片 2.imagetovideo.JPG | 用户素材 | 用户自有 | JPG 6000x4000 | — | 质感目标,未贴入场景 |

未使用外部资产:Poly Haven/BlenderKit 下载需要联网取大文件,按"未经确认不下载"约束跳过;表面复杂度按分工交给 AI 侧(见 HANDOFF.md)。blocking 层的程序化材质(noise bump 灰泥/沥青)已够控制 passes 用途。
