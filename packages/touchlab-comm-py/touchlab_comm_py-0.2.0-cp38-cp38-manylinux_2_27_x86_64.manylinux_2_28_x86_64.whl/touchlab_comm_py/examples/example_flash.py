#!/usr/bin/env python3

# Copyright (c) 2025 Touchlab Limited. All Rights Reserved
# Unauthorized copying or modifications of this file, via any medium is strictly prohibited.

import touchlab_comm_py as tl
import argparse

def show_progress(progress, total):
    percent = (float(progress) / float(total)) * 100.0
    print(f"\rFlashing: {percent:.1f}%", end='')

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Touchlab Sensor Example")
    parser.add_argument("port", type=str, help="Serial port to connect to")
    parser.add_argument("firmware_file", type=str, help="Parameter file to load")
    args = parser.parse_args()

    tl.FlashTool().flash_firmware(args.port, args.firmware_file, show_progress)
    print("\nFlashing completed successfully.")

if __name__ == "__main__":
    main()
