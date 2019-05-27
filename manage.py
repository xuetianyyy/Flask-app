from ihome import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


# 需要传递一个工作环境的参数
app = create_app('develop')
manager = Manager(app)

# 创建Migrate执行对象
Migrate(app=app, db=db)
# 添加迁移的脚本命令
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    # print(app.url_map)
    manager.run()
