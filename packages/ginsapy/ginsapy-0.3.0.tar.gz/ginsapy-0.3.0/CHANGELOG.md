# Ginsapy

## [0.3.0] - 2025-15-12

### Breaking Changes
* Refactored giutility class names to accurately represent their core functionality
* Implementations need to adapt to the new classnames of package giutility!
* Python version support below 3.10 are dropped since it is at end of live: https://devguide.python.org/versions

### Changed
- Switched to pyproject.toml for better metadata handling. Installation still works with `pip install .`
- Restructured the project to include all src files. examples are now under `src/ginsapy/examples`

### Fixed

- Fixed parsing issue in the read_dat_files.py example
- Fixed issue with authentication in example_websocket_stream.py
- Fixed issue and required params with create_udbf_buffer_ example