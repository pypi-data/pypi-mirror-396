# Release Notes - ekfsm

## Overview

ekfsm (EKF System Management Library) is a comprehensive Python framework for managing and monitoring CompactPCI Serial devices and modular hardware systems. These release notes highlight the key features, improvements, and user-facing changes in each major release.

---

## 🧪 Version 1.9.0-alpha.26-30 - December 15, 2025

**"Development Snapshot - IO4Edge Client Update"**

### What's New
- **Updated IO4Edge Client**: Upgraded to io4edge_client version 2.4.1 for improved device communication
- **Enhanced Dependency Management**: Better handling of package dependencies and version resolution
- **Development Improvements**: Refined build system and dependency resolution

### For Users
- More stable device communication with latest IO4Edge protocols
- Improved reliability for hardware operations
- Better error handling in device interactions

### Technical Details
- Updated io4edge_client dependency from >=2.0.3 to >=2.4.1
- Enhanced package resolution and cache handling
- Improved development workflow with better dependency management

**Note**: This is an alpha release intended for testing and development purposes.

---

## 🚀 Version 1.8.0 - November 25, 2025

**"Code Quality & Documentation Release"**

### What's New
- **Enhanced Code Quality**: Significant improvements to code readability and maintainability
- **Better Documentation**: Updated type hints and documentation across all modules
- **Improved Developer Experience**: Better formatted return statements and clearer error messages

### For Users
- More reliable error reporting
- Clearer API documentation
- Improved IDE support with better type hints

---

## 📚 Version 1.7.0 - November 25, 2025

**"Documentation Enhancement Release"**

### What's New
- **Updated Documentation**: Refreshed documentation requirements and dependencies
- **Better Development Experience**: Improved documentation build process

### For Users
- More comprehensive API documentation
- Better getting started guides
- Improved code examples

---

## ⚡ Version 1.6.0 - November 20, 2025

**"Performance & Reliability Release"**

### What's New
- **Enhanced IO4Edge Integration**: Improved client initialization with configurable timeouts
- **Better Logging**: Comprehensive logging across all device operations
- **Improved Reliability**: Enhanced timeout handling for hardware operations

### Key Improvements
- **Configurable Timeouts**: Customize command timeouts for different hardware setups
- **Better Diagnostics**: Enhanced logging helps troubleshoot device issues
- **Hardware Compatibility**: Updated slot coding for real system requirements

### For Users
- More reliable hardware communication
- Better error diagnostics
- Improved performance with timeout optimizations

---

## 🔧 Version 1.5.1 - November 20, 2025

**"Stability Hotfix"**

### What's Fixed
- **Critical Stability Fix**: Reverted problematic security changes that affected system stability
- **Improved Reliability**: Restored stable operation for production environments

### For Users
- Immediate stability improvements
- Recommended upgrade for all 1.5.0 users

---

## 🛡️ Version 1.5.0 - November 20, 2025

**"Security & Enhanced Hardware Support Release"**

### 🔒 Security Enhancements
- **Integrated Security Scanning**: Bandit security linter with comprehensive CI integration
- **Vulnerability Management**: Automated dependency scanning and vulnerability detection
- **Enhanced Security Reports**: JSON-based security reporting with artifact management

### 🔌 Hardware & Connectivity
- **Advanced Retry Logic**: Intelligent retry mechanisms for IO4Edge connection handling
- **Enhanced Hardware Support**: New configurations for EKF SHU-SHUTTLE and Z1010 devices
- **Improved Connection Reliability**: Better handling of connection rejections and timeouts

### 📊 Development & Testing
- **Performance Profiling**: New profiling tools for ekfsm and io4edge_client modules
- **Enhanced Testing**: Comprehensive CCTV connection test suite
- **Better Device Management**: Improved GPIO and binary I/O device handling

### For Users
- More secure operations with automated vulnerability scanning
- Better hardware compatibility and connection reliability
- Enhanced debugging and profiling capabilities

---

## 🏗️ Version 1.4.0 - November 15, 2025

**"Enhanced Device Management Release"**

### What's New
- **Comprehensive Device Logging**: Full logging support across all device initialization and operations
- **Smart Timeout Management**: Configurable timeout parameters for IO4Edge clients
- **Hardware Compatibility Updates**: Updated SMC slot coding for real system requirements

### Key Features
- **Better Debugging**: Detailed logs help identify and resolve device issues quickly
- **Flexible Configuration**: Adjust timeouts based on your hardware setup
- **Production Ready**: Enhanced reliability for production environments

### For Users
- Easier troubleshooting with comprehensive logging
- Better performance tuning with configurable timeouts
- Improved hardware compatibility

---

## 📦 Version 1.3.0 - November 10, 2025

**"Publishing & Architecture Enhancement Release"**

### 🚀 Distribution Improvements
- **PyPI.org Publishing**: Official package distribution through PyPI
- **UV Publishing Support**: Modern Python package management integration
- **Enhanced CI/CD**: Streamlined deployment pipeline

### 🏛️ Architecture Enhancements
- **Robust Exception Handling**: Comprehensive exception system for better error management
- **EEPROM Improvements**: Enhanced EEPROM operations with offset support
- **Code Quality**: Significant refactoring for maintainability and reliability

### For Users
- Easier installation through standard PyPI channels
- More reliable EEPROM operations
- Better error messages and exception handling

---

## 📖 Version 1.2.0 - November 5, 2025

**"Documentation & EEPROM Enhancement Release"**

### 📚 Documentation Excellence
- **Enhanced API Documentation**: Comprehensive examples and usage notes
- **Interactive CLI Documentation**: Sphinx-click integration for better CLI docs
- **Improved Board Documentation**: Detailed hardware documentation with examples

### 💾 EEPROM Management
- **Customer Area Writing**: New `write_customer_area` method with validation
- **Enhanced Safety**: Input validation and comprehensive error checking
- **Better Examples**: Real-world usage examples and best practices

### For Users
- Much clearer documentation with practical examples
- Safer EEPROM operations with built-in validation
- Better understanding of hardware capabilities

---

## 🎯 Version 1.1.0 - November 1, 2025

**"Documentation & CLI Enhancement Release"**

### What's New
- **Enhanced CLI Interface**: Comprehensive command-line options and documentation
- **GitVersion Integration**: Automated version management and tagging
- **Hardware Documentation**: Detailed EKF board documentation with product links

### Key Improvements
- **Better User Experience**: Improved CLI with clear options and help text
- **Hardware Reference**: Direct links to product documentation and specifications
- **Developer Tools**: Enhanced development workflow with GitVersion

### For Users
- More intuitive command-line interface
- Easy access to hardware documentation
- Better version tracking and release management

---

## 🏆 Version 1.0.0 - October 25, 2025

**"Initial Stable Release - Production Ready"**

### 🎉 Milestone Achievement
The first stable release of ekfsm - ready for production use in industrial environments.

### 🌟 Core Features
- **Complete System Management**: Full framework for CompactPCI Serial devices
- **YAML Configuration**: Intuitive configuration system for complex hardware setups
- **Comprehensive Sensor Support**: Temperature, humidity, voltage, current, accelerometer, gyroscope
- **Hardware Integration**: GPIO, I2C, PMBus device support
- **Industrial Grade**: Built for reliability in demanding environments

### 🔧 Key Capabilities
- **Device Inventory**: Automatic detection and cataloging of system components
- **EEPROM Management**: Safe read/write operations with validation
- **System Control**: LED control, fan management, power supply monitoring
- **Simulation Mode**: Development and testing without physical hardware
- **CLI Interface**: Professional command-line tools for system management

### For Users
- **Production Ready**: Stable, tested, and documented for industrial use
- **Easy Integration**: Simple APIs for embedding in larger systems
- **Comprehensive Support**: Full documentation, examples, and best practices
- **Future Proof**: Solid foundation for ongoing development and enhancement

---

## 📈 Development History (Pre-1.0)

### Version 0.12.0 - 0.2.0 (October 2024 - May 2024)
**"Foundation Development Phase"**

These versions established the core architecture and foundational features:

- **System Framework Development**: Core abstractions and device models
- **Configuration System**: YAML-based configuration foundation
- **Device Abstraction**: Generic device interfaces and implementations
- **CLI Foundation**: Basic command-line interface structure
- **Testing Infrastructure**: Unit test framework and validation tools

### Version 0.1.36 - 0.1.21 (September 2024)
**"Early Development & Proof of Concept"**

Initial development versions focusing on:

- **Architecture Design**: Core system design and patterns
- **Device Discovery**: Initial hardware detection capabilities
- **Basic Operations**: Fundamental read/write operations
- **Documentation Start**: Initial documentation and examples
- **Project Setup**: Development environment and build system

---

## 🔮 Looking Forward

### Upcoming Features
- **Enhanced Security**: Continued security improvements and vulnerability management
- **Extended Hardware Support**: Support for new device types and configurations
- **Performance Optimization**: Continued performance improvements and resource optimization
- **Cloud Integration**: Potential cloud connectivity and remote monitoring capabilities

### Community & Support
- **Open Development**: Transparent development process with regular updates
- **Community Feedback**: Active incorporation of user feedback and requirements
- **Long-term Support**: Commitment to stability and backward compatibility
- **Professional Support**: Available through EKF for commercial deployments

---

## 📞 Support & Resources

### Getting Help
- **Documentation**: Comprehensive API and usage documentation
- **Examples**: Real-world examples and best practices
- **Issue Tracking**: GitHub issues for bug reports and feature requests
- **Professional Support**: Contact EKF for commercial support options

### Installation
```bash
# Create virtual environment
python -m venv myvenv
source myvenv/bin/activate

# Install from EKF PyPI registry
pip install ekfsm --index-url https://gitlab.ekf.com/api/v4/projects/407/packages/pypi/simple
```

### Quick Start
```python
from ekfsm import System
from ekfsm.config import Config

# Load system configuration
config = Config("system.yaml")
system = System(config)

# Get system inventory
inventory = system.get_inventory()
print(f"System has {len(inventory.boards)} boards")

# Read temperature sensors
for sensor in system.temperature_sensors:
    temp = sensor.read()
    print(f"Sensor {sensor.name}: {temp}°C")
```

---

**ekfsm** - Professional system management for industrial hardware platforms.

*Copyright © 2024-2025 EKF. All rights reserved.*
