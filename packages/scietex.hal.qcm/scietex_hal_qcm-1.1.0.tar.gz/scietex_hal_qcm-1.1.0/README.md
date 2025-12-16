# scietex.hal.qcm

The `scietex.hal.qcm` package is a Python library for interfacing with Quartz Microbalance (QCM).
It provides an abstract base class (`QCM`), which in its turn inherits `scietex.hal.serial.RS485Client`.
The concrete implementations for two models of QCM manufactured by Scietex and CYKY are provided.

## Features
- Abstract base class (`VFD`) for consistent VFD implementations.
- Implemented VFD models:
  - `Scietex ftmONE`.
  - `CYKY TM106B`.

## Installation
Install the package via pip (assuming it’s published to PyPI):
```bash
pip install scietex.hal.qcm
```

Alternatively, clone the repository and install locally:
```bash
git clone https://github.com/bond-anton/scietex.hal.qcm.git
cd scietex.hal.qcm
pip install .
```

## Requirements

 - Python 3.9 or higher.
 - `scietex.hal.serial` (For RS485 communication support).

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m "Add your message"`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

Please include tests (if applicable) and follow PEP 8 style guidelines.

## License

This project is licensed under the **MIT License** - see the LICENSE file for details.
