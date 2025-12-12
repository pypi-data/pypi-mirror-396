# logsteplib

- [Description](#package-description)
- [Usage](#usage)
- [Installation](#installation)
- [Docstring](#docstring)
- [License](#license)

## Package Description

A library providing a standardised format for the logging module.

## Usage

### Stream Console Logs

From a script:

```python
# Initialise a logger for the process and log an informational message
from logsteplib.streamer import StreamLogger

logger = StreamLogger(name="my_process").logger

logger.info(msg="Something to log!")
# 2025-11-02 00:00:01 - my_process           - INFO     - Something to log!
```

## Installation

Install python and pip if you have not already.

Then run:

```bash
pip install pip --upgrade
```

For production:

```bash
pip install logsteplib
```

This will install the package and all of it's python dependencies.

If you want to install the project for development:

```bash
git clone https://github.com/aghuttun/logsteplib.git
cd logsteplib
pip install -e ".[dev]"
```

## Docstring

The script's docstrings follow the numpydoc style.

## License

BSD License (see license file)

[top](#logsteplib)
