# 1. Overview

**【角色】**

用户:

* 超级用户：由指令(python create_admin)创建，且超级用户为所有项目的管理员

* 普通用户：由超级用户在django后台创建，可被分配项目角色

角色：

* 管理员：管理项目的所有数据
* 审查员：可标注数据及将数据条目设置为已完成
* 标注员：只可标注数据

**【功能概览】**

|          | 超级用户 | 管理员 | 审查员 | 标注员 |
| -------- | -------- | ------ | ------ | ------ |
| 项目管理 | √        |        |        |        |
| 数据管理 | √        | √      |        |        |
| 标签管理 | √        | √      |        |        |
| 关系管理 | √        | √      |        |        |
| 成员管理 | √        | √      |        |        |
| 指南编辑 | √        | √      |        |        |
| 查看统计 | √        | √      |        |        |
| 审查数据 | √        | √      | √      |        |
| 标注     | √        | √      | √      | √      |

**【原项目】**

doccano https://github.com/doccano/doccano 



# 2. Run

## 3.1 Clone

```bash
git clone https://gitee.com/HITSZ-CS/sequence_labeling.git

# windows
git clone https://gitee.com/HITSZ-CS/sequence_labeling.git --config core.autocrlf=input
```



## 3.2 前端

```bash
# 前端nuxt.js
cd frontend

# 当前node版本10.19，太新会出现依赖报错
# 安装node与npm，切换node版本
sudo apt install nodejs npm
sudo npm install n -g
sudo n 10.19

# 安装依赖
npm install

# 运行
	# 调试模式
npm run dev
	# 运行模式
npm run build
npm run start
```



## 3.3 后端

```bash
# 后端django
cd backend

# 安装依赖
# 若提示安装psycopg2报错，请安装postgresql(如apt install postgresql)
pip install -r requirments.txt

# 清空数据库
# 删除api/migrations下除__init__.py的所有文件
# 删除db.sqlite3文件

# 数据库创建/更新
python3 manage.py makemigrations
python3 manage.py migrate

# 创建角色表
python3 manage.py create_roles
# 创建超级用户
python3 manage.py create_admin

# 运行
python3 manage.py runserver 0.0.0.0:8000

# 由gunicorn部署
# ln -s /usr/local/bin/python3/bin/gunicorn /usr/bin/gunicorn
gunicorn --bind="0.0.0.0:8000" --workers="4" backend.wsgi --timeout 300
# nohup gunicorn --bind="0.0.0.0:8000" --workers="4" backend.wsgi --timeout 300 > sq_backend.log 2>&1 &

# 运行地址 127.0.0.1:3000
# 后台地址 127.0.0.1:8000/admin
```



## 3.4 nginx

```bash
# 若非运行在本地，使用nginx代理

# 修改nginx/sl.nginx.conf下，第3行server_name和第54行/backend/static对应的文件路径

# 将配置文件赋值到nginx目录
cp nginx/sl.nginx.conf /etc/nginx/conf.d/

# 重启nginx
nginx -s reload
nginx -t

# 运行地址 {server_name}
# 后台地址 {server_name}/admin
```



# 3. Functions

## 3.1 数据

**【导入数据】**

**请注意使用UTF-8编码格式的文件**

对于TXT文件：

- 默认使用换行符分割数据条目（若存在空行会导致导入失败）
- 可选择输入分割符号

**【导出数据】**

选择第一个JSON导出选项导出可保留连线信息。单个数据示例：

```json
{
	"id": 1, 
	"text": "小儿3岁，一直有点流清鼻涕。偶尔有点咳嗽。有没有发现您的孩子有过敏的症状?发现了,孩子确实有过过敏。孩子现在打喷嚏吗?孩子现在没有打喷嚏。您的孩子有可能得了过敏性鼻炎,建议去医院进一步确认病情.", 
	"annotations": [
			{"id": 1, "label": "1", "start_offset": 5, "end_offset": 8, "username": "admin"}, 
			{"id": 2, "label": "1", "start_offset": 23, "end_offset": 27, "username": "admin"}, 
			{"id": 3, "label": "3", "start_offset": 39, "end_offset": 44, "username": "admin"}, 
			{"id": 5, "label": "2", "start_offset": 54, "end_offset": 59, "username": "admin"},
			{"id": 19, "label": "3", "start_offset": 70, "end_offset": 75, "username": "lqy"}
	], 
	"connections": [
			{"source": 1, "to": 5, "relation": "attrOf"}, 
			{"source": 5, "to": 2, "relation": "attrOf"}, 
			{"source": 2, "to": 3, "relation": "attrOf"}
	], 
	"annotation_approver": null,
	"entity_concordance": "1.0000", 
	"relation_concordance": "0.0000"
}
```



## 3.2 标注

**【界面区别】**

- 多个成员的标注情况：
  - 除标注员，其他角色均可显示该数据条目的多个成员标注情况
- 审查按钮：
  - 除标注员，其他角色均可显示
  - 点击‘√’将该数据条目设置为‘已完成’

**【过滤】**

- 已/未标注：当前用户有/无标注的数据

**【实体标注】**

- 选择文本，从弹出框选择标签
- 请注意：显示多个标注情况时，**在某用户的标注情况内进行标注，该标注将被该用户拥有**

**【实体关系】**

- 连线：从实体拖拽出连线到另一实体（不允许：重复连线，反向连线，自连线）
- 设置关系：单击连线，从弹出框选择关系
- 删除连线：双击连线
- 显示/隐藏连线：单击实体右上角按钮，在只显示该实体相关连线和显示全部连线切换。若处于只显示实体1的状态，单击实体2的按钮，则只显示实体2的连线（该状态会延续到其他数据条目，即在数据1只显示实体1，切换到数据2时，将无连线显示）



## 3.3 标签

**【创建标签】**

输入‘标签名’与‘快捷键’，选择‘颜色’

- **标签名与快捷键不可重复**

**【导入标签】**

```json
[
	{
		"text":"类型1",
		"suffix_key":"1",
		"background_color":"#03A9F4"（可选项，无该项则随机初始化颜色）
	},
]
```

**【导出标签】**

```json
[
	{
		"id":1,
		"text":"类型1",
		"prefix_key":null,
		"suffix_key":"1",
		"background_color":"#03A9F4",
		"text_color":"#ffffff"
	},
]
```



## 3.4 关系

**【创建关系】**

输入‘关系名’，选择‘颜色’

- **关系名不可重复**

**【导入关系】**

```json
[
	{
		"text":"类型1",
		"color":"#03A9F4"（可选项，无该项则随机初始化颜色）
	},
]
```

**【导出关系】**

```json
[
	{
		"id":5,
		"text":"attrOf",
		"color":"#03A9F4"
	},
]
```



## 3.5 成员

**【添加成员】**

* 将某普通用户设置为该项目的某角色

- 用户搜索接口只显示普通用户，不显示超级用户（超级用户可管理所有数据）



## 3.6 指南

- 由于每次修改内容都会上传数据，快速输入时存在问题，建议从别处复制粘贴到此处



## 3.7 统计

- 已完成的数量为已审查的数据数量（在标注界面点击‘确认/取消’按钮）



## 3.8 一致性

- 实体一致性和关系一致性，两者独立计算
- 数据条目由多个用户的标注情况计算
- 项目的一致性由项目下所有数据条目的一致性取均值
- 计算公式：fleiss's kappa
- 参考资料：
  - https://www.jianshu.com/p/f9c383b39859
  - https://en.wikipedia.org/wiki/Fleiss'_kappa