
S3 As A Datastore (S3aaDS)
==========================

S3-as-a-datastore is a library that lives on top of botocore and boto3, as a way to use S3 as a key-value datastore instead of a real datastore

**DISCLAIMER**\ : This is NOT a real datastore, only the illusion of one. If you have remotely high I/O, this is NOT the library for you.

Motivation
----------

S3 is really inexpensive compared to Memcache, or RDS.

For example, this is the RDS cost

.. image:: https://raw.githubusercontent.com/joeyism/s3-as-a-datastore/master/doc/rds-cost.png
   :target: https://raw.githubusercontent.com/joeyism/s3-as-a-datastore/master/doc/rds-cost.png
   :alt: rds-cost


while this is S3 cost


.. image:: https://raw.githubusercontent.com/joeyism/s3-as-a-datastore/master/doc/s3-cost.png
   :target: https://raw.githubusercontent.com/joeyism/s3-as-a-datastore/master/doc/s3-cost.png
   :alt: s3-cost


If a service doesn't have a lot of traffic, keeping up a RDS deployment is wasteful because it stands idle but incurring cost. S3 doesn't have that problem. For services that has low read/writes operations, or only has CRD without the U (if you don't know what that means, read `CRUD <https://en.wikipedia.org/wiki/Create,_read,_update_and_delete>`_\ ), saving things in S3 gets similar results. As long as data isn't getting upgrade, only written and read, S3 can be used. However, Writing to S3 requires a lot of documentation reading if you're not used to it. This library is an interface to communication with S3 like a very pseudo-ORM way.

Installation
------------

.. code-block:: bash

   pip3 install s3aads

Idea
----

The main idea is a database is mapped to a bucket, and a table is the top level "folder" of s3. The rest of nested "folders" are columns. Because the way buckets work in S3, they must be unique for all S3 buckets. This also mean the combination of keys must be unique

NOTE: There are quotations around "folder" because files in a S3 bucket are flat, and there aren't really folders.

Example
^^^^^^^

.. code-block::

   Database: joeyism-test
   Table: daily-data

   id | year | month | day | data
   ------------------------------
    1 | 2020 |    01 |  01 | ["a", "b"]
    2 | 2020 |    01 |  01 | ["c", "d"]
    3 | 2020 |    01 |  01 | ["abk20dj3i"]

is mapped to

.. code-block::

   joeyism-test/daily-data/1/2020/01/01  ->  ["a", "b"]
   joeyism-test/daily-data/2/2020/01/01  ->  ["c", "d"]
   joeyism-test/daily-data/3/2020/01/01  ->  ["abk20dj3i"]

but it can be called with

.. code-block:: python3

   from s3aads import Table
   table = Table(name="daily-data", database="joeyism-test", columns=["id", "year", "month", "day"])
   table.select(id=1, year=2020, month="01", day="01") # b'["a", "b"]'
   table.select(id=2, year=2020, month="01", day="01") # b'["c", "d"]'
   table.select(id=3, year=2020, month="01", day="01") # b'["abk20dj3i"]'

Usage
-----

Example
^^^^^^^

.. code-block:: python3

   from s3aads import Database, Table
   db = Database("joeyism-test")
   db.create()

   table = Table(name="daily-data", database=db, columns=["id", "year", "month", "day"])
   table.insert(id=1, year=2020, month="01", day="01", data=b'["a", "b"]')
   table.insert(id=2, year=2020, month="01", day="01", data=b'["c", "d"]')
   table.insert(id=2, year=2020, month="01", day="01", data=b'["abk20dj3i"]')

   table.select(id=1, year=2020, month="01", day="01") # b'["a", "b"]'
   table.select(id=2, year=2020, month="01", day="01") # b'["c", "d"]'
   table.select(id=3, year=2020, month="01", day="01") # b'["abk20dj3i"]'

   table.delete(id=1, year=2020, month="01", day="01")
   table.delete(id=2, year=2020, month="01", day="01")
   table.delete(id=3, year=2020, month="01", day="01")

API
---

Database
^^^^^^^^

.. code-block:: python

   Database(name)


* *name*\ : name of the table

Properties
~~~~~~~~~~

``tables``\ : list of tables for that Database (S3 Bucket)

Methods
~~~~~~~

``create()``\ : Create the database (S3 Bucket) if it doesn't exist

``get_table(table_name) -> Table``\ : Pass in a table name and returns the Table object

``drop_table(table_name)``\ : Fully drops table

Class methods
~~~~~~~~~~~~~

``list_databases()``\ : List all available databases (S3 Buckets)

Table
^^^^^

.. code-block:: python

   Table(name, database, columns=[])


* *name*\ : name of the table
* *database*\ : Database object. If a string is passed instead, it'll attempt to fetch the Database object
* *columns (default: [])*\ : Table columns

Properties
~~~~~~~~~~

``keys``\ : list of all keys in that table. Essentially, list the name of all files in the folder

Full Param Methods
~~~~~~~~~~~~~~~~~~

The following methods require all the params to be passed in order for it to work.

``delete(**kwargs)``\ : If you pass the params, it'll delete that row of data

``insert(data:bytes, **kwargs)``\ : If you pass the params and value for ``data``\ , it'll insert that row of bytes data

``insert_string(data:string, **kwargs)``\ : If you pass the params and value for ``data``\ , it'll insert that row of string data

``select(**kwargs) -> bytes``\ : If you pass the params, it'll select that row of data and return the value as bytes

``select_string(**kwargs) -> string``\ : If you pass the params, it'll select that row of data and return the value as a string

Partial Param Methods
~~~~~~~~~~~~~~~~~~~~~

The following methods can work with partial params passed in.

``query(**kwargs) -> List[Dict[str, str]]``\ : If you pass the params, it'll return a list of params that is availabe in the table

Key Methods
~~~~~~~~~~~

``delete_by_key(key)``\ : If you pass the full key/path of the file, it'll delete that row/file

``insert_by_key(key, data: bytes)``\ : If you pass the full key/path of the file and the data (in bytes), it'll insert that row/file with the data

``select_by_key(key) -> bytes``\ : If you pass the full key/path of the file, it'll select that row/file and return the data

``query_by_key(key="", sort_by=None) -> List[str]``\ : If you pass the full or partial key/path of the file, it'll return a list of keys that matches the pattern


* ``sort_by``\ : Possible values are *Key*\ , *LastModified*\ , *ETag*\ , *Size*\ , *StorageClass*

Methods
~~~~~~~

``distinct(columns: List[str]) -> List[Tuple]``\ : If you pass a list of columns, it'll return a list of distinct tuple combinations based on those columns

``random_key() -> str``\ : Returns a random key to data

``random() -> Dict``\ : Returns a set of params and ``data`` of a random data

``count() -> int``\ : Returns the number of objects in the table

``<first_column_name>s() -> List``\ : Taking the name of the first column, returns a list of unique values.

``<n_column_name>s() -> List``\ : Taking the name of the Nth column, returns a list of unique values.


* For example, a table with columns ``["id", "name"]`` will have the method ``table.ids()`` which will return a list of unique ids
