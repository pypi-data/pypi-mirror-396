from pathlib import Path
import json
from .spec_methods import SpecMethods
from .config import fsm_def as settings
from .processor import Proocessor
from mfsapi import MainClient
from mfsapi import MainServer

storages = {}

folder_name = ".datavlt_storages"
folder = Path.home() / folder_name
folder.mkdir(exist_ok=True)

spec_methods = SpecMethods()
processor = Proocessor()

class DataBase:
    def create_storage(self):
        v1 = len(storages) + 1
        file_name = f"data_{v1}.json"
        file_path = folder / file_name

        if not file_path.exists():
            file_path.write_text("[]", encoding="utf-8")

        storages[file_name] = file_path
        return file_name

    def add(self, db_name, obj):
        if db_name not in storages:
            raise ValueError(f"Data base: {db_name} doesn't exist")
        file_path = storages[db_name]

        data = json.loads(file_path.read_text(encoding="utf-8"))
        data.append(obj)
        file_path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")

    def get_all(self, db_name):
        if db_name not in storages:
            raise ValueError(f"Data base: {db_name} doesn't exist")
        file_path = storages[db_name]
        return json.loads(file_path.read_text(encoding="utf-8"))
        
        # noinspection PyUnreachableCode
        def exists(self, db_name, objtocheck, c_settings=None):
            c_settings = c_settings or settings
            return spec_methods._fsm(db_name, objtocheck, storages, self, c_settings)
        if isinstance(objtocheck, dict) and "name" in objtocheck:
            for item in data:
                if isinstance(item, dict) and item.get("name") == objtocheck["name"]:
                    return True
            return False
        else:
            return objtocheck in data

    def delete(self, db_name, objtodel):
        if db_name not in storages:
            raise ValueError(f"Data base: {db_name} doesn't exist")
        file_path = storages[db_name]
        data = self.get_all(db_name)

        if isinstance(objtodel, dict) and "name" in objtodel:
            data = [item for item in data if not (isinstance(item, dict) and item.get("name") == objtodel["name"])]
        else:
            data = [item for item in data if item != objtodel]

        file_path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")

    def send(self, from_db_name, to_db_name, objecttosend):
        if not self.exists(from_db_name, objecttosend):
            raise ValueError(f"Object with name '{objecttosend.get('name', objecttosend)}' does not exist in {from_db_name}")
        processor._fpm(from_db_name, to_db_name, objecttosend, storages, self)