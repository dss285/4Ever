#!/usr/bin/python
import discord
import asyncio
import database
class UpdatedMessage:
    def __init__(self, message, database, em):
        self.message = message
        self.database = database
        self.em = em
    def refresh(self,):
        pass

