# S3 As A Datastore
S3-as-a-datastore is a library that lives on top of botocore and boto3, as a way to use S3 as a key-value datastore instead of a real datastore

**DISCLAIMER**: This is NOT a real datastore, only the illusion of one. If you have remotely high I/O, this is NOT the library for you.

## Motivation
S3 is really inexpensive compared to Memcache, or RDS. For services that has low read/writes operations, or only has CRD without the U (if you don't know what that means, read [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete)), saving things in S3 gets similar results. However, writing to S3 requires a lot of documentation reading if you're not used to it. This library is an interface to communication with S3 like a very pseudo-ORM way.

## Installation
```bash
pip3 install s3aads
```

## Idea
The main idea is a database is mapped to a bucket, and a table is the top level "folder" of s3. The rest of nested "folders" are columns. Because the way buckets work in S3, they must be unique for all S3 buckets. This also mean the combination of keys must be unique

NOTE: There are quotations around "folder" because files in a S3 bucket are flat, and there aren't really folders.
### Example
```
Database: joeyism-test
Table: daily-data

id | year | month | day | data
------------------------------
 1 | 2020 |    01 |  01 | ["a", "b"]
 2 | 2020 |    01 |  01 | ["c", "d"]
 3 | 2020 |    01 |  01 | ["abk20dj3i"]
```
is mapped to
```
joeyism-test/daily-data/1/2020/01/01  ->  ["a", "b"]
joeyism-test/daily-data/2/2020/01/01  ->  ["c", "d"]
joeyism-test/daily-data/3/2020/01/01  ->  ["abk20dj3i"]
```

but it can be called with

```python3
from s3aads import Table
table = Table(name="daily-data", database="daily-data")
table.select(id=1, year=2020, month="01", day="01") // b'["a", "b"]'
table.select(id=2, year=2020, month="01", day="01") // b'["c", "d"]'
table.select(id=3, year=2020, month="01", day="01") // b'["abk20dj3i"]'
```

## Usage

### Example

```python3
from s3aads import Database, Table
db = Database("joeyism-test")
db.create()

table = Table(name="daily-data", database=db, columns=["id", "year", "month", "day"])
table.insert(id=1, year=2020, month="01", day="01", data=b'["a", "b"]')
table.insert(id=2, year=2020, month="01", day="01", data=b'["c", "d"]')
table.insert(id=2, year=2020, month="01", day="01", data=b'["abk20dj3i"]')

table.select(id=1, year=2020, month="01", day="01") // b'["a", "b"]'
table.select(id=2, year=2020, month="01", day="01") // b'["c", "d"]'
table.select(id=3, year=2020, month="01", day="01") // b'["abk20dj3i"]'

table.delete(id=1, year=2020, month="01", day="01")
table.delete(id=2, year=2020, month="01", day="01")
table.delete(id=3, year=2020, month="01", day="01")
```
