import os
from datetime import datetime


class Logger:
    def __init__(self, module_name: str, Write_on_it: bool = False):
        """_summary_

        Args:
            module_name (str): log category and file name
            Write_on_it (bool, optional): An option to delete and overwrite the file, or to continue writing without deleting. Defaults to False.
        """
        self.module_name = module_name
        os.makedirs("logs", exist_ok=True)
        if Write_on_it:
            with open(f"logs/{self.module_name}.log", "w", encoding="utf-8") as file:
                file.write("")
        else:
            with open(f"logs/{self.module_name}.log", "a", encoding="utf-8") as file:
                file.write("")

    def log(self, level_name: str, message: str):
        with open(f"logs/{self.module_name}.log", "a", encoding="utf-8") as file:
            now: datetime = datetime.now()
            log: str = (
                f"[{now.strftime('%Y-%m-%d')}] [{now.strftime('%H:%M:%S')}] [{level_name}] [{self.module_name}]: {message}\n"
            )
            file.write(log)
            print(log.removesuffix("\n"))

    def INFO(self, message: str):
        self.log("INFO", message)

    def WARNING(self, message: str):
        self.log("WARNING", message)

    def ERROR(self, message: str):
        self.log("ERROR", message)

    def CRITICAL(self, message: str):
        self.log("CRITICAL", message)
