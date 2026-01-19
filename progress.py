from tqdm import tqdm
from typing import Any, Generator, Iterable, List


class Progress:

    _bars: List[tqdm]
    _next_position: int
    
    progresses: List[int]
    totals: List[int]
    descs: List[str]
    error_messages: List[str]

    def __init__(self):
        self._bars = []
        self._next_position = 0
        self.progresses = []
        self.totals = []
        self.descs = []
        self.error_messages = []
    
    def start_process(self, total: int, desc: str):
        self._bars.append(
            tqdm(
                total=total, 
                position=self._next_position, 
                leave=True, 
                desc=desc
            )
        )
        self._next_position += 1
        self.progresses.append(0)
        self.totals.append(total)
        self.descs.append(desc)

    def update_process(self, increment: int = 1):
        self._bars[-1].update(increment)
        self.progresses[-1] += increment

    def end_process(self):
        self._bars[-1].close()
        self._bars.pop()
        self._next_position -= 1
        self.progresses.pop()
        self.totals.pop()
        self.descs.pop()

    def start_iteration(
        self, 
        iterable: Iterable, 
        total: int, 
        desc: str
    ) -> Generator[Any, None, None]:
        self.start_process(total, desc)
        for it in iterable:
            yield it
            self.update_process()
        self.end_process()

    def add_error_message(self, message: str):
        self.error_messages.append(message)
        