# 1. 概览

## 1.1 功能

|                             | 超级用户 | 管理员 | 审查员 | 标注员 |
| --------------------------- | -------- | ------ | ------ | ------ |
| 创建/删除项目               | √        |        |        |        |
| 导入/导出数据               | √        | √      |        |        |
| 设置标签                    | √        | √      |        |        |
| 为项目分配用户角色          | √        | √      |        |        |
| 修改指南                    | √        | √      |        |        |
| 查看统计数据                | √        | √      |        |        |
| 将标注条目设置为 已/未 完成 | √        | √      | √      |        |
| 标注                        | √        | √      | √      | √      |

其他功能：切换日间/夜间模式；切换中/英文显示

## 1.2 角色

- 总体上，分为超级用户和普通用户
- 超级用户是命令行（python manager.py create_admin）创建的用户，可进入后台进行所有数据的管理
- 项目上，所有用户可被分配管理员/标注员/审查员三种角色

## 1.3 其他说明

* 原项目：[doccano/doccano: Open source text annotation tool for machine learning practitioners. (github.com)](https://github.com/doccano/doccano)
* 当前运行：
  * 地址：http://39.108.124.18/
  * 后台：http://39.108.124.18/admin



# 2. 功能

1. （超级用户）创建项目
2. 分配项目成员及其角色
3. 导入数据
   * 具有TXT，JSON，CONLL三种导入选项
   * **TXT默认使用换行符分割数据条目（因此存在空行会导致导入失败），可在/backend/api/utils.py 261行处设置分割符**
4. 设置标签（名称、颜色、快捷键）。标签支持导入导出
5. 标注
   * 标注功能：选中文本后选择弹出框条目或按下快捷键进行标注
   * 连线功能：
     * 连线：从实体拖拽出连线到另一实体（不允许：重复连线，反向连线，自连线）
     * 设置关系：单击连线，从弹出框选择关系（第一个选项为空关系）
     * 删除连线：双击连线
     * 显示/隐藏连线：单击实体右上角按钮，在只显示该实体相关连线和显示全部连线切换。若处于只显示实体1的状态，单击实体2的按钮，则只显示实体2的连线（该状态会延续到其他数据条目，即在数据1只显示实体1，切换到数据2时，将无连线显示）
     * **默认具有['', 'attrOf', 'valueOf']三种关系，可在/frontend/components/organisms/annotation/EntityItemBox.vue 150行处设置关系列表**
6. 指南与统计
7. 导出数据
   * 具有两种JSON导出格式，推荐使用第一种：

```json
{
	"id": 1, 
	"text": "小儿3岁，一直有点流清鼻涕。偶尔有点咳嗽。有没有发现您的孩子有过敏的症状?发现了,孩子确实有过过敏孩子现在打喷嚏吗?孩子现在没有打喷嚏您的孩子有可能得了过敏性鼻炎,建议去医院进一步确认病情.", 
	"annotations": [
			{"id": 1, "label": "1", "start_offset": 5, "end_offset": 8, "user": "admin"}, 
			{"id": 2, "label": "1", "start_offset": 23, "end_offset": 27, "user": "admin"}, 
			{"id": 3, "label": "3", "start_offset": 39, "end_offset": 44, "user": "admin"}, 
			{"id": 5, "label": "2", "start_offset": 54, "end_offset": 59, "user": "admin"},
			{"id": 19, "label": "3", "start_offset": 70, "end_offset": 75, "user": "lqy"}
	], 
	"connections": [
			{"source": 1, "to": 5, "relation": "attrOf"}, 
			{"source": 5, "to": 2, "relation": "attrOf"}, 
			{"source": 2, "to": 3, "relation": "attrOf"}
	], 
	"annotation_approver": null
}
```



# 3. 运行

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
	# 发布模式
npm run build
npm run start
```

## 3.3 后端

```bash
# 后端django
cd backend

# 安装依赖
# 若出现安装psycopg2报错，可先apt install postgresql
pip install -r requirments.txt

# 数据库迁移
# 可先删除db.sqlite3文件
python3 manage.py makemigrations
python3 manage.py migrate
# 创建角色
python3 manage.py create_roles
# 创建初始超级用户
python3 manage.py create_admin

# 运行
python3 manage.py runserver 0.0.0.0:8000
	# or
gunicorn -b 0.0.0.0:8000 -w 4 backend.wsgi -t 300

# 运行地址 127.0.0.1:3000
# 后台地址 127.0.0.1:8000/admin
```

## 3.4 nginx

```bash
# 若非运行在本地，使用nginx代理
# 修改nginx/sl.nginx.conf下，第3行server_name和第54行/backend/static对应的文件路径
cp nginx/sl.nginx.conf /etc/nginx/conf.d/
# 重启nginx
nginx -s reload
nginx -t
```

## 3.5 Docker启动（未更新）

```bash
# 修改脚本权限（可能需要）
sudo chmod 777 frontend/dev-nuxt.sh
sudo chmod 777 backend/django.sh

# 启动
docker-compose up
```

