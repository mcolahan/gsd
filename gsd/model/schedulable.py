from pydantic import BaseModel, Field
from enum import IntEnum
from datetime import datetime

class RepetitionTypes(IntEnum):
    NotRepeated = 0
    Annually = 1
    Quarterly = 2
    Monthly = 3
    Weekly = 4
    Daily = 5

class ScheduledEvent(BaseModel):
    start_time: str = None
    end_time: str = None

    # repetition
    repetition_type: int = 0
    repetition_start: str = None
    repetition_end: str = None

    _scheduler: None

    @property
    def start_time_dt(self) -> datetime:
        return datetime.fromisoformat(self.start_time)
    
    @property
    def end_time_dt(self) -> datetime:
        return datetime.fromisoformat(self.end_time)
    
    @staticmethod
    def _get_current_time() -> str:
        return datetime.now().isoformat()

    @staticmethod
    def _parse_time(time: str) -> datetime:
        return datetime.fromisoformat(time)
    
    @staticmethod
    def current_timezone():
        return datetime.now().astimezone().tzinfo
    
    
    def is_within(self, from_time: datetime, to_time: datetime) -> bool:
        if self.start_time_dt >= from_time and self.start_time_dt <= to_time:
            return True
        if self.end_time_dt >= from_time and self.end_time_dt <= to_time:
            return True
        if self.start_time_dt <= from_time and self.end_time_dt >= to_time:
            return True
        


    


class Schedulable(BaseModel):
    events: list[ScheduledEvent] = []

    

