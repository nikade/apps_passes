from datetime import datetime
from enum import Enum

Direction = Enum('Direction',['IN','OUT'])

class PassReportItem:
    def __init__(self, date: datetime, direction: Direction):
        self.date = date
        self.direction = direction


