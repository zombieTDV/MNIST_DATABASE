import yaml

class Settings:
    def __init__(self, path: str = "config/config.yaml"):
        self.path = path
        with open(self.path, "r") as file:
            self.cfg = yaml.safe_load(file)
            
            #Database settings
            self.server = self.cfg["database_info"]["SERVER"]
            self.database = self.cfg["database_info"]["DATABASE"]
            self.username = self.cfg["database_info"]["USERNAME"]
            self.password = self.cfg["database_info"]["PASSWORD"]
            self.driver = self.cfg["database_info"]["DRIVER"]
            
    def save(self) -> None:
        with open(self.path, "w") as file:
            yaml.safe_dump(self.cfg, file, sort_keys=False)
        

settings = Settings()