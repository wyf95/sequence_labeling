原作者：https://github.com/doccano

# 1. Functions

用户角色说明：

- 分为超级用户和普通用户
- 超级用户是命令行创建的用户，可进入后台
- 所有用户可被分配管理员/标注员/审查员三种角色
- 初始超级用户账号：name: admin / password: root

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

当前运行地址：http://121.196.41.4/

后台运行地址：http://121.196.41.4/admin

# 2. Problems

- 刷新加载很慢
  - 原因：服务器性能较差或未将前端打包为静态资源
  - 前端nuxt打包缺失static文件夹，还需添加动态路由
- 导入数据需要utf-8格式，且不能有空行
- 指南使用tui-editor模板，如果输入太快，光标会自动移动到末尾
  - 原因：每个字符的改变都会触发上传
  - 可添加保存按钮，点击保存才上传
- 假设admin为超级用户，为其在project1设置某角色再删除该设置，admin将失去对该项目的控制权
- 只测试了两个浏览器的并发，若label条目被其他用户增/删，需要重新进入“数据”列表或刷新页面以重新显示
- 同一浏览器两个标签页可以登录不同账号，但是刷新后都会变成最后登录账号
  - 原因：使用LocalStorage，同时只能保存一个账号信息

# 3. Run

* Docker加速

```shell
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://13c21w00.mirror.aliyuncs.com"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

* Run

```shell
docker-compose up
```

* nginx（可选）

```shell
# 先修改nginx/sl.nginx.conf下server_name和static对应的文件路径
cp nginx/sl.nginx.conf /etc/nginx/conf.d/
nginx -s reload
nginx -t
```

