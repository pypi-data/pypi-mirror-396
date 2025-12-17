# Changelog

All notable changes to the ekfsm (EKF System Management Library) project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- SSM device class for managing system state transitions
- Open, close, and connected methods for various device classes
- ShellCheck integration for shell script linting
- Enhanced IO4Edge documentation with additional method descriptions

### Changed
- Consolidated ColorLED and LEDArray classes into a single module
- Renamed `set_fatal` method to `fatal` for consistency
- Changed logging level to DEBUG and increased loop iterations for testing
- Updated devenv.lock and devenv.nix for improved dependency management and CI integration
- Migrated to new hooks syntax in devenv

### Fixed
- Vulnerability in urllib fixed with dependency pinning to 2.6.0

### Removed
- Watchdog device and related references from the codebase

## [1.8.0] - 2025-11-25

### Changed
- Improved code readability by formatting long return statements and error messages

### Fixed
- Updated documentation and type hints across multiple files

## [1.7.0] - 2025-11-25

### Changed
- Updated documentation requirements

## [1.6.0] - 2025-11-20

### Added
- Enhanced IO4Edge client initialization with command timeout parameter
- Logging for device initialization and operations across multiple device classes

### Changed
- Updated io4edge_client dependency to version 2.0.3
- Updated Python version dependencies
- Increased timeout for read buttons operations
- Moved client context management into display_image method
- SMC slot coding changed to meet real system requirements

### Fixed
- Pixel display no autoconnect issue
- Various bug fixes (#45, #46)

## [1.5.1] - 2025-11-20

### Fixed
- Reverted problematic SAST security fixes that caused issues

## [1.5.0] - 2025-11-20

### Added
- Profiling scripts for ekfsm and io4edge_client modules
- NET1 configuration to CCTV YAML file
- EKF SHU-SHUTTLE and EKF Z1010 configurations to YAML files
- CCTV connection test script
- Bandit security linter configuration and CI integration
- Dependency scanning template in CI
- Security audit scans for vulnerabilities
- SAST scanning scripts in CI configuration

### Changed
- Updated io4edge_client dependency to version 2.1.0
- Replaced Button with BinaryToggle and GPIOArray in device configuration
- Enhanced LED control in CCTV profiling scripts
- Streamlined system initialization in CCTV profiling
- Added retry mechanism for all i4e functions on connection rejects
- Improved logging throughout the system

### Fixed
- Replaced assertions with proper error handling in device classes (#47)
- Updated .gitignore to ignore all Bandit report files
- Removed unused import of sleep in cctv-connecs.py
- Override dependencies to fix security vulnerabilities (#48)

### Security
- Added Bandit security scanning with JSON reports
- Enhanced artifact handling for security scans
- Integrated vulnerability scanning in CI pipeline

## [1.4.0] - 2025-11-15

### Added
- Logging for device initialization and operations across multiple device classes
- Timeout parameter for IO4Edge client initialization

### Changed
- Updated io4edge_client dependency to version 2.0.3
- Updated Python version dependencies
- Increased timeout for read button operations
- Moved client context management into display_image method
- SMC slot coding changed to real system requirements

### Fixed
- Pixel display autoconnect issues
- Various bug fixes (#45, #46)

## [1.3.0] - 2025-11-10

### Added
- PyPI.org deployment stage in CI
- UV publishing support
- Enhanced exception handling system
- Offset support for EEPROM attribute writes

### Changed
- Refactored EEPROM write method for improved error handling and readability
- Refactored EEPROM and utility functions for improved maintainability
- Simplified SMBIOS revision handling
- Simplified IIO calculation
- Enhanced exception system architecture

### Fixed
- Typing errors in various modules
- Unsupported seek operation during file open mechanism for EEPROM

## [1.2.0] - 2025-11-05

### Added
- `write_customer_area` method to EKF_CCU_EEPROM with validation and documentation
- Sphinx-click to documentation requirements
- Enhanced documentation for temperature, load_firmware, and load_parameterset methods

### Changed
- Reorganized utils and updated documentation in ekfsm.rst
- Enhanced boards and CCU documentation with additional examples
- Improved lock.py docstrings for better understanding of locking mechanism

### Fixed
- Corrected expected output in write_customer_area docstring for EKF_CCU_EEPROM
- Fixed error in pmbus psustatus example documentation

## [1.1.0] - 2025-11-01

### Added
- GitVersion.yml configuration
- CLI options documentation
- EKF boards documentation with product page links
- Documentation for ekfsm.core.slots module

### Changed
- Enhanced documentation and structure by improving module exports
- Reordered and enhanced docstring for System class
- Improved docstring formatting and consistency in SysFSAttribute class
- Updated docstring for CoreTemp class for enhanced clarity

### Fixed
- Issues #23 and #24
- Fixed eeprom `__all__` in documentation
- Enhanced generic device documentation

## [1.0.2] - 2025-10-28

### Fixed
- Minor bug fixes and improvements

## [1.0.0] - 2025-10-25

### Added
- Initial stable release of ekfsm
- Complete system management framework for CompactPCI Serial devices
- YAML configuration system
- Inventory information retrieval
- Sensor information access (temperature, humidity, voltage, current, accelerometer, gyroscope)
- EEPROM read/write functionality
- System level functions (LEDs, fans, power supply)
- Simulation mode for development and testing
- Board probing functionality

### Features
- System configuration via YAML files
- Comprehensive sensor monitoring
- Device inventory management
- GPIO and I2C device support
- PMBus device integration
- CLI interface with click framework
- Extensive documentation and examples

## [0.12.0] - 2024-10-15

### Added
- Enhanced device support
- Improved error handling
- Extended CLI functionality

## [0.11.0] - 2024-10-01

### Added
- Additional board configurations
- Enhanced sensor support
- Improved documentation

## [0.10.0] - 2024-09-15

### Added
- Core system management functionality
- Initial YAML configuration support
- Basic sensor framework
- CLI foundation

## [0.9.0] - 2024-09-01

### Added
- Device abstraction layer
- Initial sensor implementations
- Configuration framework

## [0.8.0] - 2024-08-15

### Added
- Basic system framework
- Initial device detection
- Core utility functions

## [0.7.0] - 2024-08-01

### Added
- Project foundation
- Initial system abstraction
- Basic device framework

## [0.6.0] - 2024-07-15

### Added
- Early development framework
- Initial concepts and architecture

## [0.5.0] - 2024-07-01

### Added
- Alpha version with core concepts
- Basic system management ideas

## [0.4.0] - 2024-06-15

### Added
- Early experimental features
- Initial development structure

## [0.3.0] - 2024-06-01

### Added
- Foundation development
- Core architecture planning

## [0.2.1] - 2024-05-20

### Fixed
- Initial bug fixes and improvements

## [0.2.0] - 2024-05-15

### Added
- Initial development version
- Basic project structure

## [0.1.36] - 2024-09-21

### Added
- Final alpha improvements before major version

## [0.1.35] - [0.1.21] - 2024-09-20

### Added
- Early development versions
- Initial framework development
- Basic testing infrastructure
- Documentation foundation
- Unit test framework
- Initial commit and project setup

---

## Release Notes

### About ekfsm

The EKF System Management Library (ekfsm) is a comprehensive sensor monitoring suite designed for Compact PCI Serial devices. It provides a Python framework for accessing system management functions on Linux-based modular hardware systems.

### Key Features

- **System Configuration**: YAML-based configuration files for easy setup
- **Hardware Inventory**: Comprehensive system and component inventory information
- **Sensor Monitoring**: Support for temperature, humidity, voltage, current, accelerometer, gyroscope sensors
- **EEPROM Management**: Read and write capabilities for EEPROM contents
- **System Control**: Access to LEDs, fans, power supplies, and other system-level functions
- **Simulation Mode**: Development and testing capabilities without physical hardware
- **Device Probing**: Automatic detection and configuration of boards in slots

### Installation

The package requires Python 3.12+ and should be installed in a virtual environment:

```bash
python -m venv myvenv
source myvenv/bin/activate
pip install ekfsm --index-url https://gitlab.ekf.com/api/v4/projects/407/packages/pypi/simple
```

### Dependencies

Key dependencies include:
- io4edge_client (>=2.4.1)
- click (>=8.0.1)
- gpiod (>=2.1.0)
- protobuf (>=6.32.1)
- Various utility libraries for system management

### Support

For issues and support, please refer to the project repository or contact the development team.
