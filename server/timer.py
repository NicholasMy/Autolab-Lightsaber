from datetime import datetime


class Timer:
    def __init__(self, duration: float):
        self.duration = duration
        self.start_time = datetime.now()

    def set_duration(self, duration: float):
        self.duration = duration

    def reset(self):
        self.start_time = datetime.now()

    def is_done(self) -> bool:
        return (datetime.now() - self.start_time).total_seconds() >= self.duration
