import sys, os, argparse, subprocess, json
from datetime import datetime
from pathlib import Path

SCRIPT_TITLE = "dump-wifi"
SCRIPT_NAME = os.path.basename(__file__)
SCRIPT_DESCRIPTION = "Dump JSON formatted data of saved Wi-Fi networks in Windows"

def printTitle():
    print("-"*len(SCRIPT_TITLE) + "\n" + SCRIPT_TITLE + "\n" + "-"*len(SCRIPT_TITLE))

def initialize():
    global parser
    #Initialize argparse object
    parser = argparse.ArgumentParser(prog=SCRIPT_NAME, description=SCRIPT_DESCRIPTION, add_help=True)

    #Create mutually exclusive group for inputs
    parser_group_input = parser.add_mutually_exclusive_group()
    
    #Optional Arguments
    parser_group_input.add_argument("--networks", help="dump all saved networks data as JSON", action="store_true")
    parser_group_input.add_argument("--passwords", help="dump passwords of all saved networks as JSON", action="store_true")
    parser_group_input.add_argument("--ssid", help="print password of specified ssid", type=str)
    
    global args
    args = parser.parse_args()
    
    global dumpFolder
    dumpFolder = Path(os.getcwd()) / "wifidumps"
    if not os.path.isdir(dumpFolder): os.makedirs(dumpFolder)

def dump_saved_wifi_networks():
    output = subprocess.run("netsh wlan show profiles", capture_output=True, text=True).stdout.split("\n")
    profiles = [s.split(":")[1][1:] for s in output if "All User Profile" in s]
    properties = [
        "SSID name",
        "Authentication",
        "Cipher",
        "Security key",
        "Key Content",
        "Connection mode",
        "Network broadcast",
        "AutoSwitch",
        "MAC Randomization",
        " Cost  ",
        "Cost Source",
        "Congested",
        "Approaching Data Limit",
        "Over Data Limit",
        "Roaming"
    ]
    wifi_networks = {}
    for profile in profiles:
        output = subprocess.run(f"netsh wlan show profile {profile} key=clear", capture_output=True, text=True).stdout.split("\n")
        data = {}
        for property in properties:
            property_value = [s.split(":")[1][1:] for s in output if property in s]
            if len(property_value) == 1:
                property_value = property_value[0]
            if property == " Cost  ":
                property = "Cost"
            if property == "SSID name":
                property_value = property_value[1:-1]
            data[property] = property_value
        wifi_networks[profile] = data
        
    outFilePath = Path(dumpFolder) / f"{timestamp} networks.json"
    with open(outFilePath, 'w') as outfile:
        json.dump(wifi_networks, outfile, indent=2)
        print(f"Dumped networks to {outFilePath}")

def dump_saved_wifi_passwords():
    output = subprocess.run("netsh wlan show profiles", capture_output=True, text=True).stdout.split("\n")
    profiles = [s.split(":")[1][1:] for s in output if "All User Profile" in s]
    wifi_passwords = {}
    for profile in profiles:
        output = subprocess.run(f"netsh wlan show profile {profile} key=clear", capture_output=True, text=True).stdout.split("\n")
        ssid = [s.split(":")[1][1:] for s in output if "SSID name" in s][0][1:-1]
        password = [s.split(":")[1][1:] for s in output if "Key Content" in s][0]
        wifi_passwords[ssid] = password
        
    outFilePath = Path(dumpFolder) / f"{timestamp} passwords.json"
    with open(outFilePath, 'w') as outfile:
        json.dump(wifi_passwords, outfile, indent=1)
        print(f"Dumped passwords to {outFilePath}")

def get_saved_wifi_password(ssid):
    output = subprocess.run("netsh wlan show profiles", capture_output=True, text=True).stdout.split("\n")
    profiles = [s.split(":")[1][1:] for s in output if "All User Profile" in s]
    for profile in profiles:
        output = subprocess.run(f"netsh wlan show profile {profile} key=clear", capture_output=True, text=True).stdout.split("\n")
        saved_ssid = [s.split(":")[1][1:] for s in output if "SSID name" in s][0][1:-1]
        saved_password = [s.split(":")[1][1:] for s in output if "Key Content" in s][0]
        if saved_ssid == ssid:
            return saved_password

def main():
    if len(sys.argv) > 1:        
        printTitle()        
        global timestamp
        timestamp = datetime.now().strftime("%H.%M.%S %d-%b-%Y")
        
        if args.networks:
            dump_saved_wifi_networks()
        if args.passwords:
            dump_saved_wifi_passwords()
        if args.ssid:
            print(get_saved_wifi_password(args.ssid))
        
    else:
        parser.print_help()

try:
    initialize()
    main()

except KeyboardInterrupt:
    sys.exit(1)
