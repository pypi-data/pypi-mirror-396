# Lager CLI

A powerful command-line interface for controlling embedded hardware, test equipment, and development boards through Lager Data gateway devices.

[![PyPI version](https://badge.fury.io/py/lager-cli.svg)](https://badge.fury.io/py/lager-cli)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

### Hardware Control
- **Power Management**: Control power supplies, battery simulators, solar simulators, and electronic loads
- **I/O Operations**: ADC/DAC, GPIO, thermocouple sensors
- **Test Instruments**: Oscilloscopes, logic analyzers, multimeters, signal generators

### Embedded Development
- **Debugging**: ARM Cortex-M debugging with J-Link, CMSIS-DAP, ST-Link support
- **Firmware Flashing**: Flash firmware via debug probes
- **Serial Communication**: UART terminal with test framework integration
- **Robotics**: Robot arm control for automated testing

### Wireless & Connectivity
- **Bluetooth LE**: Scan, connect, and interact with BLE devices
- **USB**: Programmable USB hub control
- **Webcam**: Video streaming from gateway devices

## Installation

Install the Lager CLI using pip:

```bash
pip install lager-cli
```

Or upgrade to the latest version:

```bash
pip install -U lager-cli
```

## Quick Start

1. **Configure your gateway**:
   ```bash
   lager defaults set gateway <your-gateway-id>
   ```

2. **Test connectivity**:
   ```bash
   lager hello
   ```

3. **List available instruments**:
   ```bash
   lager instruments
   ```

4. **Control a power supply**:
   ```bash
   lager supply <net> voltage 3.3 --dut <gateway-id>
   ```

## Core Commands

### Power Supply Control
```bash
# Set voltage and enable output
lager supply <net> voltage 3.3 --yes

# Set current limit
lager supply <net> current 0.5

# Check power state
lager supply <net> state
```

### ADC/DAC Operations
```bash
# Read ADC voltage
lager adc <net>

# Set DAC output
lager dac <net> 1.8
```

### Embedded Debugging
```bash
# Connect to debug probe
lager debug <net> connect --dut <dut>

# Flash firmware (auto-connects if needed)
lager debug <net> flash --hex firmware.hex --dut <dut>

# Reset and halt target
lager debug <net> reset --halt --dut <dut>

# Stream RTT logs
lager debug <net> rtt --dut <dut>

# Read memory
lager debug <net> memrd 0x08000000 256 --dut <dut>
```

### Oscilloscope & Logic Analyzer
```bash
# Measure frequency on scope channel
lager scope <net> measure freq

# Configure edge trigger
lager logic <net> trigger edge --slope rising --level 1.8
```

### Battery & Solar Simulation
```bash
# Set battery state of charge
lager battery <net> soc 80

# Configure solar irradiance
lager solar <net> irradiance 1000
```

### Serial Communication
```bash
# Connect to UART
lager uart --baudrate 115200

# Interactive mode with test runner
lager uart -i --test-runner unity

# Show the tty path for a UART net
lager uart <net> serial-port

# Create a UART net for an adapter without a USB serial number (store /dev path directly)
lager nets create <net> uart /dev/ttyUSB0 <label> --box <gateway>
# Warning: tty names can change after reboot; prefer device-serial mode when available
```

### Bluetooth LE
```bash
# Scan for BLE devices
lager ble scan --timeout 5.0

# Connect to device
lager ble connect <address>
```

## Configuration

### Gateway Setup

The CLI can connect to gateways via:
- **Cloud API**: Using gateway IDs
- **Direct IP**: Using Tailscale or VPN IP addresses

Create a `.lager` file in your project directory:

```json
{
  "duts": {
    "my-gateway": "gateway-abc123",
    "local-gateway": "100.91.127.26"
  }
}
```

### Direct IP Access

For direct IP connections, ensure SSH key authentication is configured:

```bash
# Configure SSH key for a gateway
ssh-copy-id lagerdata@<gateway-ip>

# Then connect via the CLI
lager ssh --dut <gateway-ip>
```

### Environment Variables

- `LAGER_GATEWAY`: Default gateway ID or IP address
- `LAGER_DEBUG`: Enable debug output
- `LAGER_COMMAND_DATA`: Command data (used internally)

## Net Management

Lager uses "nets" to represent physical test points or signals on your PCB:

```bash
# List all configured nets
lager nets

# Create a new power supply net
lager nets create VDD_3V3 supply 1 USB0::0x1AB1::0x0E11::DP8C0000001

# Auto-discover and create all nets
lager nets create-all

# Interactive TUI for net management
lager nets tui
```

## Advanced Features

### Remote Python Execution
```bash
# Run a Python script on the gateway
lager python my_script.py --dut <gateway-id>

# Run with port forwarding
lager python --port 5000:5000/tcp server.py
```

### Development Environment
```bash
# Create a development environment
lager devenv create --image python:3.10

# Open interactive terminal
lager devenv terminal
```

### Package Management
```bash
# Install packages on gateway
lager pip install numpy
```

## Supported Hardware

### Debug Probes
- SEGGER J-Link
- ARM CMSIS-DAP
- ST-Link v2/v3
- Xilinx XDS110

### Power Supplies
- Rigol DP800 series
- Keysight E36200/E36300 series
- Keithley 2200/2280 series

### Battery Simulators
- Keithley 2281S

### Solar Simulators
- EA PSI/EL series (two-quadrant)

### Oscilloscopes
- Rigol MSO5000 series

### I/O Hardware
- LabJack T7 (ADC/DAC/GPIO)
- MCC USB-202 (ADC/DAC/GPIO)

### USB Hubs
- Acroname USBHub3+
- YKUSH

### Robotics
- Rotrics Dexarm

### Temperature
- Phidget Thermocouples

## Target Microcontrollers

Supports debugging and flashing for:
- STM32 (F0/F1/F2/F3/F4/F7/G0/G4/H7/L0/L1/L4/WB/WL series)
- Nordic nRF52/nRF91
- Atmel/Microchip SAM D/E/4S/70
- Texas Instruments CC32xx
- NXP i.MX RT, LPC54xx/55xx
- Silicon Labs EFM32
- Microchip PIC32MM

## Authentication & Access

The CLI authenticates to gateways via VPN access (Tailscale or similar). Access control is managed by your VPN permissions - if you have VPN access to a gateway, you can control it with the CLI.

### Prerequisites

1. **VPN Access**: Connect to your organization's VPN (Tailscale, etc.)
2. **SSH Keys**: Configure SSH key authentication for direct gateway access:
   ```bash
   ssh-copy-id lagerdata@<gateway-ip>
   ```
3. **SSH to Gateway**: Use the CLI to connect:
   ```bash
   lager ssh --dut <gateway-ip-or-name>
   ```

### Verify Connectivity

```bash
# Test gateway connectivity
lager hello --dut <gateway-id-or-ip>

# Check DUT status
lager status
```

## Documentation

For detailed documentation, visit: [https://docs.lagerdata.com](https://docs.lagerdata.com)

### Command Help

Every command has built-in help:

```bash
lager --help                 # Show all commands
lager supply --help          # Show supply command options
lager debug --help           # Show debug command options
```

## Examples

### Automated Test Script

```bash
#!/bin/bash

DUT="my-gateway"

# Configure power supply
lager supply VDD voltage 3.3 --dut $DUT --yes

# Flash firmware
lager debug DEBUG_SWD flash --hex build/firmware.hex --dut $DUT

# Reset and start
lager debug DEBUG_SWD reset --dut $DUT

# Monitor UART output
lager uart --baudrate 115200 --test-runner unity --dut $DUT

# Read sensor values
voltage=$(lager adc SENSOR_OUT --dut $DUT)
temp=$(lager thermocouple TEMP1 --dut $DUT)

echo "Voltage: $voltage V"
echo "Temperature: $temp °C"

# Disable power
lager supply VDD disable --dut $DUT
```

### Interactive Python Control

```python
# example_test.py - Run on gateway with: lager python example_test.py

from lager.supply import supply
from lager.adc import adc
import time

# Set power supply voltage
supply.set_voltage("VDD_3V3", 3.3)
supply.enable("VDD_3V3")

# Wait for stabilization
time.sleep(0.1)

# Measure voltage
voltage = adc.read("VOUT")
print(f"Output voltage: {voltage:.3f} V")

# Disable supply
supply.disable("VDD_3V3")
```

## Troubleshooting

### Connection Issues

```bash
# Test gateway connectivity
lager hello --dut <gateway-id>

# Check gateway status
lager status --dut <gateway-id>
```

### Permission Errors

For Tailscale/direct IP connections, ensure SSH keys are configured:

```bash
# Set up SSH keys
ssh-copy-id lagerdata@<gateway-ip>

# Test SSH access
lager ssh --dut <gateway-ip-or-name>
```

### Debug Probe Not Found

Verify J-Link GDB Server is installed on the gateway:

```bash
# Download J-Link to /tmp/ on your local machine
# Visit: https://www.segger.com/downloads/jlink/
# Download: JLink_Linux_V794a_x86_64.tgz to /tmp/

# Deploy gateway (J-Link will be installed automatically)
cd deployment
./setup_and_deploy_gateway.sh <gateway-ip>
```

### Authentication Issues

If you encounter connection issues:

1. **Verify VPN connection**: Ensure you're connected to the correct VPN
2. **Check SSH keys**: Verify SSH key authentication is configured
   ```bash
   ssh-copy-id lagerdata@<gateway-ip>
   ```
3. **Test SSH access**: Try connecting to the gateway
   ```bash
   lager ssh --dut <gateway-ip-or-name>
   ```
4. **Test connectivity**: Use `lager hello` to verify the gateway is reachable
   ```bash
   lager hello --dut <gateway-ip-or-name>
   ```

## Contributing

We welcome contributions! Please see our contribution guidelines for more information.

## Support

- **Documentation**: https://docs.lagerdata.com
- **Issues**: Report bugs and request features via your support channel
- **Email**: hello@lagerdata.com

## License

MIT License - Copyright (c) Lager Data LLC

## Testing

Comprehensive test suites are available in the `test/` directory:

```bash
# Hardware-dependent tests (require instruments)
cd test
./supply.sh <DUT> <SUPPLY_NET>
./battery.sh <DUT> <BATTERY_NET>
./debug.sh <DUT> <DEBUG_NET> <HEXFILE> <ELFFILE>
./labjack.sh <DUT> <GPIO_NET> <ADC_NET> <DAC_NET>

# Gateway-only tests (no instruments required)
./deployment.sh <gateway-ip>
```

See `test/README.md` for test format and how to write new tests.

## Changelog

### Recent Updates
- Renamed test scripts for clarity (`test_*_commands.sh` → `*.sh`)
- Unified gateway deployment script (`setup_and_deploy_gateway.sh`)
- Added comprehensive test documentation (`test/README.md`)
- Enhanced debug command with RTT streaming and memory operations
- Improved error handling and validation across all commands

See full changelog in the [releases](https://github.com/lagerdata/lager-cli/releases).
