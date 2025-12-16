class SpecMethods:
    class SpecMethods:
        def _fsm(self, db_name, objtocheck, storages, mnclass, settings):
            if db_name not in storages:
                raise ValueError(f"Data base: {db_name} doesn't exist")
            
            mode = settings.get("search_by", "all") if isinstance(settings, dict) else settings
            
            data = mnclass.get_all(db_name)
            
            if mode == "all":
                return objtocheck in data
            
            if isinstance(mode, str):
                search_value = mode
                for item in data:
                    if isinstance(item, dict) and search_value in item.values():
                        return True
                return False
            
            return False