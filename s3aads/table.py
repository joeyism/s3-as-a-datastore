from typing import Dict, List, Tuple
import random
import os
import io
from s3aads.resources import s3_resource, s3_client
from s3aads import Copy

class Table(object):

  def __init__(self, name, database, columns=[]):
    self.name = name
    if isinstance(database, str):
      from s3aads import Database
      self.database = Database(database)
    else:
      self.database = database
    self.columns = columns

    def column_generator(self, column_number):
      def get_values():
        keys = self.keys
        return list(set(key.split("/")[column_number] for key in keys))

      return get_values

    for i, col in enumerate(self.columns):
      setattr(self, f"{col}s", column_generator(self, i))

  @property
  def keys(self) -> list:
    return self.query_by_key("")

  def first_column_values(self):
    keys = self.keys
    return list(set(key.split("/")[0] for key in keys))

  def count(self) -> int:
    return len(self.keys)

  def select_all_by_filter(self, key=""):
    return [obj for obj in self.database.bucket.objects.filter(Prefix=os.path.join(self.name, key))]

  def query_by_key(self, key="", sort_by=None) -> List[str]:
    result = self.select_all_by_filter(key=key)
    contents = [obj.meta.data for obj in result]
    if contents is None:
      return []
    if sort_by:
      contents = sorted(contents, key=lambda k: k[sort_by])
    return [content['Key'][len(self.name)+1:] for content in contents if content.get('Key')]

  def select_by_key(self, key) -> bytes:
    if not self.query_by_key(key):
      return
    stringio = io.BytesIO()
    obj = self.database.bucket.Object(os.path.join(self.name, key))
    obj.download_fileobj(stringio)
    return stringio.getvalue()

  def insert_by_key(self, key, data, **kwargs):
    obj = self.database.bucket.Object(os.path.join(self.name, key))
    return obj.put( 
      Body=data,
      **kwargs
    )

  def delete_by_key(self, key):
    obj = self.database.bucket.Object(os.path.join(self.name, key))
    return obj.delete()

  def __form_column_placeholder__(self):
    return "/".join(["{" + column + "}" for column in self.columns])

  def select(self, **kwargs) -> bytes:
    if not self.columns:
      raise Exception("Columns not set. Please set columns before using this method")
    column_placeholder = self.__form_column_placeholder__()
    key = column_placeholder.format(**kwargs)
    return self.select_by_key(key)

  def select_string(self, **kwargs) -> str:
    data = self.select(**kwargs)
    if data:
      return data.decode("utf8")
    return

  def insert(self, **kwargs):
    if not self.columns:
      raise Exception("Columns not set. Please set columns before using this method")
    if kwargs.get("data") is None:
      raise Exception("data not found. You must include something to insert")

    data = kwargs.pop("data")
    if not isinstance(data, bytes):
      raise Exception("data must be bytes")

    column_placeholder = self.__form_column_placeholder__()
    metadata = kwargs.pop("metadata", {})
    key = column_placeholder.format(**kwargs)
    return self.insert_by_key(key, data, **metadata)

  def insert_string(self, **kwargs):
    if kwargs.get("data") is None:
      raise Exception("data not found. You must include something to insert")
    data = kwargs["data"]
    kwargs["data"] = data.encode("utf8")
    return self.insert(**kwargs)

  def delete(self, **kwargs):
    if not self.columns:
      raise Exception("Columns not set. Please set columns before using this method")
    column_placeholder = self.__form_column_placeholder__()
    key = column_placeholder.format(**kwargs)
    return self.delete_by_key(key)

  def query(self, **kwargs) -> List[Dict[str, str]]:
    key_list = []
    for column in self.columns:
      if kwargs.get(column) is None:
        break
      key_list.append(str(kwargs[column]))

    key = "/".join(key_list)
    filenames = self.query_by_key(key)
    results = []
    for filename in filenames:
      vals = filename.split("/")
      results.append(dict(zip(self.columns, vals)))
    return results

  def distinct(self, columns: List[str]) -> List[Tuple]:
    keys = self.query_by_key()
    return list(set(tuple(key.split("/")[:len(columns)]) for key in keys))

  def random_key(self) -> str:
    return random.choice(self.keys)

  def random(self) -> Dict:
    key = self.random_key()
    result = dict(zip(self.columns, key.split("/")))
    result["data"] = self.select_by_key(key)
    return result

  def copy(self, key) -> Copy:
    """
    Usage:
      copy(key).to(dest_table, dest_key)

    Example:
      from s3aads import Table

      table1 = Table("table1", database="db1", columns=["a"])
      table2 = Table("table2", database="db2", columns=["a"])
      table1.copy(key).to(table2, key)
    """

    return Copy(self, key)

