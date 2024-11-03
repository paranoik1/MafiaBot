from typing import Callable


class ExistsKey(Exception):
    message = "Ключ '{}' уже существует в репозитории"

    def __init__(self, key: str):
        super().__init__(self.message.format(key))


class Repository[T]:
    def __init__(self, store: dict[int, T] = None):
        self._store = store if store else dict()

    def __iter__(self):
        return iter(self._store.values())

    def __repr__(self):
        return str(self.to_list())

    def __len__(self):
        return len(self._store)

    def __getitem__(self, index: int):
        return self.to_list()[index]

    def __eq__(self, other: "Repository"):
        return self._store == other._store

    def to_list(self):
        return list(self._store.values())

    def add(self, id: int, obj: T):
        if id in self._store:
            raise ExistsKey(str(id))

        self.set(id, obj)

    def set(self, id: int, obj: T):
        self._store[id] = obj

    def get(self, id: int) -> T:
        return self._store.get(id)

    def remove(self, id: int):
        self._store.pop(id)

    def filter(self, func_filter: Callable[[T], bool]):
        new_repository = Repository[T]()
        for id, obj in self._store.items():
            if func_filter(obj):
                new_repository.add(id, obj)

        return new_repository
