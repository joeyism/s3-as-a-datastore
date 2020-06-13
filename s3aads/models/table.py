from typing import Dict, List, Tuple
import random
import os
import io
from s3aads.resources import s3_resource, s3_client

class Table(object):

  def __init__(self, name, database, columns=[]):
    self.name = name
    if isinstance(database, str):
      from s3aads import Database
      self.database = Database(database)
    else:
      self.database = database
    self.columns = columns

  @property
  def keys(self) -> list:
    return self.query_by_key("")

  def query_by_key(self, key="") -> List[str]:
    result = s3_client.list_objects_v2(Bucket=self.database.name, Prefix=os.path.join(self.name, key))
    contents = result.get("Contents")
    return [content['Key'][len(self.name)+1:] for content in contents if content.get('Key')]

  def select_by_key(self, key) -> bytes:
    stringio = io.BytesIO()
    obj = self.database.bucket.Object(os.path.join(self.name, key))
    obj.download_fileobj(stringio)
    return stringio.getvalue()

  def insert_by_key(self, key, data):
    obj = self.database.bucket.Object(os.path.join(self.name, key))
    return obj.put( 
      Body=data
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

  def insert(self, **kwargs):
    if not self.columns:
      raise Exception("Columns not set. Please set columns before using this method")
    if kwargs.get("data") is None:
      raise Exception("data not found. You must include something to insert")

    data = kwargs.pop("data")
    if not isinstance(data, bytes):
      raise Exception("data must be bytes")

    column_placeholder = self.__form_column_placeholder__()
    key = column_placeholder.format(**kwargs)
    return self.insert_by_key(key, data)

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
      key_list.append(kwargs[column])

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
