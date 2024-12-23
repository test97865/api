from peewee import *
from database.base import BaseModel

class Assets(BaseModel):
    id = AutoField()
    identifier = CharField(max_length=255)
    url = CharField(max_length=255)
    timestamp = CharField(max_length=255)
    search_engine = CharField(max_length=255)
    query_statements = CharField(max_length=255)
    protocol = CharField(max_length=255, null=True)
    ip = CharField(max_length=255)
    port = IntegerField(null=True)
    domain = CharField(max_length=255, null=True)
    title = CharField(max_length=255, null=True)
    product = CharField(max_length=255, null=True)
    product_category = CharField(max_length=255, null=True)
    country = CharField(max_length=255, null=True)
    country_name = CharField(max_length=255, null=True)
    region = CharField(max_length=255, null=True)
    city = CharField(max_length=255, null=True)
    os = CharField(max_length=255, null=True)
    as_organization = CharField(max_length=255, null=True)
    lastupdatetime = CharField(max_length=255, null=True)
    icp = CharField(max_length=255, null=True)

    class Meta:
        indexes = (
            (('ip', 'port'), True),
        ) 