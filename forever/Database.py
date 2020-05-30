import re
import json
import discord
class Database:
    def __init__(self,):
        self.data_dir = "/home/dss/data"
        self.dictionary = {}
    
    def modifyDictionary(self, **kwargs):
        primarykey = None
        subkeys = None
        if "primaryKey" in kwargs.keys():
            primarykey = kwargs["primaryKey"]
        if "subKeys" in kwargs.keys():
            subkeys = kwargs["subkeys"]

        if primarykey in self.
    def load(self, ):
