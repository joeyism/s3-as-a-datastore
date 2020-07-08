import os

class Copy(object):

  def __init__(self, table, key):
    self.source_table = table
    self.source_key = key

  def to(self, dest_table, dest_key, **kwargs) -> None:
    copy_source = {
      'Bucket': self.source_table.database.name,
      'Key': os.path.join(self.source_table.name, self.source_key)
    }
    self.source_table.database.bucket.meta.client.copy_object(
      CopySource=copy_source,
      Bucket=dest_table.database.bucket.name,
      Key=os.path.join(dest_table.name, dest_key),
      **kwargs
    )
