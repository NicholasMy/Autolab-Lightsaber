class InfiniteQueue:
    def __init__(self, queue=None):
        self.queue = queue or []
        self.index = 0

    def append(self, item):
        self.queue.append(item)

    def peek(self):
        return self.queue[self.index]

    def next(self):
        if self.index >= len(self.queue):
            self.index = 0
        item = self.queue[self.index]
        self.index += 1
        return item
