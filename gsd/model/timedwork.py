from pydantic import BaseModel
from datetime import datetime, UTC, timedelta

class TimedWork(BaseModel):
    start_times: list[str] = []
    end_times: list[str] = []
    expected_time: float = 0

    @property
    def total_work_time(self):
        start_times = [self._parse_time(t) for t in self.start_times]
        end_times = [self._parse_time(t) for t in self.end_times]

        # print(start_times)
        # print(end_times)

        if self.is_work_ongoing:
            end_times.append(datetime.now(UTC))
        
        total_time = 0
        for i in range(len(start_times)):
            total_time += (end_times[i] - start_times[i]).total_seconds()
        
        return total_time / 3600
    
    
    def start_work(self):
        assert not self.is_work_ongoing, 'The work timer has already started!'
        self.start_times.append(self._get_current_time())

    @property
    def is_work_ongoing(self) -> bool:
        return len(self.start_times) > len(self.end_times)
    
    def end_work(self):
        if self.is_work_ongoing:
            self.end_times.append(self._get_current_time())
    
    @staticmethod
    def _get_current_time() -> str:
        return datetime.now().isoformat()

    @staticmethod
    def _parse_time(time: str) -> datetime:
        return datetime.fromisoformat(time)
    