# print('Hello, world! Your gateway is connected.')
import sys

# ANSI color codes
GREEN = '\033[92m'
RESET = '\033[0m'

# Get the IP address from command line argument if provided
if len(sys.argv) > 1:
    dut_ip = sys.argv[1]
    print(f'{GREEN}Hello from DUT {dut_ip}!{RESET}')
else:
    print(f'{GREEN}Hello, world! Your gateway is connected.{RESET}')
