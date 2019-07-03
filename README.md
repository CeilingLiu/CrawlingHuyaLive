# 爬取虎牙直播视频脚本
## 脚本需求分析
* 输入主播房间号
* 监控主播是否开播
* 开播后自动下载视频片段
* 关播后合并视频片段

## 脚本概要设计
* 使用get请求获取html源码
* 解析源码获取m3u8链接地址
* 拼接ts视频下载地址
* 下载ts
* 合并所有ts视频文件

## 执行脚本步骤

Enter the tiger tooth live room number, automatically record the live video of the anchor, save the low, easy to look back
