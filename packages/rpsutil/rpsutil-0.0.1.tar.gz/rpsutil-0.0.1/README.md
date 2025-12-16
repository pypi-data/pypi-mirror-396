# Intro

This is an experimental package to expose [sysinfo](https://github.com/GuillaumeGomez/sysinfo) functionality in psutil compatible manner

## How to test

create venv and install [maturin](https://github.com/PyO3/maturin)

```
maturin develop
python3
from rsutil import Process
p = Process()
p.kill()
```
