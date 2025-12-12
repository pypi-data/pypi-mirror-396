# FoxDotM - "Alias" to `Master()` with the functionality to reset old values

> Inspired by the [`masterAll()`](https://crashserver.fr/blog/the-ultimate-crash-server-foxdot-python-custom-functions/#globalfunction) duo Crash Server function.

## Instalation

``` shell
pip install FoxDotM
# or
pip install git+https://codeberg.org/FoxDotExtensions/FoxDotM
```

## Usage

Import lib

``` python
from FoxDotM import m
```

Set value

``` python
m.oct = 5
```

Reset value

``` python
>>> ~m.oct
```

Reset all values

``` python
~m
```

Create event

``` python
m.every(2, 'jump')
```

Cancel event

``` python
m.never('jump')
```
