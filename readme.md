# 1. Functions

用户角色说明：

- 分为超级用户和普通用户
- 超级用户是命令行创建的用户，可进入后台
- 所有用户可被分配管理员/标注员/审查员三种角色

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

# 2. Problems

- guidline使用tui-editor模板，如果输入太快，光标会自动移动到末尾
  - 原因：每个字符的改变都会触发上传
  - 可设置保存按钮，点击保存才上传
- 假设admin为超级用户，为其在project1设置某角色再删除该设置，admin将失去对该项目的控制权
- 只测试了两个浏览器的并发，若label条目被其他用户增/删，需要重新进入“数据”列表或刷新页面以重新显示
- 同一浏览器两个标签页可以登录不同账号，但是刷新后都会变成最后登录账号
  - 原因：使用LocalStorage，同时只能保存一个账号信息

# 3. Run

* Clone

```shell
git clone git@gitee.com:HITSZ-CS/sequence-tagging-system.git

# windows
git clone git@gitee.com:HITSZ-CS/sequence-tagging-system.git --config core.autocrlf=input
```

* 前后端分别启动

```shell
# 前端nuxt，node版本10.19，太新会出现依赖报错

# 安装node与npm，切换node版本
sudo apt install nodejs npm
sudo npm install n -g
sudo n 10.19

cd frontend

# 安装依赖
npm install --save nuxt

# 运行
	# 调试模式
npm run dev
	# 发布模式
npm run build
npm run start

# 后端django
cd ../backend

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
```

* Docker启动

```shell
# 修改脚本权限（可能需要）
sudo chmod 777 frontend/dev-nuxt.sh
sudo chmod 777 backend/django.sh

# 启动
docker-compose up

# 访问：127.0.0.1:3000
```

* nginx代理（可选）

```shell
# 修改nginx/sl.nginx.conf下，server_name和static对应的文件路径
cp nginx/sl.nginx.conf /etc/nginx/conf.d/
nginx -s reload
nginx -t
```
