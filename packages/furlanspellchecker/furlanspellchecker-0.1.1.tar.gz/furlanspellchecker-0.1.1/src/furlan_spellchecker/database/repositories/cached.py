"""LRU cache decorator for repositories."""

from collections import OrderedDict
from typing import Any, Generic, TypeVar

from .base import (
    BaseRepository,
    IElisionRepository,
    IErrorRepository,
    IFrequencyRepository,
    IPhoneticRepository,
)

T = TypeVar("T")


class LRUCache(Generic[T]):
    """Simple LRU cache with O(1) access and eviction."""

    def __init__(self, maxsize: int = 10000):
        self.maxsize = maxsize
        self._cache: OrderedDict[str, T] = OrderedDict()

    def get(self, key: str) -> T | None:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, value: T) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key] = value
        else:
            if len(self._cache) >= self.maxsize:
                self._cache.popitem(last=False)
            self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        return key in self._cache


class CachedRepository(BaseRepository):
    """Generic cached repository decorator."""

    _NOT_FOUND = object()  # Sentinel for caching misses

    def __init__(
        self,
        inner: BaseRepository,
        cache_size: int = 10000,
        cache_misses: bool = True,
    ):
        self._inner = inner
        self._cache: LRUCache[Any] = LRUCache(cache_size)
        self._cache_misses = cache_misses
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> str | None:
        cached = self._cache.get(key)
        if cached is not None:
            self._hits += 1
            return None if cached is self._NOT_FOUND else cached

        value = self._inner.get(key)
        self._misses += 1

        if value is not None:
            self._cache.put(key, value)
        elif self._cache_misses:
            self._cache.put(key, self._NOT_FOUND)

        return value

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def close(self) -> None:
        self._cache.clear()
        self._inner.close()

    @property
    def stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0.0,
            "cache_size": len(self._cache),
        }


class CachedPhoneticRepository(CachedRepository, IPhoneticRepository):
    """Cached phonetic repository."""

    def __init__(self, inner: IPhoneticRepository, cache_size: int = 50000):
        super().__init__(inner, cache_size)
        self._inner: IPhoneticRepository = inner

    def get_words_list(self, phonetic_hash: str) -> list[str]:
        result = self.get(phonetic_hash)
        return result.split(",") if result else []

    def get_batch(self, phonetic_hashes: list[str]) -> dict[str, str]:
        """Batch lookup with cache-aware aggregation."""
        if not phonetic_hashes:
            return {}

        result: dict[str, str] = {}
        uncached: list[str] = []

        for phon_hash in phonetic_hashes:
            cached = self._cache.get(phon_hash)
            if cached is not None:
                self._hits += 1
                if cached is not self._NOT_FOUND:
                    result[phon_hash] = cached
            else:
                uncached.append(phon_hash)

        if uncached:
            self._misses += len(uncached)
            batch_result = self._inner.get_batch(uncached)

            for phon_hash in uncached:
                if phon_hash in batch_result:
                    value = batch_result[phon_hash]
                    self._cache.put(phon_hash, value)
                    result[phon_hash] = value
                elif self._cache_misses:
                    self._cache.put(phon_hash, self._NOT_FOUND)

        return result

    # Alias methods for IPhoneticDatabase interface compatibility
    def find_by_phonetic_hash(self, phonetic_hash: str) -> str | None:
        """Alias for get() - IPhoneticDatabase compatibility."""
        return self.get(phonetic_hash)

    def get_words_by_phonetic_hash(self, phonetic_hash: str) -> list[str]:
        """Alias for get_words_list() - IPhoneticDatabase compatibility."""
        return self.get_words_list(phonetic_hash)

    def has_phonetic_hash(self, phonetic_hash: str) -> bool:
        """Alias for has() - IPhoneticDatabase compatibility."""
        return self.has(phonetic_hash)


class CachedFrequencyRepository(CachedRepository, IFrequencyRepository):
    """Cached frequency repository."""

    def __init__(self, inner: IFrequencyRepository, cache_size: int = 20000):
        super().__init__(inner, cache_size)
        self._inner: IFrequencyRepository = inner

    def get_frequency(self, word: str) -> int:
        result = self.get(word)
        return int(result) if result else 0

    def rank_suggestions(self, suggestions: list[str]) -> list[tuple[str, int]]:
        """Rank suggestions using cached frequency lookups where available."""
        ranked = []
        for suggestion in suggestions:
            ranked.append((suggestion, self.get_frequency(suggestion)))

        ranked.sort(key=lambda item: (-item[1], item[0]))
        return ranked

    # Alias methods for IFrequencyDatabase interface compatibility
    def has_word(self, word: str) -> bool:
        """Alias for has() - IFrequencyDatabase compatibility."""
        return self.has(word)


class CachedErrorRepository(CachedRepository, IErrorRepository):
    """Cached error repository."""

    def __init__(self, inner: IErrorRepository, cache_size: int = 1000):
        super().__init__(inner, cache_size)
        self._inner: IErrorRepository = inner

    def get_correction(self, error_word: str) -> str | None:
        return self.get(error_word)

    # Alias methods for IErrorDatabase interface compatibility
    def has_error(self, error_word: str) -> bool:
        """Alias for has() - IErrorDatabase compatibility."""
        return self.has(error_word)


class CachedElisionRepository(CachedRepository, IElisionRepository):
    """Cached elision repository."""

    def __init__(self, inner: IElisionRepository, cache_size: int = 5000):
        super().__init__(inner, cache_size)
        self._inner: IElisionRepository = inner

    def has_elision(self, word: str) -> bool:
        return self.get(word) is not None
