from peewee import Model, MySQLDatabase
from config.database import MYSQL_CONFIG

# 创建数据库连接
db = MySQLDatabase(
    MYSQL_CONFIG['database'],
    **{k: v for k, v in MYSQL_CONFIG.items() if k != 'database'}
)

class BaseModel(Model):
    class Meta:
        database = db 