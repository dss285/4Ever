#!/usr/bin/python
import discord
class UpdatedMessage:
    def __init__(self, message, message_type):
        self.message = message
        self.message_type = message_type
    def refresh(self,):
        raise NotImplementedError
