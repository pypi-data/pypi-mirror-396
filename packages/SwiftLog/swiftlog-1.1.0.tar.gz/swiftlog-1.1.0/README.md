
# SwiftLog

Lightweight, modular logger that can write to console and file.
## Features

- advanced timestamps
- classic error levels
- object-based
- customizable

## Installation

Install SwiftLog with pip

```bash
  pip install SwiftLog
```
    
## Usage/Examples

```python
from SwiftLog import Logger
logger = Logger(module_name = 'app')
logger.log(level_name = 'debug', message = 'app is starting...')
logger.INFO(message = 'app is started.')
```
```
[2025-12-09] [14:10:55] [debug] [app]: app is starting...
[2025-12-09] [14:10:55] [INFO] [app]: app is started.
```



## Authors

- [@adem-ocel](https://github.com/adem-ocel)

