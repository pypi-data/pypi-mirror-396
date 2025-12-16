# datavlt

**datavlt** is a lightweight Python library for simple JSON-based data storage and management.
It allows you to create multiple independent JSON storage files, add, delete, check existence, and transfer data between them.

## Features

- Create multiple storage files in a dedicated folder
- Add, remove, and check for objects in storage
- Supports checking objects by unique key (`name` by default)
- Move objects from one storage to another
- Fully written in pure Python with no external dependencies
- Easy to use and integrate into existing projects

## Installation

```bash
pip install datavlt
```

## Usage
```python
from datavlt import DataBase

db = DataBase()
db1 = db.create_storage()
db.add(db1, {"name": "Alice", "age": 25})
print(db.get_all(db1))
```