import asyncio
import time
from typing import Optional, Any, overload, Callable

class TTLDict:
    def __init__(self, default_ttl: int = 60, cleanup_interval: int = 300, cleanup_callback: Optional[Callable] = None, loop: Optional[asyncio.AbstractEventLoop] = None):
        """
        :param default_ttl: TTL по умолчанию (сек), если при записи не указан
        :param cleanup_interval: периодическая очистка от просроченных ключей (сек),
                                 если -1 — очистка не запускается автоматически
        :param cleanup_callback: функция(key), вызывается при удалении просроченного ключа
        """
        self._store = {}
        self._default_ttl = default_ttl
        self._cleanup_interval = cleanup_interval
        self._cleanup_callback = cleanup_callback
        self._task = None
        self._loop = loop

    def set(self, key, value, ttl: Optional[int] = None):
        if ttl is None:
            ttl = self._default_ttl
        self._store[key] = (value, time.monotonic() + ttl)


        if self._task is None and self._cleanup_interval != -1:
            if self._loop is None:
                try:
                    self._loop = asyncio.get_running_loop()
                except RuntimeError:
                    return
            self._task = self._loop.create_task(self._cleanup_worker())


    def get(self, key, default=None):
        item = self._store.get(key)
        if not item:
            return default
        value, expire_at = item
        now = time.monotonic()
        if expire_at < now:
            self._delete_expired(key)
            return default
        return value

    def __setitem__(self, key, value):
        self.set(key, value, self._default_ttl)

    def __getitem__(self, key):
        val = self.get(key)
        if val is None:
            raise KeyError(key)
        return val

    def __contains__(self, key):
        item = self._store.get(key)
        if not item:
            return False
        _, exp = item
        if exp < time.monotonic():
            self._delete_expired(key)
            return False
        return True

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return f"<TTLDict size={len(self._store)}>"

    def __iter__(self):
        now = time.monotonic()
        for k, (_, exp) in list(self._store.items()):
            if exp < now:
                self._delete_expired(k)
            else:
                yield k

    def keys(self):
        return list(iter(self))

    def values(self):
        now = time.monotonic()
        return [v for k, (v, exp) in list(self._store.items()) if exp >= now]

    def items(self):
        now = time.monotonic()
        return [(k, v) for k, (v, exp) in list(self._store.items()) if exp >= now]

    def update(self, other):
        for k, v in other.items():
            self.set(k, v)

    def clear(self):
        self._store.clear()

    def setdefault(self, key, default=None, ttl: Optional[int] = None):
        val = self.get(key)
        if val is None:
            self.set(key, default, ttl)
            return default
        return val

    def copy(self):
        return dict(self.items())

    @overload
    def pop(self, key: Any, /) -> Any: ...
    @overload
    def pop(self, key: Any, default: Any, /) -> Any: ...

    def pop(self, key: Any, default: Any = None, /) -> Any:
        item = self._store.pop(key, None)
        if item is None:
            return default
        value, exp = item
        if exp < time.monotonic():
            if self._cleanup_callback:
                try:
                    self._cleanup_callback(key)
                except Exception:
                    pass
            return default
        return value

    def _delete_expired(self, key):
        """Внутренний метод удаления с вызовом callback"""
        self._store.pop(key, None)
        cb = self._cleanup_callback
        if cb:
            try:
                cb(key)
            except Exception:
                pass

    async def _cleanup_worker(self):
        """Фоновая очистка просроченных ключей"""
        while True:
            await asyncio.sleep(self._cleanup_interval)
            self.cleanup()

    def cleanup(self):
        """Удалить все просроченные ключи"""
        now = time.monotonic()
        expired = [k for k, (_, exp) in self._store.items() if exp < now]
        cb = self._cleanup_callback
        if cb:
            for k in expired:
                self._store.pop(k, None)
                try:
                    cb(k)
                except Exception:
                    pass
        else:
            for k in expired:
                self._store.pop(k, None)

    async def stop(self):
        """Остановить фон очистки"""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
