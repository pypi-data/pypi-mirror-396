import peewee as pw

db = pw.SqliteDatabase(None)  # start database later with parameter name


class BaseModel(pw.Model):
    class Meta:
        database = db
