from collections import defaultdict

from FoxDot.lib import Clock

__all__ = ['m']


class M:
    """
    "Alias" to `Master()`.

    Inspired by the `masterAll()` duo Crash Server function.

    Example:
        >>> m.oct = 5           # set value
        >>> ~m.oct              # reset value
        >>> ~m                  # reset all values
        >>> m.every(2, 'jump')  # create event
        >>> m.never('jump')     # cancel event
    """

    _values = defaultdict(dict)

    class MCallable:
        def __init__(self, attr):
            self.attr = attr

        def __call__(self, *args, **kwargs):
            for player in Clock.playing:
                getattr(player, self.attr)(*args, **kwargs)

    class MAttr:
        def __init__(self, attr, values):
            self.attr = attr
            self._values = values

        def __invert__(self):
            for player in Clock.playing:
                if self.attr not in self._values[player.id]:
                    continue
                setattr(player, self.attr, self._values[player.id][self.attr])
                del self._values[player.id][self.attr]

    def __invert__(self):
        for player in Clock.playing:
            for name, value in self._values[player.id].items():
                setattr(player, name, value)
            del self._values[player.id]

    def __setattr__(self, name, value):
        for player in Clock.playing:
            if name in self._values[player.id]:
                setattr(player, name, value)
                continue

            try:
                self._values[player.id][name] = player[name]
            except:
                self._values[player.id][name] = 0
            setattr(player, name, value)

    def __getattr__(self, name):
        for player in Clock.playing:
            if callable(attr := getattr(player, name)):
                return self.MCallable(name)
            else:
                break
        return self.MAttr(name, self._values)


m = M()
