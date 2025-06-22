# models.py
from uagents import Model

class Request(Model):
    query: str

class Message(Model):
    body: str

class MatchResult(Model):
    name: str
    address: str

class Proposal(Model):
    content: str
    round: int