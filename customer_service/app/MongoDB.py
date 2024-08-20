import motor.motor_asyncio
import os


conn_str = os.getenv('conn_str')

class MongoDB:
    def __init__(self, conn_str, list):
        self.__client = motor.motor_asyncio.AsyncIOMotorClient(
            conn_str, serverSelectionTimeoutMS=5000
        )
        self.collections = {}
        self.addCollection(list)

    def addCollection(self, list):
        for collection in list:
            self.collections[collection[1]] = self.__client[collection[0]][collection[1]]

mongodb = MongoDB(conn_str, [["Tesodev", "customers"]])
