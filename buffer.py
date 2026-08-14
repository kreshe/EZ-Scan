from collections import deque


class QRBuffer:

    def __init__(self, max_size=24):

        self.max_size = max_size
        self.buffer = deque()



    def add(self, code):

        if code in self.buffer:
            return False

        if len(self.buffer) >= self.max_size:
            return False

        self.buffer.append(code)

        return True



    def get(self):

        if self.buffer:
            return self.buffer.popleft()

        return None



    def clear(self):

        self.buffer.clear()



    def count(self):

        return len(self.buffer)



    def all(self):

        return list(self.buffer)



    #
    # удалить QR по индексу
    #
    def remove(self, index):

        if index < 0:
            return False

        if index >= len(self.buffer):
            return False


        items = list(self.buffer)

        items.pop(index)

        self.buffer = deque(items)

        return True



    #
    # удалить конкретный QR
    #
    def remove_code(self, code):

        try:

            self.buffer.remove(code)

            return True

        except ValueError:

            return False



    #
    # поменять порядок
    #
    def move(self, old_index, new_index):

        items = list(self.buffer)


        if (
            old_index < 0
            or old_index >= len(items)
        ):
            return False


        item = items.pop(old_index)


        items.insert(
            new_index,
            item
        )


        self.buffer = deque(items)

        return True