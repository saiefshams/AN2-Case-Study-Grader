import os
import re
import tkinter as tk
from tkinter import filedialog
import csv
import subprocess
from ciscoconfparse import CiscoConfParse
from ipaddress import ip_address, ip_network


def cidr_to_decimal(cidr):
        """Converts CIDR notation to decimal subnet mask."""
        mapping = {
            '32': '255.255.255.255',
            '31': '255.255.255.254',
            '30': '255.255.255.252',
            '29': '255.255.255.248',
            '28': '255.255.255.240',
            '27': '255.255.255.224',
            '26': '255.255.255.192',
            '25': '255.255.255.128',
            '24': '255.255.255.0'
        }
        if '/' in cidr:
            ip, mask = cidr.split('/')
            return ip, mapping.get(mask, mask)
        return cidr, None


class CaseStudyGrader:
    def __init__(self):
        self.submissions_dir = None
        self.answer_key_dir = None
        self.groups = []
        self.output_csv = "grading_results.csv"
        self.device_keywords = {
            "Toronto": ["toronto"],
            "ISP": ["isp"],
            "Ottawa": ["ottawa", "ott"],
            "Oshawa": ["oshawa", "osh"],
            "TOR-A1": ["tor-a1", "a1"],
            "TOR-A2": ["tor-a2", "a2"],
            "TOR-D1": ["tor-d1", "d1"],
            "TOR-D2": ["tor-d2", "d2"]
        }

    def run(self):
        """Main execution flow."""
        self.check_submissions()
        self.initialize_csv()
        self.grade_submissions()

    def check_submissions(self):
        """Checks if submissions are already downloaded or calls canvasFetch.py to download them."""
        print("Do you already have the submissions downloaded?")
        answer = input("Enter 'y' for yes or 'n' for no: ").strip().lower()

        if answer == 'y':
            print("Select the directory containing submission folders...")
            root = tk.Tk()
            root.withdraw()
            self.submissions_dir = filedialog.askdirectory()
            if not self.submissions_dir:
                print("[ERROR] No directory selected. Exiting.")
                exit()
            print(f"[INFO] Selected submissions directory: {self.submissions_dir}")
        elif answer == 'n':
            print("[INFO] Running canvasFetch.py to download submissions...")
            subprocess.run(['python', 'canvasFetch.py'], check=True)
            print("[INFO] Submissions downloaded successfully.")
            print("Select the directory containing submission folders...")
            root = tk.Tk()
            root.withdraw()
            self.submissions_dir = filedialog.askdirectory()
            if not self.submissions_dir:
                print("[ERROR] No directory selected. Exiting.")
                exit()
            print(f"[INFO] Selected submissions directory: {self.submissions_dir}")
        else:
            print("[ERROR] Invalid input. Exiting.")
            exit()

    def initialize_csv(self):
        """Initializes the output CSV file."""
        with open(self.output_csv, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Group Name", "Task Name", "Grade", "Comments"])
        print(f"[INFO] Initialized CSV file: {self.output_csv}")

    def grade_submissions(self):
        """Grades submissions for each group."""
        print("[INFO] Grading submissions...")
        
        # Find all groups in the submission directory
        self.groups = [group for group in os.listdir(self.submissions_dir) if os.path.isdir(os.path.join(self.submissions_dir, group))]
        if not self.groups:
            print("[ERROR] No groups found. Exiting.")
            return

        # Iterate through each group for grading
        for i, group in enumerate(self.groups):
            print(f"[INFO] Grading submissions for {group}...")
            group_number = self.extract_group_number(group)  # Extract group number
            device_files = self.map_files_to_devices(os.path.join(self.submissions_dir, group))  # Map files to devices

            # Handle insufficient files
            if not device_files:
                print(f"[WARNING] Skipping {group} due to insufficient files.")
                continue

            # Log detected files
            print(f"[INFO] Detected files for group {group}:")
            for device, filepath in device_files.items():
                print(f"    {device}: {filepath}")

            # Grade Task 1
            print(f"[INFO] Starting grading for Task 1...")
            task_1_results = self.grade_task_1(device_files, group_number)
            self.write_to_csv(group, "Task 1", task_1_results["grade"], task_1_results["comments"])

            # Grade Task 2
            print(f"[INFO] Starting grading for Task 2...")
            task_2_results = self.grade_task_2(device_files, group_number)
            self.write_to_csv(group, "Task 2", task_2_results["grade"], task_2_results["comments"])

            # Grade Task 3
            print(f"[INFO] Starting grading for Task 3...")
            task_3_results = self.grade_task_3(device_files, group_number)
            self.write_to_csv(group, "Task 3", task_3_results["grade"], task_3_results["comments"])

            # Grade Task 4
            print(f"[INFO] Starting grading for Task 4...")
            task_4_results = self.grade_task_4(device_files, group_number)
            self.write_to_csv(group, "Task 4", task_4_results["grade"], task_4_results["comments"])

            # Grade Task 5
            print(f"[INFO] Starting grading for Task 5...")
            task_5_results = self.grade_task_5(device_files, group_number)
            self.write_to_csv(group, "Task 5", task_5_results["grade"], task_5_results["comments"])

            # Grade Task 6
            print(f"[INFO] Starting grading for Task 6...")
            task_6_results = self.grade_task_6(device_files, group_number)
            self.write_to_csv(group, "Task 6", task_6_results["grade"], task_6_results["comments"])

            # Grade Task 7
            print(f"[INFO] Starting grading for Task 7...")
            task_7_results = self.grade_task_7(device_files, group_number)
            self.write_to_csv(group, "Task 7", task_7_results["grade"], task_7_results["comments"])

            # Grade Task 8
            print(f"[INFO] Starting grading for Task 8...")
            task_8_results = self.grade_task_8(device_files)
            self.write_to_csv(group, "Task 8", task_8_results["grade"], task_8_results["comments"])

            # Calculate total grade
            total_grade = sum([
                task_1_results["grade"],
                task_2_results["grade"],
                task_3_results["grade"],
                task_4_results["grade"],
                task_5_results["grade"],
                task_6_results["grade"],
                task_7_results["grade"],
                task_8_results["grade"]
            ])
            print(f"[GRADE] Total grade for {group}: {total_grade}/139")
            print(f"[GRADE] Percentage grade for {group}: {total_grade / 139 * 100:.2f}%")

            # Ask if the user wants to continue to the next group
            if i < len(self.groups) - 1:
                next_group = self.groups[i + 1]
                answer = input(f"Do you want to continue grading? Next group is {next_group} (y/n): ").strip().lower()
                if answer != 'y':
                    print("[INFO] Grading process terminated by user.")
                    break

        print("[INFO] Grading completed for all groups.")

    def extract_group_number(self, group_name):
        """Extracts the group number dynamically from the group name."""
        try:
            group_number = int("".join(filter(str.isdigit, group_name)))
            print(f"[INFO] Group {group_name}: Detected group number {group_number}")
            return group_number
        except ValueError:
            print(f"[ERROR] Could not extract group number from {group_name}. Exiting.")
            exit()

    def map_files_to_devices(self, group_path):
        """Maps configuration files to devices using flexible matching with filename and hostname logic."""
        device_files = {}
        unmatched_files = []

        # Step 1: Match using filename keywords
        for filename in os.listdir(group_path):
            filepath = os.path.join(group_path, filename)
            if not os.path.isfile(filepath):
                continue

            matched = False
            # Match using filename keywords
            for device, keywords in self.device_keywords.items():
                if any(keyword.lower() in filename.lower() for keyword in keywords):
                    if device in device_files:
                        print(f"[WARNING] Overwriting existing file for device {device}: {device_files[device]} with {filepath}")
                    device_files[device] = filepath
                    matched = True
                    print(f"[INFO] Matched {filepath} to {device} using filename keywords.")
                    break

            if not matched:
                unmatched_files.append(filepath)  # Collect files for hostname fallback

        # Step 2: Fallback to hostname-based matching
        for filepath in unmatched_files:
            hostname = self.extract_hostname(filepath)
            if hostname:
                # Attempt to map hostname to device_keywords
                for device, keywords in self.device_keywords.items():
                    if hostname.lower() in keywords:
                        if device in device_files:
                            print(f"[WARNING] Overwriting existing file for device {device}: {device_files[device]} with {filepath}")
                        device_files[device] = filepath
                        print(f"[INFO] Matched {filepath} to {device} using hostname {hostname}.")
                        break
                else:
                    print(f"[WARNING] Hostname '{hostname}' from {filepath} did not match any device.")
            else:
                print(f"[WARNING] Could not extract hostname from: {filepath}")

        # Step 3: Handle insufficient files for the group
        if len(device_files) < 4:
            print(f"[WARNING] Detected only {len(device_files)} files in {group_path}. Skipping this group.")
            return {}

        # Step 4: Log all detected files
        print(f"[INFO] Mapped files for group: {device_files}")
        return device_files

    def extract_hostname(self, filepath):
        """Extracts hostname from a configuration file."""
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    match = re.match(r'^hostname (\S+)', line.strip(), re.IGNORECASE)
                    if match:
                        return match.group(1)  # Extract hostname directly
            print(f"[WARNING] Hostname not found in: {filepath}")
            return None
        except Exception as e:
            print(f"[ERROR] Failed to open {filepath}: {e}")
            return None

    def grade_task_1(self, device_files, group_number):
        """
        Grades Task 1: Addressing.
        Validates IP addresses, interfaces, and VLANs using new rubric.
        """
        comments = []
        grade = 3.5  # Start with full marks, deduct 0.5 per incorrect or missing configuration

        # Dynamically adjust working configs for group number
        expected_addresses = {
            "ISP": {
                "GigabitEthernet0/0/0": f"10.202.10.2/29",
                "GigabitEthernet0/0/1": f"10.202.20.2/29",
                "Loopback1": f"2.2.2.2/32"
            },
            "Toronto": {
                "GigabitEthernet0/0/0": f"10.202.10.1/29",
                "GigabitEthernet0/0/1.10": f"172.16.{group_number}.1/24",
                "GigabitEthernet0/0/1.100": f"199.212.32.{group_number}/24",
                "Loopback1": f"1.1.1.1/32",
                "Tunnel1": f"10.1.{group_number}.1/24"
            },
            "Ottawa": {
                "GigabitEthernet0/0/0": f"10.202.20.3/29",
                "GigabitEthernet0/0/1": f"209.165.200.{group_number}/24",
                "Loopback1": f"3.3.3.3/32",
                "Loopback101": f"172.16.84.{group_number}/24",
                "Loopback102": f"172.16.85.{group_number}/24",
                "Loopback103": f"172.16.86.{group_number}/24",
                "Tunnel1": f"10.1.{group_number}.2/24"
            },
            "Oshawa": {
                "GigabitEthernet0/0/1": f"198.51.100.{group_number}/24",
                "Loopback1": f"4.4.4.4/32",
                "Loopback101": f"172.16.87.{group_number}/24",
                "Loopback102": f"172.16.88.{group_number}/24",
                "Loopback103": f"172.16.89.{group_number}/24",
                "Tunnel1": f"10.1.{group_number}.3/24"
            },
            "TOR-D2": {
                "Vlan100": f"199.212.32.254/24",
                "Vlan300": f"209.165.200.254/24",
                "Vlan400": f"198.51.100.254/24"
            }
        }

        # SVIs for TOR-D1, TOR-A1 and TOR-A2 cz they be special
        svi_addresses = {
            "Vlan10": f"172.16.{group_number}.0/24",
            f"Vlan{200 + group_number}": f"172.16.{100+group_number}.0/24",
            f"Vlan{300 + group_number}": f"172.16.{200+group_number}.0/24"
        }

        def is_ip_in_subnet(ip, subnet):
            """Helper function to check if an IP address is in a subnet."""
            return ip_address(ip) in ip_network(subnet)

        for device, filepath in device_files.items():
            print(f"[INFO] Grading file: {filepath}")
            try:
                submission = CiscoConfParse(filepath)
                print(f"[INFO] Detected hostname: {device}")

                # Check main device IP addresses
                if device in expected_addresses:
                    for interface, expected_ip_cidr in expected_addresses[device].items():
                        ip, expected_mask = cidr_to_decimal(expected_ip_cidr)
                        print(f"[INFO] Checking {device} - Interface: {interface}")

                        interface_obj = submission.find_objects(rf"^interface {interface}")
                        if not interface_obj:
                            print(f"[WARNING] {device} - Missing interface {interface}")
                            comments.append(f"{device} Missing interface {interface}")
                            grade -= 0.5
                            continue

                        found_ip = False
                        for child in interface_obj[0].children:
                            if "ip address" in child.text:
                                parts = child.text.strip().split()
                                actual_ip, actual_mask = parts[2], parts[3]
                                if actual_ip == ip and actual_mask == expected_mask:
                                    print(f"[INFO] {device} - Interface {interface}: Correct IP ({actual_ip}/{actual_mask})")
                                    found_ip = True
                                    break

                        if not found_ip:
                            print(f"[WARNING] {device} - Interface {interface}: Expected {ip}/{expected_mask}, but not found")
                            comments.append(f"{device} Incorrect IP on {interface} (Expected: {ip}/{expected_mask})")
                            grade -= 0.5

                # Check TOR-D1, TOR-A1 and TOR-A2 SVIs
                if device in ["TOR-D1", "TOR-A1", "TOR-A2"]:
                    for svi, expected_subnet in svi_addresses.items():
                        print(f"[INFO] Checking {device} - SVI: {svi}")

                        svi_obj = submission.find_objects(rf"^interface {svi}")
                        if not svi_obj:
                            print(f"[WARNING] {device} - Missing SVI {svi}")
                            comments.append(f"{device} Missing SVI {svi}")
                            grade -= 0.5
                            continue

                        found_ip = False
                        for child in svi_obj[0].children:
                            if "ip address" in child.text:
                                parts = child.text.strip().split()
                                actual_ip = parts[2]
                                if is_ip_in_subnet(actual_ip, expected_subnet):
                                    print(f"[INFO] {device} - SVI {svi}: Correct IP in range {expected_subnet}")
                                    found_ip = True
                                    break

                        if not found_ip:
                            print(f"[WARNING] {device} - SVI {svi}: Expected IP in range {expected_subnet}, but not found")
                            comments.append(f"{device} Incorrect IP on SVI {svi} (Expected: {expected_subnet})")
                            grade -= 0.5

            except Exception as e:
                print(f"[ERROR] {device}: Failed to parse configuration - {e}")
                comments.append(f"{device} Parse error")


        grade = max(0, grade)  # Ensure grade doesn't drop below 0
        return {"grade": grade, "comments": " | ".join(comments)}
    
    def grade_task_2(self, device_files, group_number):
        """
        Grades Task 2: Switch Configuration.
        Validates trunk links, EtherChannels, and SVIs according to the rubric.
        """
        comments = []
        grade = 31.0  # Start with full marks, deduct for issues found.

        # Define switches and exclude routers
        switch_devices = ["TOR-D1", "TOR-D2", "TOR-A1", "TOR-A2"]

        # Validation criteria
        trunk_interfaces = {
            "TOR-D1": ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2", "GigabitEthernet1/0/3", "GigabitEthernet1/0/4",
                    "GigabitEthernet1/0/5", "GigabitEthernet1/0/6", "GigabitEthernet1/0/7", "GigabitEthernet1/0/8", 
                    "GigabitEthernet1/0/11"],
            "TOR-D2": ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2", "GigabitEthernet1/0/3", "GigabitEthernet1/0/4", 
                    "GigabitEthernet1/0/5", "GigabitEthernet1/0/6", "GigabitEthernet1/0/7", "GigabitEthernet1/0/8"],
            "TOR-A1": ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2", "GigabitEthernet1/0/3", "GigabitEthernet1/0/4"],
            "TOR-A2": ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2", "GigabitEthernet1/0/3", "GigabitEthernet1/0/4"]
        }

        etherchannel_interfaces = {
            "TOR-D1": {"Port-channel1": ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2", "GigabitEthernet1/0/3", "GigabitEthernet1/0/4"],
                    "Port-channel2": ["GigabitEthernet1/0/5", "GigabitEthernet1/0/6"],
                    "Port-channel3": ["GigabitEthernet1/0/7", "GigabitEthernet1/0/8"]},
            "TOR-D2": {"Port-channel1": ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2", "GigabitEthernet1/0/3", "GigabitEthernet1/0/4"],
                    "Port-channel2": ["GigabitEthernet1/0/5", "GigabitEthernet1/0/6"],
                    "Port-channel3": ["GigabitEthernet1/0/7", "GigabitEthernet1/0/8"]},
            "TOR-A1": {"Port-channel2": ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2"], 
                    "Port-channel3": ["GigabitEthernet1/0/3", "GigabitEthernet1/0/4"]},
            "TOR-A2": {"Port-channel2": ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2"], 
                    "Port-channel3": ["GigabitEthernet1/0/3", "GigabitEthernet1/0/4"]}
        }

        svi_interfaces = [f"Vlan10", f"Vlan{group_number + 200}", f"Vlan{group_number + 300}"]  # Adjust SVIs dynamically based on group number

        # Unused interfaces - spot check a few ports, and make sure they're shutdown and set to VLAN 999
        unused_interfaces = {
            "TOR-D1": ["GigabitEthernet1/0/13", "GigabitEthernet1/0/14", "GigabitEthernet1/0/15"],
            "TOR-D2": ["GigabitEthernet1/0/16", "GigabitEthernet1/0/17", "GigabitEthernet1/0/18"],
            "TOR-A1": ["GigabitEthernet1/0/19", "GigabitEthernet1/0/20", "GigabitEthernet1/0/21"],
            "TOR-A2": ["GigabitEthernet1/0/22", "GigabitEthernet1/0/23", "GigabitEthernet1/0/24"]
        }

        points_distribution = {
            "trunks_and_dtp": 5,
            "vlan_pruning": 8,
            "tor_d1_g1_0_11": 2,
            "tor_d2_access_ports": 2,
            "unused_ports": 2,
            "etherchannels": 8,
            "svis": 4
        }

        # Iterate through detected files for switch devices
        for device, filepath in device_files.items():
            if device not in switch_devices:
                print(f"[INFO] Skipping {device}: Task 2 does not apply to routers.")
                continue

            print(f"[INFO] Grading file: {filepath}")
            try:
                submission = CiscoConfParse(filepath)

                # Task 2.3: Validate Static Trunk Links and Disable DTP
                all_nonegotiate = True
                if device in trunk_interfaces:
                    print(f"[INFO] Validating trunk links for {device}...")
                    for interface in trunk_interfaces[device]:
                        interface_obj = submission.find_objects(rf"^interface {interface}")
                        if not interface_obj:
                            print(f"[WARNING] {device} - Missing trunk interface {interface}.")
                            comments.append(f"{device} Missing trunk interface {interface}")
                            grade -= 1.0 / len(trunk_interfaces)  # Split 1 point across switches
                            continue

                        children = [child.text.strip() for child in interface_obj[0].children]
                        if "switchport mode trunk" not in children:
                            print(f"[WARNING] {device} - Interface {interface} is not a trunk.")
                            comments.append(f"{device} Interface {interface} is not a trunk")
                            grade -= 1.0 / len(trunk_interfaces)
                        if "switchport nonegotiate" not in children:
                            all_nonegotiate = False

                # Give bonus 1 point if all trunk links have nonegotiate
                if all_nonegotiate:
                    print(f"[INFO] Awarding 1 bonus point for nonegotiate on all trunk links.")
                    grade += 1.0
                
                # Task 2.4: Validate VLAN Pruning
                print(f"[INFO] Validating VLAN pruning for {device}...")
                vlan_pruning = {
                    "TOR-D1": {
                        "Port-channel1": "10,100," + str(group_number + 200) + "," + str(group_number + 300),
                        "Port-channel2": "10," + str(group_number + 200) + "," + str(group_number + 300),
                        "Port-channel3": "10," + str(group_number + 200) + "," + str(group_number + 300)
                    },
                    "TOR-D2": {
                        "Port-channel1": "10,100," + str(group_number + 200) + "," + str(group_number + 300),
                        "Port-channel2": "10," + str(group_number + 200) + "," + str(group_number + 300),
                        "Port-channel3": "10," + str(group_number + 200) + "," + str(group_number + 300)
                    }
                }

                # Iterate over each Port-channel interface and validate mandatory VLANs
                for pc_interface, vlan_list in vlan_pruning.get(device, {}).items():
                    mandatory_vlans = vlan_list.split(",")
                    # Locate the Port-channel interface
                    pc_obj = submission.find_objects(rf"^interface {pc_interface}")
                    if not pc_obj:
                        print(f"[WARNING] {device} - Missing {pc_interface}.")
                        comments.append(f"{device} Missing {pc_interface}")
                        grade -= points_distribution["vlan_pruning"] / len(vlan_pruning[device])
                        continue

                    # Check VLAN pruning configuration on the Port-channel
                    children = [child.text.strip() for child in pc_obj[0].children]
                    allowed_vlans = None
                    for child in children:
                        if "switchport trunk allowed vlan" in child:
                            allowed_vlans = child.replace("switchport trunk allowed vlan ", "").split(",")

                    # Validate mandatory VLANs
                    for vlan in mandatory_vlans:
                        if allowed_vlans and vlan not in allowed_vlans:
                            print(f"[WARNING] {device} - Missing mandatory VLAN {vlan} on {pc_interface}.")
                            comments.append(f"{device} Missing mandatory VLAN {vlan} on {pc_interface}")
                            grade -= points_distribution["vlan_pruning"] / len(mandatory_vlans)

                # Task 2.5: TOR-D1 G1/0/11 Configuration
                print(f"[INFO] Validating TOR-D1 G1/0/11 configuration...")
                if device == "TOR-D1":
                    interface_obj = submission.find_objects(r"^interface GigabitEthernet1/0/11")
                    if not interface_obj:
                        print(f"[WARNING] {device} - Missing interface G1/0/11.")
                        comments.append(f"{device} Missing interface G1/0/11")
                        grade -= points_distribution["tor_d1_g1_0_11"]

                # Task 2.6: Validate TOR-D2 Access Ports
                print(f"[INFO] Validating TOR-D2 access ports configuration...")
                if device == "TOR-D2":
                    for interface, vlan in {"GigabitEthernet1/0/11": 300, "GigabitEthernet1/0/12": 400}.items():
                        interface_obj = submission.find_objects(rf"^interface {interface}")
                        if not interface_obj:
                            print(f"[WARNING] {device} - Missing interface {interface}.")
                            comments.append(f"{device} Missing interface {interface}")
                            grade -= points_distribution["tor_d2_access_ports"] / 2  # Split between both interfaces
                            continue

                        children = [child.text.strip() for child in interface_obj[0].children]
                        if f"switchport access vlan {vlan}" not in children:
                            print(f"[WARNING] {device} - Interface {interface} not assigned to VLAN {vlan}.")
                            comments.append(f"{device} Interface {interface} not assigned to VLAN {vlan}")
                            grade -= points_distribution["tor_d2_access_ports"] / 2
                        if "switchport mode access" not in children:
                            print(f"[WARNING] {device} - Interface {interface} is not configured as an access port.")
                            comments.append(f"{device} Interface {interface} is not configured as an access port")
                            grade -= points_distribution["tor_d2_access_ports"] / 2

                # Task 2.7: Validate Unused Ports
                print(f"[INFO] Validating unused ports for {device}...")
                for unused_port in unused_interfaces.get(device, []):
                    interface_obj = submission.find_objects(rf"^interface {unused_port}")
                    if not interface_obj:
                        print(f"[WARNING] {device} - Missing configuration for unused port {unused_port}.")
                        comments.append(f"{device} Missing configuration for unused port {unused_port}")
                        grade -= points_distribution["unused_ports"] / len(unused_interfaces[device])  # Split points across unused ports
                        continue

                    children = [child.text.strip() for child in interface_obj[0].children]
                    if "switchport access vlan 999" not in children:
                        print(f"[WARNING] {device} - Unused port {unused_port} not assigned to VLAN 999.")
                        comments.append(f"{device} Unused port {unused_port} not assigned to VLAN 999")
                        grade -= points_distribution["unused_ports"] / len(unused_interfaces[device])
                    if "shutdown" not in children:
                        print(f"[WARNING] {device} - Unused port {unused_port} is not shut down.")
                        comments.append(f"{device} Unused port {unused_port} is not shut down")
                        grade -= points_distribution["unused_ports"] / len(unused_interfaces[device])

                # Task 2.8: Validate EtherChannels
                print(f"[INFO] Validating EtherChannels for {device}...")

                if device in etherchannel_interfaces:
                    for port_channel, member_interfaces in etherchannel_interfaces[device].items():
                        # Locate the Port-channel interface
                        pc_obj = submission.find_objects(rf"^interface {port_channel}")
                        if not pc_obj:
                            print(f"[WARNING] {device} - {port_channel} is missing.")
                            comments.append(f"{device} Missing EtherChannel {port_channel}")
                            grade -= points_distribution["etherchannels"] / len(etherchannel_interfaces[device])
                            continue

                        # Expected protocol for the Port-channel
                        expected_protocol = (
                            "Static" if port_channel == "Port-channel1" else
                            ("PAgP" if port_channel == "Port-channel2" and device in ["TOR-D1", "TOR-A1"] else
                            "LACP" if port_channel == "Port-channel2" and device in ["TOR-D2", "TOR-A2"] else
                            "PAgP" if port_channel == "Port-channel3" and device in ["TOR-D1", "TOR-A2"] else
                            "LACP" if port_channel == "Port-channel3" and device in ["TOR-D2", "TOR-A1"] else None)
                        )

                        # Detect protocol from member interfaces
                        detected_protocol = None
                        for interface in member_interfaces:
                            int_obj = submission.find_objects(rf"^interface {interface}")
                            if not int_obj:
                                print(f"[WARNING] {device} - Missing interface {interface} in {port_channel}.")
                                comments.append(f"{device} Missing interface {interface} in {port_channel}")
                                grade -= (points_distribution["etherchannels"] / len(etherchannel_interfaces[device])) / len(member_interfaces)
                                continue

                            # Parse channel-group mode for protocol detection
                            children = [child.text.strip() for child in int_obj[0].children]
                            for line in children:
                                if "channel-group" in line:
                                    if "mode on" in line:
                                        detected_protocol = "Static"
                                    elif any(mode in line for mode in ["mode auto", "mode desirable", "mode desirable non-silent"]):
                                        detected_protocol = "PAgP"
                                    elif any(mode in line for mode in ["mode active", "mode passive"]):
                                        detected_protocol = "LACP"
                                    break

                        print(f"[INFO] {device} - {port_channel} detected protocol: {detected_protocol}")

                        # Compare detected protocol with expected protocol
                        if detected_protocol != expected_protocol:
                            print(f"[WARNING] {device} - {port_channel} missing or incorrect protocol (Expected: {expected_protocol}, Detected: {detected_protocol}).")
                            comments.append(f"{device} {port_channel} missing or incorrect protocol (Expected: {expected_protocol})")
                            grade -= points_distribution["etherchannels"] / len(etherchannel_interfaces[device])
                        else:
                            print(f"[INFO] {device} - {port_channel} protocol is correctly configured as {detected_protocol}.")

                # Task 2.9: Validate SVIs
                print(f"[INFO] Validating SVIs for {device}...")

                # Award points if the SVIs exist for the switch
                for svi in svi_interfaces:
                    svi_obj = submission.find_objects(rf"^interface {svi}")
                    if not svi_obj:
                        print(f"[WARNING] {device} - Missing SVI {svi}.")
                        comments.append(f"{device} Missing SVI {svi}")
                        grade -= points_distribution["svis"] / len(svi_interfaces)
                    else:
                        print(f"[INFO] {device} - SVI {svi} exists. Awarding marks.")

            except Exception as e:
                print(f"[ERROR] {device}: Failed to parse configuration - {e}")
                comments.append(f"{device} Parse error")

        grade = max(0, grade)
        return {"grade": grade, "comments": " | ".join(comments)}

    def grade_task_3(self, device_files, group_number):
        """
        Grades Task 3: Configure Spanning Tree.
        Validates root bridge priorities, port costs, and other spanning tree configurations.
        """
        comments = []
        grade = 9.0  # Total points for Task 3

        # Define switches and exclude routers
        switch_devices = ["TOR-D1", "TOR-D2", "TOR-A1", "TOR-A2"]

        # Dynamic VLAN IDs based on group number
        vlan_2xx = group_number + 200
        vlan_3xx = group_number + 300

        # Iterate through detected files for switch devices
        for device, filepath in device_files.items():
            if device not in switch_devices:
                print(f"[INFO] Skipping {device}: Task 3 does not apply to routers.")
                continue

            print(f"[INFO] Grading file: {filepath}")
            try:
                submission = CiscoConfParse(filepath)

                # Task 3.1: Validate Root Bridge Configuration
                if device in ["TOR-D1", "TOR-D2"]:
                    print(f"[INFO] Validating root bridge priorities for {device}...")
                    
                    # Calculate dynamic VLAN IDs
                    vlan_2xx = 200 + group_number
                    vlan_3xx = 300 + group_number

                    def get_priority(vlan):
                        """Fetches priority for a specific VLAN."""
                        priority_obj = submission.find_objects(rf"^spanning-tree vlan {vlan}(?:,\d+)? priority")  # Support commas in the line
                        if priority_obj:
                            priority = int(priority_obj[0].text.split()[-1])  # Fetch the last value, which is the priority
                            print(f"[INFO] {device} - VLAN {vlan} priority: {priority}")
                            return priority
                        else:
                            print(f"[WARNING] {device} - VLAN {vlan} priority not found.")
                            return None

                    # Fetch priorities for relevant VLANs
                    vlan_10_priority = get_priority(10)
                    vlan_3xx_priority = vlan_10_priority if vlan_10_priority is not None else get_priority(vlan_3xx)  # Align VLAN 3xx priority with VLAN 10
                    vlan_2xx_priority = get_priority(vlan_2xx)  # Dynamic group number for VLAN 2xx

                    # Validate TOR-D1 priorities
                    if device == "TOR-D1":
                        if vlan_10_priority and vlan_3xx_priority and vlan_2xx_priority and vlan_10_priority < vlan_2xx_priority and vlan_3xx_priority < vlan_2xx_priority:
                            print(f"[INFO] {device} - VLAN 10 and 3xx priorities ({vlan_10_priority}, {vlan_3xx_priority}) are lower than VLAN 2xx ({vlan_2xx_priority}).")
                        else:
                            print(f"[WARNING] {device} - VLAN 10 or 3xx priority is not lower than VLAN 2xx.")
                            comments.append(f"{device} Incorrect priority relationship for VLAN 10/3xx vs 2xx")
                            grade -= 1.0 / 2.0 # Deduct 1 point for each incorrect priority

                    # Validate TOR-D2 priorities
                    if device == "TOR-D2":
                        if vlan_2xx_priority and vlan_10_priority and vlan_3xx_priority and vlan_2xx_priority < vlan_10_priority and vlan_2xx_priority < vlan_3xx_priority:
                            print(f"[INFO] {device} - VLAN 2xx priority ({vlan_2xx_priority}) is lower than VLAN 10 and 3xx ({vlan_10_priority}, {vlan_3xx_priority}).")
                        else:
                            print(f"[WARNING] {device} - VLAN 2xx priority is not lower than VLAN 10 or 3xx.")
                            comments.append(f"{device} Incorrect priority relationship for VLAN 2xx vs 10/3xx")
                            grade -= 1.0 / 2.0 # Deduct 1 point for each incorrect priority

                # Task 3.2: Validate Spanning Tree Port Costs
                if device == "TOR-A1":
                    print(f"[INFO] Validating spanning-tree port costs on {device}...")

                    # Locate Port-channel2 interface
                    po2_interface = submission.find_objects(r"^interface Port-channel2")
                    if po2_interface:
                        po2_children = [child.text.strip() for child in po2_interface[0].children]
                        print(f"[DEBUG] {device} Port-channel2 Children: {po2_children}")

                        # Dynamically calculate expected cost
                        expected_cost = (2 * group_number) + 10
                        cost_detected = False

                        # Check for any 'spanning-tree vlan <vlan_id> cost <value>' command
                        for line in po2_children:
                            match = re.search(r"spanning-tree(?: vlan \d+)? cost (\d+)", line)
                            if match:
                                actual_cost = int(match.group(1))
                                if actual_cost == expected_cost:
                                    print(f"[INFO] {device} - Port-channel2 cost is correctly set to {expected_cost}.")
                                    cost_detected = True
                                    break
                                else:
                                    print(f"[WARNING] {device} - Port-channel2 cost exists but is set to {actual_cost} instead of {expected_cost}.")
                                    comments.append(f"{device} Incorrect spanning-tree cost (Expected: {expected_cost}, Found: {actual_cost})")
                                    grade -= 1.0
                                    cost_detected = True
                                    break
                        
                        # If no cost command is found
                        if not cost_detected:
                            print(f"[WARNING] {device} - Port-channel2 cost command is missing.")
                            comments.append(f"{device} Missing spanning-tree cost command")
                            grade -= 1.0

                # Task 3.3: Validate PortFast and BPDU Guard
                if device in ["TOR-A1", "TOR-A2"]:
                    print(f"[INFO] Validating PortFast and BPDU Guard on access ports for {device}...")
                    access_ports = [f"GigabitEthernet1/0/{i}" for i in range(12, 25)]
                    for port in access_ports:
                        port_obj = submission.find_objects(rf"^interface {port}")
                        if not port_obj:
                            print(f"[WARNING] {device} - Access port {port} is missing.")
                            comments.append(f"{device} Missing configuration for access port {port}")
                            grade -= 2.0 / len(access_ports) 
                            continue

                        children = [child.text.strip() for child in port_obj[0].children]
                        if "spanning-tree portfast" not in children:
                            print(f"[WARNING] {device} - PortFast is not enabled on {port}.")
                            comments.append(f"{device} PortFast not enabled on {port}")
                            grade -= 1.0 / len(access_ports)
                        if "spanning-tree bpduguard enable" not in children:
                            print(f"[WARNING] {device} - BPDU Guard is not enabled on {port}.")
                            comments.append(f"{device} BPDU Guard not enabled on {port}")
                            grade -= 1.0 / len(access_ports)

                # Task 3.4: Validate Root Guard
                if device in ["TOR-D1", "TOR-D2"]:
                    print(f"[INFO] Validating Root Guard configuration on {device}...")
                    root_guard_ports = ["GigabitEthernet1/0/5", "GigabitEthernet1/0/6"]
                    for port in root_guard_ports:
                        port_obj = submission.find_objects(rf"^interface {port}")
                        if not port_obj:
                            print(f"[WARNING] {device} - Root Guard port {port} is missing.")
                            comments.append(f"{device} Missing Root Guard port {port}")
                            grade -= 2.0 / len(root_guard_ports)
                            continue

                        children = [child.text.strip() for child in port_obj[0].children]
                        if "spanning-tree guard root" not in children:
                            print(f"[WARNING] {device} - Root Guard is not enabled on {port}.")
                            comments.append(f"{device} Root Guard not enabled on {port}")
                            grade -= 2.0 / len(root_guard_ports)

            except Exception as e:
                print(f"[ERROR] {device}: Failed to parse configuration - {e}")
                comments.append(f"{device} Parse error")

        # Final Grade
        grade = max(0, grade)  # Ensure grade does not go below 0
        return {"grade": grade, "comments": " | ".join(comments)}

    def grade_task_4(self, device_files, group_number):
        """
        Grades Task 4: Configure First Hop Redundancy.
        Validates HSRPv2, primary gateways, preemption, virtual IPs, object tracking, and default gateway configuration.
        """
        comments = []
        grade = 17.0  # Total points for Task 4 based on rubric

        # Calculate dynamic VLAN numbers and HSRP group numbers
        vlan_2xx = 200 + group_number
        vlan_3xx = 300 + group_number
        hsrp_group_10 = (2 * group_number) + 10
        hsrp_group_2xx = (2 * group_number) + vlan_2xx
        hsrp_group_3xx = (2 * group_number) + vlan_3xx

        # Iterate through device files
        for device, filepath in device_files.items():
            if device not in ["TOR-D1", "TOR-D2", "TOR-A1", "TOR-A2"]:
                print(f"[INFO] Skipping {device}: Task 4 does not apply.")
                continue

            print(f"[INFO] Grading file: {filepath}")
            try:
                submission = CiscoConfParse(filepath)

                # Validation logic for TOR-D1 and TOR-D2
                if device in ["TOR-D1", "TOR-D2"]:
                    print(f"[INFO] Validating HSRPv2 configuration on {device}...")
                    
                    # Define VLANs and HSRP groups for TOR-D1 and TOR-D2
                    vlans = [10, vlan_2xx, vlan_3xx]
                    hsrp_groups = [hsrp_group_10, hsrp_group_2xx, hsrp_group_3xx]
                    priorities = {}

                    for vlan, group in zip(vlans, hsrp_groups):
                        vlan_interface = submission.find_objects(rf"^interface Vlan{vlan}")
                        if not vlan_interface:
                            print(f"[WARNING] {device} - Missing interface Vlan{vlan} for HSRP.")
                            comments.append(f"{device} Missing interface Vlan{vlan}")
                            continue

                        children = [child.text.strip() for child in vlan_interface[0].children]

                        # Validate HSRPv2
                        if f"standby version 2" not in children:
                            print(f"[WARNING] {device} - HSRPv2 not enabled for VLAN {vlan}.")
                            comments.append(f"{device} Missing HSRPv2 for VLAN {vlan}")
                            grade -= 0.5

                        # Validate HSRP group number
                        if f"standby {group} " not in " ".join(children):
                            print(f"[WARNING] {device} - Incorrect HSRP group for VLAN {vlan}.")
                            comments.append(f"{device} Incorrect HSRP group for VLAN {vlan}")
                            grade -= 0.5

                        # Extract priority
                        priority_line = [line for line in children if f"standby {group} priority" in line]
                        if priority_line:
                            priorities[vlan] = int(priority_line[0].split()[-1])
                        else:
                            print(f"[WARNING] {device} - Priority configuration missing for VLAN {vlan}.")
                            priorities[vlan] = 100  # Assume default priority for missing priorities

                    # Primary Gateway Validation
                    if device == "TOR-D1":
                        if priorities.get(10) and priorities.get(vlan_3xx) and priorities.get(vlan_2xx):
                            if priorities[10] <= priorities[vlan_2xx]:
                                print(f"[WARNING] {device} - Priority for VLAN 10 is not higher than VLAN 2xx.")
                                comments.append(f"{device} Priority for VLAN 10 not higher than VLAN 2xx")
                                grade -= 0.75
                            if priorities[vlan_3xx] <= priorities[vlan_2xx]:
                                print(f"[WARNING] {device} - Priority for VLAN 3xx is not higher than VLAN 2xx.")
                                comments.append(f"{device} Priority for VLAN 3xx not higher than VLAN 2xx")
                                grade -= 0.75

                    if device == "TOR-D2":
                        if priorities.get(10) and priorities.get(vlan_3xx) and priorities.get(vlan_2xx):
                            if priorities[vlan_2xx] <= priorities[10]:
                                print(f"[WARNING] {device} - Priority for VLAN 2xx is not higher than VLAN 10.")
                                comments.append(f"{device} Priority for VLAN 2xx not higher than VLAN 10")
                                grade -= 0.75
                            if priorities[vlan_2xx] <= priorities[vlan_3xx]:
                                print(f"[WARNING] {device} - Priority for VLAN 2xx is not higher than VLAN 3xx.")
                                comments.append(f"{device} Priority for VLAN 2xx not higher than VLAN 3xx")
                                grade -= 0.75

                    # Preemption Validation
                    for vlan, group in zip(vlans, hsrp_groups):
                        vlan_interface = submission.find_objects(rf"^interface Vlan{vlan}")
                        if vlan_interface:
                            children = [child.text.strip() for child in vlan_interface[0].children]
                            if f"standby {group} preempt" not in " ".join(children):
                                print(f"[WARNING] {device} - Preemption not enabled for VLAN {vlan}.")
                                comments.append(f"{device} Missing preemption for VLAN {vlan}")
                                grade -= 1.5 / len(vlans)

                    # Virtual IP Validation
                    for vlan, group in zip(vlans, hsrp_groups):
                        vlan_interface = submission.find_objects(rf"^interface Vlan{vlan}")
                        if vlan_interface:
                            children = [child.text.strip() for child in vlan_interface[0].children]
                            if f"standby {group} ip" not in " ".join(children):
                                print(f"[WARNING] {device} - Virtual IP missing for VLAN {vlan}.")
                                comments.append(f"{device} Missing virtual IP for VLAN {vlan}")
                                grade -= 1.0 / len(vlans)

                    # Object Tracking Validation for TOR-D2
                    if device == "TOR-D2":
                        vlan_interface = submission.find_objects(rf"^interface Vlan{vlan_2xx}")
                        if vlan_interface:
                            children = [child.text.strip() for child in vlan_interface[0].children]

                            # Validate standby tracking configuration
                            if f"standby {hsrp_group_2xx} track {hsrp_group_2xx}" not in " ".join(children):
                                print(f"[WARNING] {device} - Object tracking not configured for VLAN {vlan_2xx}.")
                                comments.append(f"{device} Missing object tracking for VLAN {vlan_2xx}")
                                grade -= 1.0

                            # Validate decrement tracking for Port-channel2
                            if "decrement" not in " ".join(children):
                                print(f"[WARNING] {device} - Missing decrement tracking for VLAN {vlan_2xx}.")
                                comments.append(f"{device} Missing decrement tracking for VLAN {vlan_2xx}")
                                grade -= 1.0

                # Default Gateway Validation for TOR-A1 and TOR-A2
                if device in ["TOR-A1", "TOR-A2"]:
                    print(f"[INFO] Validating default gateway configuration on {device}...")
                    default_gateway_obj = submission.find_objects(r"^ip default-gateway")
                    expected_gateway = f"172.16.{group_number}.254"
                    if not default_gateway_obj or expected_gateway not in default_gateway_obj[0].text:
                        print(f"[WARNING] {device} - Default gateway not configured correctly for VLAN 10.")
                        grade -= 1.0
                        comments.append(f"{device} Missing default gateway for VLAN 10")

            except Exception as e:
                print(f"[ERROR] {device}: Failed to parse configuration - {e}")
                comments.append(f"{device} Parse error")

        # Final Grade
        grade = max(0, grade)  # Ensure grade doesn't go below 0
        return {"grade": grade, "comments": " | ".join(comments)}

    def grade_task_5(self, device_files, group_number):
        """
        Grades Task 5: Configure MPLS.
        Validates MPLS on specific links, label protocol, and LDP router ID configuration.
        """
        comments = []
        grade = 10.0  # Total points for Task 5

        # Interface mapping for MPLS links
        interfaces = {
            "Toronto": "GigabitEthernet0/0/0",
            "ISP_Toronto": "GigabitEthernet0/0/0",
            "Ottawa": "GigabitEthernet0/0/0",
            "ISP_Ottawa": "GigabitEthernet0/0/1"
        }

        # Check devices
        for device, filepath in device_files.items():
            if device not in ["Toronto", "ISP", "Ottawa"]:
                print(f"[INFO] Skipping {device}: Task 5 does not apply.")
                continue

            print(f"[INFO] Grading file: {filepath}")
            try:
                submission = CiscoConfParse(filepath)

                # Validate MPLS on specific interfaces
                if device in ["Toronto", "ISP", "Ottawa"]:
                    print(f"[INFO] Validating MPLS configuration on {device}...")
                    if device == "ISP":
                        isp_interfaces = [interfaces["ISP_Toronto"], interfaces["ISP_Ottawa"]]
                        print(f"[DEBUG] Validating ISP interfaces: {isp_interfaces}")
                        for interface in isp_interfaces:
                            print(f"[DEBUG] Checking interface: {interface}")
                            interface_obj = submission.find_objects(rf"^interface {interface}")
                            if not interface_obj:
                                print(f"[WARNING] {device} - Interface {interface} not found.")
                                comments.append(f"{device} Missing interface {interface}")
                                continue
                            children = [child.text.strip() for child in interface_obj[0].children]
                            if "mpls ip" not in children:
                                print(f"[WARNING] {device} - MPLS not enabled on {interface}.")
                                comments.append(f"{device} MPLS missing on {interface}")
                            if "mpls label protocol ldp" not in children:
                                print(f"[WARNING] {device} - MPLS label protocol LDP not configured on {interface}.")
                                comments.append(f"{device} Missing label protocol LDP on {interface}")
                                grade -= 1.0
                    else:
                        interface = interfaces[device]
                        interface_obj = submission.find_objects(rf"^interface {interface}")
                        if not interface_obj:
                            print(f"[WARNING] {device} - Interface {interface} not found.")
                            comments.append(f"{device} Missing interface {interface}")
                            continue
                        children = [child.text.strip() for child in interface_obj[0].children]
                        if "mpls ip" not in children:
                            print(f"[WARNING] {device} - MPLS not enabled on {interface}.")
                            comments.append(f"{device} MPLS missing on {interface}")
                            grade -= 1.0  # Deduct 1 point for missing MPLS
                        if "mpls label protocol ldp" not in children:
                                print(f"[WARNING] {device} - MPLS label protocol LDP not configured on {interface}.")
                                comments.append(f"{device} Missing label protocol LDP on {interface}")
                                grade -= 1.0

                # Validate LDP Router ID
                print(f"[INFO] Validating LDP Router ID configuration on {device}...")
                if not submission.find_objects(r"^mpls ldp router-id Loopback1"):
                    print(f"[WARNING] {device} - LDP Router ID not set to Loopback1.")
                    comments.append(f"{device} Missing LDP Router ID configuration")
                    grade -= 1.0   # Deduct 1 point if LDP Router ID is missing or incorrect

            except Exception as e:
                print(f"[ERROR] {device}: Failed to parse configuration - {e}")
                comments.append(f"{device} Parse error")

        # Final Grade
        grade = max(0, grade)  # Ensure grade does not go below 0
        return {"grade": grade, "comments": " | ".join(comments)}

    def grade_task_6(self, device_files, group_number):
        """
        Grades Task 6: Configure DMVPN Phase 3.
        Validates tunnel interfaces, NHRP, and IPsec configurations. Confirms VRF-INET exists on D2.
        Includes debug print statements for all detected configurations.
        """
        comments = []
        grade = 38.0  # Total points for Task 6

        # Devices restricted to Toronto, Ottawa, and Oshawa
        valid_devices = ["Toronto", "Ottawa", "Oshawa", "TOR-D2"]

        # Internet-facing interfaces and their IP addresses
        internet_interfaces = {
            "Toronto": {"interface": "GigabitEthernet0/0/1.100", "ip": f"199.212.32.{group_number}"},
            "Ottawa": {"interface": "GigabitEthernet0/0/1", "ip": f"209.165.200.{group_number}"},
            "Oshawa": {"interface": "GigabitEthernet0/0/1", "ip": f"198.51.100.{group_number}"}
        }

        # Tunnel IP addresses based on group number
        tunnel_ips = {
            "Toronto": f"10.1.{group_number}.1",
            "Ottawa": f"10.1.{group_number}.2",
            "Oshawa": f"10.1.{group_number}.3"
        }

        internet_ips = {
            "Toronto": f"199.212.32.{group_number}",
            "Ottawa": f"209.165.200.{group_number}",
            "Oshawa": f"198.51.100.{group_number}"
        }

        # Check each device
        for device, filepath in device_files.items():
            if device not in valid_devices:
                print(f"[INFO] Skipping {device}: Task 6 does not apply.")
                continue

            print(f"[INFO] Grading file: {filepath}")
            try:
                submission = CiscoConfParse(filepath)

                # validate VRF configuration on TOR-D2
                if device == "TOR-D2":
                    print(f"[INFO] Validating VRF configuration on {device}...")

                    # Check for 'vrf definition INET'
                    vrf_detected = submission.find_objects(r"^vrf definition INET")
                    print(f"[DEBUG] {device} VRF Definition INET Detected: {bool(vrf_detected)}")
                    if not vrf_detected:
                        print(f"[WARNING] {device} - VRF definition INET not found.")
                        comments.append(f"{device} Missing VRF definition INET")
                        grade -= 2.0
                    else:
                        print(f"[INFO] {device} - VRF definition INET exists.")

                    # Check for 'vrf forwarding INET' on specific VLAN interfaces
                    for vlan in ["Vlan100", "Vlan300", "Vlan400"]:
                        vlan_interface = submission.find_objects(rf"^interface {vlan}")
                        print(f"[DEBUG] {device} {vlan} Interface Detected: {bool(vlan_interface)}")
                        if vlan_interface:
                            children = [child.text.strip() for child in vlan_interface[0].children]
                            print(f"[DEBUG] {device} {vlan} Children: {children}")
                            if "vrf forwarding INET" not in children:
                                print(f"[WARNING] {device} - {vlan} missing 'vrf forwarding INET'.")
                                comments.append(f"{device} {vlan} missing 'vrf forwarding INET'")
                                grade -= 1.0
                            else:
                                print(f"[INFO] {device} - 'vrf forwarding INET' configured on {vlan}.")
                        else:
                            print(f"[WARNING] {device} - Interface {vlan} not found.")
                            comments.append(f"{device} Missing interface {vlan}")
                            grade -= 1.0

                # Skip Tunnel1-related checks for TOR-D2
                elif device in ["Toronto", "Ottawa", "Oshawa"]:
                    
                    # Tunnel Interface Validation
                    print(f"[INFO] Validating Tunnel1 configuration on {device}...")
                    tunnel_interface = submission.find_objects(r"^interface Tunnel1")
                    if not tunnel_interface:
                        print(f"[WARNING] {device} - Tunnel1 interface not found.")
                        comments.append(f"{device} Missing Tunnel1 interface")
                        continue

                    children = [child.text.strip() for child in tunnel_interface[0].children]
                    print(f"[DEBUG] {device} Tunnel1 Children: {children}")

                    # Check multipoint GRE
                    if "tunnel mode gre multipoint" not in children:
                        print(f"[WARNING] {device} - Multipoint GRE not configured on Tunnel1.")
                        comments.append(f"{device} Missing multipoint GRE")
                        grade -= 0.5

                    # Check tunnel source
                    expected_source_interface = internet_interfaces[device]["interface"]
                    expected_source_ip = internet_interfaces[device]["ip"]
                    tunnel_source_detected = any(
                        f"tunnel source {value}" in children
                        for value in [expected_source_interface, expected_source_ip]
                    )
                    print(f"[DEBUG] {device} Tunnel Source Detected: {tunnel_source_detected}")
                    if not tunnel_source_detected:
                        print(f"[WARNING] {device} - Tunnel source not correctly configured.")
                        comments.append(f"{device} Incorrect tunnel source")
                        grade -= 0.5

                    # Check tunnel key
                    expected_key = 3 * group_number
                    tunnel_key_detected = f"tunnel key {expected_key}" in children
                    print(f"[DEBUG] {device} Tunnel Key Detected: {tunnel_key_detected}")
                    if not tunnel_key_detected:
                        print(f"[WARNING] {device} - Tunnel key not correctly configured.")
                        comments.append(f"{device} Incorrect tunnel key")
                        grade -= 0.5

                    # Check Tunnel IP address
                    expected_ip = tunnel_ips[device]
                    ip_address_detected = any(
                        f"ip address {expected_ip}" in line for line in children
                    )
                    print(f"[DEBUG] {device} Tunnel IP Address Detected: {ip_address_detected}")
                    if not ip_address_detected:
                        print(f"[WARNING] {device} - Tunnel IP address not correctly configured.")
                        comments.append(f"{device} Incorrect Tunnel IP address")
                        grade -= 0.5

                    # Check bandwidth and delay
                    bandwidth_detected = "bandwidth 1000000" in children
                    print(f"[DEBUG] {device} Bandwidth Detected: {bandwidth_detected}")
                    if not bandwidth_detected:
                        print(f"[WARNING] {device} - Bandwidth not correctly configured.")
                        comments.append(f"{device} Missing bandwidth setting")
                        grade -= 0.5
                    expected_delay = 2 * group_number + 20
                    delay_detected = f"delay {expected_delay}" in children
                    print(f"[DEBUG] {device} Delay Detected: {delay_detected}")
                    if not delay_detected:
                        print(f"[WARNING] {device} - Delay not correctly configured.")
                        comments.append(f"{device} Missing delay setting")
                        grade -= 0.5

                    # NHRP Validation
                    print(f"[INFO] Validating NHRP configuration on {device}...")
                    nhrp_network_detected = f"ip nhrp network-id {group_number}" in children
                    print(f"[DEBUG] {device} NHRP Network-ID Detected: {nhrp_network_detected}")
                    if not nhrp_network_detected:
                        print(f"[WARNING] {device} - NHRP network ID not correctly configured.")
                        comments.append(f"{device} Missing NHRP network ID")
                        grade -= 0.5

                    nhrp_authentication_detected = any(
                        "ip nhrp authentication" in line for line in children
                    )
                    print(f"[DEBUG] {device} NHRP Authentication Detected: {nhrp_authentication_detected}")
                    if not nhrp_authentication_detected:
                        print(f"[WARNING] {device} - NHRP authentication not configured.")
                        comments.append(f"{device} Missing NHRP authentication")
                        grade -= 0.5

                    # Check for 'ip nhrp redirect' in Toronto
                    if device == "Toronto":
                        nhrp_redirect_detected = any(
                            "ip nhrp redirect" in line for line in children
                        )
                        print(f"[DEBUG] {device} NHRP Redirect Detected: {nhrp_redirect_detected}")
                        if not nhrp_redirect_detected:
                            print(f"[WARNING] {device} - NHRP redirect not configured.")
                            comments.append(f"{device} Missing NHRP redirect")
                            grade -= 1.0

                    # check for ip nhrp nhs on Ottawa and Oshawa, set to Toronto's tunnel IP
                    if device in ["Ottawa", "Oshawa"]:
                        nhrp_nhs_detected = any(
                            f"ip nhrp nhs {tunnel_ips['Toronto']}" in line for line in children
                        )
                        print(f"[DEBUG] {device} NHRP NHS Detected: {nhrp_nhs_detected}")
                        if not nhrp_nhs_detected:
                            print(f"[WARNING] {device} - NHRP NHS not configured to Toronto's tunnel IP.")
                            comments.append(f"{device} Incorrect NHRP NHS configuration")
                            grade -= 1.0

                    # check for static mapping of toronto's tunnel IP to its public IP on Ottawa and Oshawa
                    if device in ["Ottawa", "Oshawa"]:
                        nhrp_static_mapping_detected = any(
                            f"ip nhrp map {tunnel_ips['Toronto']} {internet_ips['Toronto']}" in line for line in children
                        )
                        print(f"[DEBUG] {device} NHRP Static Mapping Detected: {nhrp_static_mapping_detected}")
                        if not nhrp_static_mapping_detected:
                            print(f"[WARNING] {device} - NHRP static mapping not configured for Toronto's tunnel IP.")
                            comments.append(f"{device} Missing NHRP static mapping for Toronto's tunnel IP")
                            grade -= 1.0

                    # check for static mapping of multicast to toronto's tunnel IP on Ottawa and Oshawa
                    if device in ["Ottawa", "Oshawa"]:
                        nhrp_multicast_mapping_detected = any(
                            f"ip nhrp map multicast {internet_ips['Toronto']}" in line for line in children
                        )
                        print(f"[DEBUG] {device} NHRP Multicast Mapping Detected: {nhrp_multicast_mapping_detected}")
                        if not nhrp_multicast_mapping_detected:
                            print(f"[WARNING] {device} - NHRP multicast mapping not configured for Toronto's tunnel IP.")
                            comments.append(f"{device} Missing NHRP multicast mapping for Toronto's tunnel IP")
                            grade -= 1.0

                    # IPSec Validation
                    print(f"[INFO] Validating IPSec configuration on {device}...")

                    # 1. Validate ISAKMP Key
                    isakmp_detected = submission.find_objects(r"crypto isakmp key .* address 0.0.0.0")
                    print(f"[DEBUG] {device} ISAKMP Key Detected: {isakmp_detected}")
                    if not isakmp_detected:
                        print(f"[WARNING] {device} - ISAKMP key not correctly configured.")
                        comments.append(f"{device} Missing ISAKMP key")
                        grade -= 0.5

                    # 2. Validate IKE Policy and Child Commands
                    ike_policy_obj = submission.find_objects(rf"^crypto isakmp policy {group_number}")
                    print(f"[DEBUG] {device} IKE Policy Detected: {ike_policy_obj}")
                    if not ike_policy_obj:
                        print(f"[WARNING] {device} - IKE policy {group_number} not found.")
                        comments.append(f"{device} Missing IKE policy {group_number}")
                        grade -= 0.5
                    else:
                        ike_policy_children = [child.text.strip() for child in ike_policy_obj[0].children]
                        print(f"[DEBUG] {device} IKE Policy Children: {ike_policy_children}")
                        for setting in ["sha512", "aes 256", "pre-share", "group 14"]:
                            if setting not in " ".join(ike_policy_children):
                                print(f"[WARNING] {device} - IKE policy missing required attribute: {setting}.")
                                comments.append(f"{device} Incorrect IKE policy {setting}")
                                grade -= 1.5

                    # 3. Validate IPSec Transform Set
                    transform_set_obj = submission.find_objects(r"^crypto ipsec transform-set .*_TRANS")
                    print(f"[DEBUG] {device} IPSec Transform Set Detected: {transform_set_obj}")
                    if not transform_set_obj:
                        print(f"[WARNING] {device} - IPSec transform set not correctly configured.")
                        comments.append(f"{device} Missing IPSec transform set")
                        grade -= 0.5
                    else:
                        # Parse the parent line for encryption and hash
                        transform_set_line = transform_set_obj[0].text.strip()
                        print(f"[DEBUG] {device} Transform Set Parent Line: {transform_set_line}")
                        if "esp-aes 256" not in transform_set_line:
                            print(f"[WARNING] {device} - IPSec transform set missing encryption esp-aes 256.")
                            comments.append(f"{device} Incorrect IPSec transform set encryption")
                            grade -= 0.5
                        if "esp-sha512-hmac" not in transform_set_line:
                            print(f"[WARNING] {device} - IPSec transform set missing hash esp-sha512-hmac.")
                            comments.append(f"{device} Incorrect IPSec transform set hash")
                            grade -= 0.5

                        # Parse child lines for mode transport
                        transform_set_children = [child.text.strip() for child in transform_set_obj[0].children]
                        print(f"[DEBUG] {device} Transform Set Children: {transform_set_children}")
                        if "mode transport" not in transform_set_children:
                            print(f"[WARNING] {device} - IPSec transform set missing mode transport.")
                            comments.append(f"{device} Incorrect IPSec transform set mode")
                            grade -= 0.5

                    # 4. Validate IPSec Profile
                    profile_obj = submission.find_objects(r"^crypto ipsec profile .*_PROFILE")
                    print(f"[DEBUG] {device} IPSec Profile Detected: {profile_obj}")
                    if not profile_obj:
                        print(f"[WARNING] {device} - IPSec profile not correctly configured.")
                        comments.append(f"{device} Missing IPSec profile")
                        grade -= 0.5
                    else:
                        profile_children = [child.text.strip() for child in profile_obj[0].children]
                        print(f"[DEBUG] {device} IPSec Profile Children: {profile_children}")
                        if f"set transform-set" not in " ".join(profile_children):
                            print(f"[WARNING] {device} - IPSec profile does not reference correct transform set.")
                            comments.append(f"{device} Missing IPSec profile transform-set reference")
                            grade -= 0.5

                    # 5. Check if IPSec Profile Applied to Tunnel1
                    tunnel_interface = submission.find_objects(r"^interface Tunnel1")
                    children = [child.text.strip() for child in tunnel_interface[0].children]
                    print(f"[DEBUG] {device} Tunnel1 Children: {children}")
                    profile_applied = f"tunnel protection ipsec profile" in " ".join(children)
                    print(f"[DEBUG] {device} Tunnel Protection Applied: {profile_applied}")
                    if not profile_applied:
                        print(f"[WARNING] {device} - Tunnel protection not correctly configured.")
                        comments.append(f"{device} Missing tunnel protection for IPSec profile")
                        grade -= 0.5

            except Exception as e:
                print(f"[ERROR] {device}: Failed to parse configuration - {e}")
                comments.append(f"{device} Parse error")

        # Final Grade
        grade = max(0, grade)  # Ensure grade doesn't go below 0
        return {"grade": grade, "comments": " | ".join(comments)}

    def grade_task_7(self, device_files, group_number):
        """
        Grades Task 7: Configure Routing.
        Dynamically parses EIGRP address-family ipv4 for network commands and router ID validation.
        Excludes EIGRP checks for TOR-D1 and TOR-D2, validating only static routes for these devices.
        """
        comments = []
        grade = 18.0  # Total points for Task 7

        # Devices restricted to Toronto, ISP, Ottawa, Oshawa, TOR-D1, and TOR-D2
        valid_devices = ["Toronto", "ISP", "Ottawa", "Oshawa", "TOR-D1", "TOR-D2"]

        # Router IDs
        router_ids = {
            "Toronto": "1.1.1.1",
            "ISP": "2.2.2.2",
            "Ottawa": "3.3.3.3",
            "Oshawa": "4.4.4.4"
        }

        # Forbidden Internet/Underlay Networks
        forbidden_networks = {
            "Toronto": "199.212.32.xx",
            "Ottawa": "209.165.200.xx",
            "Oshawa": "198.51.100.xx"
        }

        # Required network prefixes
        tunnel_prefixes = {
            "Toronto": ["10.1.xx.0"],
            "Ottawa": ["10.1.xx.0"],
            "Oshawa": ["10.1.xx.0"]
        }

        mpls_prefixes = {
            "Toronto": ["10.202.10.0"],
            "ISP": ["10.202.10.0", "10.202.20.0"],
            "Ottawa": ["10.202.20.0"],
        }

        loopback_prefixes = {
            "Toronto": ["1.1.1.1"],
            "ISP": ["2.2.2.2"],
            "Ottawa": ["3.3.3.3", "172.16.84.0", "172.16.85.0", "172.16.86.0"],
            "Oshawa": ["4.4.4.4", "172.16.87.0", "172.16.88.0", "172.16.89.0"]
        }

        # Static routes for TOR-D1 and TOR-D2
        static_default_route = f"ip route 0.0.0.0 0.0.0.0 172.16.{group_number}.1"

        # Static route for Toronto
        toronto_static_route = f"ip route 172.16.0.0 255.255.0.0 172.16.{group_number}.254"

        # Regex for dynamic EIGRP process name
        eigrp_process_name = rf"OntarioTech0?{group_number}"

        # Check each device
        for device, filepath in device_files.items():
            if device not in valid_devices:
                print(f"[INFO] Skipping {device}: Task 7 does not apply.")
                continue

            print(f"[INFO] Grading file: {filepath}")
            try:
                submission = CiscoConfParse(filepath)

                # Static Routes Validation for TOR-D1 and TOR-D2
                if device in ["TOR-D1", "TOR-D2"]:
                    print(f"[INFO] Validating static default route on {device}...")
                    if static_default_route not in submission.ioscfg:
                        print(f"[WARNING] {device} - Missing static default route {static_default_route}.")
                        comments.append(f"{device} Missing static default route {static_default_route}")
                        grade -= 1.0
                    continue  # Skip EIGRP checks for TOR-D1 and TOR-D2

                # EIGRP Configuration Validation (Remaining Devices)
                print(f"[INFO] Validating EIGRP configuration on {device}...")
                eigrp_obj = submission.find_objects(rf"^router eigrp {eigrp_process_name}")
                print(f"[DEBUG] {device} EIGRP Process Detected: {eigrp_obj}")
                if not eigrp_obj:
                    print(f"[WARNING] {device} - EIGRP process {eigrp_process_name} not found.")
                    comments.append(f"{device} Missing or incorrect EIGRP process")
                    grade -= 0.5
                else:
                    # Address Family Validation
                    address_family_obj = eigrp_obj[0].re_search_children(rf"^ address-family ipv4 unicast autonomous-system {group_number}")
                    print(f"[DEBUG] {device} Address Family Detected: {address_family_obj}")
                    if not address_family_obj:
                        print(f"[WARNING] {device} - EIGRP address-family for AS {group_number} not found.")
                        comments.append(f"{device} Missing EIGRP address-family configuration")
                        grade -= 1.0
                    else:
                        # Parse all children of address-family ipv4
                        address_family_children = [child.text.strip() for child in address_family_obj[0].children]
                        print(f"[DEBUG] {device} Address Family Children: {address_family_children}")

                        # Network Prefix Validation
                        # check if toronto, ottawa, oshawa have network command for tunnel prefixes
                        if device in ["Toronto", "Ottawa", "Oshawa"]:
                            print(f"[INFO] Validating tunnel prefixes for {device}...")
                            for prefix in tunnel_prefixes[device]:
                                # Replace 'xx' with the group number in the prefix
                                formatted_prefix = prefix.replace("xx", str(group_number))
                                
                                # Regex to match the "network <prefix>" part, ignoring any masks
                                regex = rf"^network\s+{re.escape(formatted_prefix)}"
                                if not any(re.match(regex, line) for line in address_family_children):
                                    print(f"[WARNING] {device} - Missing network command for prefix {formatted_prefix}.")
                                    comments.append(f"{device} Missing network command for prefix {formatted_prefix}")
                                    grade -= 1.0

                        # check if toronto, isp, ottawa have network command for mpls prefixes
                        if device in ["Toronto", "ISP", "Ottawa"]:
                            print(f"[INFO] Validating MPLS prefixes for {device}...")
                            for prefix in mpls_prefixes[device]:
                                # Regex to match the "network <prefix>" part, ignoring any masks
                                regex = rf"^network\s+{re.escape(prefix)}"
                                if not any(re.match(regex, line) for line in address_family_children):
                                    print(f"[WARNING] {device} - Missing network command for prefix {prefix}.")
                                    comments.append(f"{device} Missing network command for prefix {prefix}")
                                    grade -= 1.0

                        # check if toronto, isp, ottawa, oshawa have network command for loopback prefixes
                        if device in ["Toronto", "ISP", "Ottawa", "Oshawa"]:
                            print(f"[INFO] Validating loopback prefixes for {device}...")
                            for prefix in loopback_prefixes[device]:
                                # Regex to match the "network <prefix>" part, ignoring any masks
                                regex = rf"^network\s+{re.escape(prefix)}"
                                if not any(re.match(regex, line) for line in address_family_children):
                                    print(f"[WARNING] {device} - Missing network command for prefix {prefix}.")
                                    comments.append(f"{device} Missing network command for prefix {prefix}")
                                    grade -= 0.5

                        # Forbidden Network Validation
                        forbidden_network = forbidden_networks.get(device, "").replace("xx", str(group_number))
                        if forbidden_network and forbidden_network in [child.split()[1] for child in address_family_children if child.startswith("network")]:
                            print(f"[WARNING] {device} - Forbidden network command found for prefix {forbidden_network}.")
                            comments.append(f"{device} Forbidden network command for prefix {forbidden_network}")
                            grade -= 1.0

                        # Router-ID Validation
                        if f"eigrp router-id {router_ids[device]}" not in address_family_children:
                            print(f"[WARNING] {device} - Router-ID {router_ids[device]} not configured under address-family ipv4.")
                            comments.append(f"{device} Missing Router-ID {router_ids[device]} under address-family ipv4")
                            grade -= 0.5

                    # Static Route Validation for Toronto
                    if device == "Toronto":
                        print(f"[INFO] Validating static route on Toronto...")
                        if toronto_static_route not in submission.ioscfg:
                            print(f"[WARNING] Toronto - Missing static route {toronto_static_route}.")
                            comments.append(f"Toronto Missing static route {toronto_static_route}")
                            grade -= 1.0

            except Exception as e:
                print(f"[ERROR] {device}: Failed to parse configuration - {e}")
                comments.append(f"{device} Parse error")

        # Final Grade
        grade = max(0, grade)  # Ensure grade doesn't go below 0
        return {"grade": grade, "comments": " | ".join(comments)}

    def grade_task_8(self, device_files):
        """
        Grades Task 8: Configure IP Services.
        Validates time zone, NTP server configuration, and time synchronization across devices.
        """
        comments = []
        grade = 12.5  # Total points for Task 8

        # NTP server IP addresses
        isp_loopback1_ip = "2.2.2.2"  # ISP's Loopback1 IP
        toronto_loopback1_ip = "1.1.1.1"  # Toronto's Loopback1 IP

        # Devices categorized by synchronization requirements
        ntp_synchronize_isp = ["Toronto", "Ottawa", "Oshawa"]
        ntp_synchronize_toronto = ["TOR-D1", "TOR-D2", "TOR-A1", "TOR-A2"]

        # Check each device
        for device, filepath in device_files.items():
            print(f"[INFO] Grading file: {filepath}")

            try:
                submission = CiscoConfParse(filepath)

                # 1. Time Zone and Daylight Savings Validation
                print(f"[INFO] Validating time zone settings on {device}...")
                timezone_detected = submission.find_objects(r"^clock timezone EST -5")  # Adjusted regex
                summertime_detected = submission.find_objects(r"^clock summer-time EDT recurring")
                print(f"[DEBUG] {device} Time Zone Detected: {bool(timezone_detected)}")
                print(f"[DEBUG] {device} Daylight Savings Detected: {bool(summertime_detected)}")

                if not timezone_detected:
                    print(f"[WARNING] {device} - Time zone not correctly configured.")
                    comments.append(f"{device} Missing or incorrect time zone configuration")
                    grade -= 0.5
                if not summertime_detected:
                    print(f"[WARNING] {device} - Daylight savings time not correctly configured.")
                    comments.append(f"{device} Missing or incorrect daylight savings time configuration")
                    grade -= 0.5

                # 2. ISP as Stratum 2 NTP Server
                if device == "ISP":
                    print(f"[INFO] Validating NTP server configuration on ISP...")
                    ntp_master_detected = submission.find_objects(r"^ntp master 2")
                    print(f"[DEBUG] ISP NTP Master Detected: {bool(ntp_master_detected)}")

                    if not ntp_master_detected:
                        print(f"[WARNING] ISP - NTP master configuration missing or incorrect.")
                        comments.append("ISP Missing or incorrect NTP master configuration")
                        grade -= 1.0

                # 3. Synchronization for Toronto, Ottawa, Oshawa
                if device in ntp_synchronize_isp:
                    print(f"[INFO] Validating NTP synchronization with ISP on {device}...")
                    ntp_server_detected = submission.find_objects(rf"^ntp server {isp_loopback1_ip}")
                    print(f"[DEBUG] {device} NTP Server ISP Detected: {bool(ntp_server_detected)}")

                    if not ntp_server_detected:
                        print(f"[WARNING] {device} - NTP synchronization with ISP missing or incorrect.")
                        comments.append(f"{device} Missing or incorrect NTP synchronization with ISP")
                        grade -= 0.5

                # 4. Synchronization for TOR-D1, TOR-D2, TOR-A1, TOR-A2
                if device in ntp_synchronize_toronto:
                    print(f"[INFO] Validating NTP synchronization with Toronto on {device}...")
                    ntp_server_detected = submission.find_objects(rf"^ntp server {toronto_loopback1_ip}")
                    print(f"[DEBUG] {device} NTP Server Toronto Detected: {bool(ntp_server_detected)}")

                    if not ntp_server_detected:
                        print(f"[WARNING] {device} - NTP synchronization with Toronto missing or incorrect.")
                        comments.append(f"{device} Missing or incorrect NTP synchronization with Toronto")
                        grade -= 0.5

            except Exception as e:
                print(f"[ERROR] {device}: Failed to parse configuration - {e}")
                comments.append(f"{device} Parse error")

        # Final Grade
        grade = max(0, grade)  # Ensure grade doesn't go below 0
        return {"grade": grade, "comments": " | ".join(comments)}

    def write_to_csv(self, group_name, task_name, grade, comments):
        """Writes group task grade and summary comments to CSV, task by task."""
        # Check if the file exists to write the header only once
        file_exists = os.path.isfile(self.output_csv)

        with open(self.output_csv, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Write the header row if this is the first write
            if not file_exists:
                csv_writer.writerow(["Group Name", "Task Name", "Grade", "Comments"])

            # Write the task details row
            csv_writer.writerow([group_name, task_name, grade, comments])

# Entry point of the program
if __name__ == "__main__":
    grader = CaseStudyGrader()
    grader.run()