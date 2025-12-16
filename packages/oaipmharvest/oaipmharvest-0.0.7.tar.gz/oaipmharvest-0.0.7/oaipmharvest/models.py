from peewee import *

database = SqliteDatabase(None)


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseModel(Model):
    class Meta:
        database = database


class HarvestRun(BaseModel):
    config_file_checksum = TextField(null=True)
    config_file_path = TextField(null=True)
    endpoint_url = TextField(null=True)
    metadata_prefixes = TextField(null=True)
    sets = TextField(null=True)
    timestamp = TextField(null=True)

    class Meta:
        table_name = "harvest_run"


class ResumptionToken(BaseModel):
    harvest_run = ForeignKeyField(
        column_name="harvest_run_id", field="id", model=HarvestRun, null=True
    )
    metadata_prefix = TextField(null=True)
    resumption_token = TextField(null=True)
    set = TextField(null=True)
    state = TextField(null=True)
    timestamp = TextField(null=True)

    class Meta:
        table_name = "resumption_token"
