# DoubanImageWall

读取豆瓣用户标记为“看过”的电影/“听过”的音乐/“读过”的图书，生成**电影海报墙**/**音乐专辑封面墙**/**图书封面墙**。

大小与排列方式可调。
参考 [workflows 目录](.github/workflows/)以使用 GitHub Actions [更新图片](.github/workflows/generate-image-wall.yml) ，以及[输入任意豆瓣 ID 将运行结果存放于 workflow artifacts](.github/workflows/generate-image-wall-on-demand-for-anyone.yml)。

### 效果图
电影海报墙：
![MoviePosterWall](output/49729399_movie.jpg?raw=true "MoviePosterWall")

音乐专辑封面墙：
![MusicAlbumCoverWall](output/49729399_music.jpg?raw=true "MusicAlbumCoverWall")

### 使用方式
```
pip install -r requirements.txt
python image_wall.py -i={豆瓣 ID}
```
运行完毕后前往 output 文件夹查看成品图。

运行时间视参数与网络状况而定。首次运行或更换 ID 时会需要更久，后续运行由于图片缓存会快许多。

### 已知问题
生成图书封面墙时，很有可能在访问豆瓣的第一步（拉取标记过的图书）就失败。没有已知解决方案。见 [Issue 页](https://github.com/icue/DoubanImageWall/issues/1)。

### 参数说明
| 参数（短） | 参数（长） | 默认值 | 说明 |
| - | - | - | - |
| i | id |  |用户 ID，或含用户 ID 的豆瓣链接 |
| s | sort-by-time | False | 按标记顺序，从近往远排列，并且**被标为五星的条目会优先占据大图位置**。<br>注意，这不是默认排列方式。默认排列方式为**按照该用户给出的打星高低、再从近往远排列**。 |
| rd | random | False| 是否随机排列所有图片。若按标记顺序排列并开启了此选项，五星条目的“大图优先”原则仍然有效。 |
| m | mode | `movie` | `movie`，`music`或`book`。`movie`生成电影海报墙；`music`生成音乐专辑封面墙；`book`生成图书封面墙。设为`music`时，每张图片的高度将等同于宽度。 |
| c | col | 5 | 列数 |
| r | row | 8 | 行数，建议使用偶数 |
| o | offset | 13 |在前四行中每隔多少张图片加入一张大图。图片墙从第五行起会重复前四行的排列方式。<br>设为 0 禁用大图。大图为其余图片的四倍大小，当排列冲突时，程序会提示 offset 无效，可尝试将其调低或调高 1。|
| w | width | 540 | 每张图片的宽度，建议小于 600 |
| ht | height | 750 | 每张图片的高度，建议小于 800。在音乐专辑封面墙上，高度将等同于宽度。 |
| rt | rating | 0 | 按打星过滤，可用数字 1 到 5。设为 0 不过滤。 |
| t | threshold | 300 | 允许保留缓存图片的最大数量。若设为 0，则每次运行后，未被本次运行读取到的缓存图片将被删除。 若设为负数，则运行时不会存储缓存，且所有缓存图片将被删除。|
| l | limit | 200 | 图片处理的最大数量。通常这个值需要高于列数乘以行数，以获得足够多的图片。 |
|   | max-width | 4000 | 成品图的最大宽度（像素） |
|   | max-height | 8000 | 成品图的最大高度（像素） |
