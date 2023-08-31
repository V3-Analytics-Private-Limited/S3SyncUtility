import logging

class Logger:
    
    _instance = None
    def __new__(cls):
        """The __new__() method is typically used when you need to customize the creation of a new instance 
        of a class. For example, you might want to create a new instance of a class only if a certain condition 
        is met, or you might want to return an existing instance of the class if it has already been created"""
        
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            """The logging.getLogger() method is typically used to create a logger object 
            in each module that uses logging"""

            cls.logger = logging.getLogger(__name__)
            """The __name__ parameter in the getLogger() method is a special variable in Python 
            that represents the name of the current module. """

            cls.logger.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
            file_handler = logging.FileHandler('logs.log',mode="a")
            file_handler.setFormatter(formatter)
            cls.logger.addHandler(file_handler)

        return cls._instance

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)
    
    def critical(self,msg):
        self.logger.critical(msg)
        
logger = Logger()