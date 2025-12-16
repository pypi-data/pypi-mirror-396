import json

class Proocessor():
	def _fpm(self, from_db_name, to_db_name, objecttosend, storages, mnclass):
		if from_db_name not in storages:
			raise ValueError(f"Data base: {from_db_name} doesn't exist")
		if to_db_name not in storages:
			raise ValueError(f"Data base: {to_db_name} doesn't exist")
		
		mnclass.add(to_db_name, objecttosend)
		mnclass.delete(from_db_name, objecttosend)