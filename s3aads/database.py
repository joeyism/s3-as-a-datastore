from s3aads import Table
from s3aads.resources import s3_resource, s3_client

class Database(object):

  def __init__(self, name):
    self.name = name
    self.bucket = s3_resource.Bucket(self.name)

  @property
  def tables(self) -> list:
    result = s3_client.list_objects(Bucket=self.name, Delimiter="/")
    prefixes = result.get('CommonPrefixes')
    if prefixes is None:
      return []
    return [prefix['Prefix'][:-1] for prefix in prefixes]

  def create(self):
    if self.name in DataBase.list_databases():
      return
    return s3_client.create_bucket(Bucket=self.name)

  def get_table(self, table_name) -> Table:
    if table_name in self.tables:
      return Table(table_name, database=self)

  def drop_table(self, table_name):
    self.bucket.objects.filter(Prefix=f"{table_name}/").delete()

  @classmethod
  def list_databases(cls) -> list:
    response = s3_client.list_buckets()
    return [bucket['Name'] for bucket in response['Buckets']]

