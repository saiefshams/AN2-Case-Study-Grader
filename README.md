### **Task 1: Addressing**

| **Total Grade** | **Grading Criteria**                                                                                                  | **Deduction per Issue**                     |
|-----------------|----------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| **10 points**   | - Validate the presence of expected interfaces based on the device role.                                             | **0.1 point** for each missing interface    |
|                 | - Check that each interface is assigned the correct IP address and subnet mask.                                      | **0.1 point** for incorrect IP/mask         |

---

### **Task 2: Switch Configuration**

| **Total Grade** | **Grading Criteria**                                                                                                                                       | **Deduction per Issue**                  |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| **15 points**   | - Validate the presence and configuration of **trunk interfaces**.                                                                                        | **0.5 points** for each missing trunk interface |
|                 | - Check if trunk interfaces are set to mode `trunk`, have DTP disabled (`switchport nonegotiate`), and a native VLAN of `123`.                           | **0.5 points** for missing trunk mode<br> **0.2 points** for missing DTP disable<br> **0.2 points** for missing native VLAN configuration |
|                 | - Validate the presence and configuration of **EtherChannels** (Port-Channels) and their associated member interfaces.                                    | **1 point** for missing EtherChannel<br> **0.5 points** for missing member interface in EtherChannel |
|                 | - Verify the existence of **SVIs (Switched Virtual Interfaces)** and their IP address configurations.                                                     | **0.3 points** for missing SVI<br> **0.3 points** for missing SVI IP address |

---

### **Task 3: Configure Spanning Tree**

| **Total Grade** | **Grading Criteria**                                                                                                                                     | **Deduction per Issue**                         |
|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| **10 points**   | - Validate **root bridge priorities** for dynamic VLANs: VLAN 10, VLAN `2xx`, and VLAN `3xx`.                                                           | **0.5 points** for incorrect priority relationships |
|                 | - Check **spanning-tree port costs** for Port-channel2 on TOR-A1 for VLAN 10.                                                                          | **0.5 points** for missing or incorrect cost configuration |
|                 | - Verify **PortFast** and **BPDU Guard** on access ports (`GigabitEthernet1/0/12` to `GigabitEthernet1/0/24`) on TOR-A1 and TOR-A2.                     | **0.2 points** for missing port configuration<br>**0.1 points** for missing PortFast<br>**0.1 points** for missing BPDU Guard |
|                 | - Validate **Root Guard** configuration on TOR-D1 and TOR-D2 for designated ports (`GigabitEthernet1/0/5` and `GigabitEthernet1/0/6`).                 | **0.5 points** per missing Root Guard configuration or port |

---

### **Task 4: Configure First Hop Redundancy**

| **Total Grade** | **Grading Criteria**                                                                                                                                              | **Deduction per Issue**                             |
|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| **10 points**   | - Validate the presence of **HSRPv2** on VLANs 10, `2xx`, and `3xx` for TOR-D1 and TOR-D2.                                                                        | **0.5 points** for missing HSRPv2 per VLAN         |
|                 | - Verify **preemption** is enabled for each VLAN.                                                                                                                | **0.5 points** per missing preemption per VLAN     |
|                 | - Check **priority configuration** for each VLAN.                                                                                                                | **0.5 points** for missing or incorrect priority relationship |
|                 | - Validate the presence of **virtual IP addresses** for each VLAN.                                                                                               | **0.5 points** per missing virtual IP per VLAN     |
|                 | - Validate **object tracking** and **priority decrement** for TOR-D2 on VLAN `2xx`.                                                                              | **1.0 point** for missing object tracking<br>**0.5 points** for missing priority decrement |
|                 | - Verify **default gateway configuration** for TOR-A1 and TOR-A2.                                                                                                | **1.0 point** per missing or incorrect default gateway |

---

### **Task 5: Configure MPLS**

| **Total Grade** | **Grading Criteria**                                                                                                                   | **Deduction per Issue**                               |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------|
| **12 points**   | - Validate the presence of specific **MPLS-enabled interfaces** on Toronto, ISP, and Ottawa.                                           | **1.5 points** per missing interface                |
|                 | - Check that **MPLS is enabled** on the relevant interfaces (`mpls ip`).                                                              | **1.5 points** per interface without MPLS enabled    |
|                 | - Verify that the **MPLS label protocol** is set to LDP (`mpls label protocol ldp`) on the interfaces.                                 | **1.0 point** per interface missing LDP configuration |
|                 | - Check for the **LDP Router ID** configuration (`mpls ldp router-id Loopback1 force`).                                               | **1.0 point** per device missing LDP Router ID configuration |

---

### **Task 6: Configure DMVPN Phase 3**

| **Total Grade** | **Grading Criteria**                                                                                                                   | **Deduction per Issue**                                 |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| **20 points**   | - Validate **VRF configuration** for `TOR-D2`.                                                                                         | **2.0 points** for missing `vrf definition INET`       |
|                 | - Check `vrf forwarding INET` on VLANs `100`, `300`, and `400` for `TOR-D2`.                                                          | **1.0 point** for each missing configuration or interface |
|                 | - Validate **Tunnel1 interfaces** on Toronto, Ottawa, and Oshawa.                                                                     | **1.0 point** for missing Tunnel1 interface            |
|                 | - Confirm correct **multipoint GRE configuration** on Tunnel1 for Toronto, Ottawa, and Oshawa.                                        | **1.0 point** per device missing multipoint GRE configuration |
|                 | - Validate **Tunnel Source** for Tunnel1 based on device-specific interfaces and IP addresses.                                         | **1.0 point** for incorrect Tunnel Source configuration |
|                 | - Check **Tunnel Key** configuration on Tunnel1.                                                                                      | **1.0 point** for incorrect Tunnel Key configuration   |
|                 | - Validate **Tunnel IP addresses** on Tunnel1.                                                                                        | **1.0 point** for incorrect Tunnel IP address          |
|                 | - Verify **Bandwidth and Delay** settings on Tunnel1.                                                                                 | **1.0 point** per missing bandwidth setting<br>**1.0 point** per missing delay configuration |
|                 | - Validate **NHRP (Next Hop Resolution Protocol)** configuration on Tunnel1.                                                           | **1.0 point** per missing NHRP network ID configuration<br>**1.0 point** per missing NHRP authentication |
|                 | - Check for **`ip nhrp redirect`** on Tunnel1 for Toronto.                                                                            | **1.0 point** for missing NHRP redirect configuration  |
|                 | - Validate **ISAKMP Key** configuration on Toronto, Ottawa, and Oshawa.                                                               | **2.0 points** per device missing ISAKMP Key           |
|                 | - Validate **IKE Policy** for Toronto, Ottawa, and Oshawa, including attributes like `sha512`, `aes 256`, `pre-share`, and `group 14`. | **2.0 points** per missing IKE policy<br>**0.5 points** per missing attribute |
|                 | - Check **IPSec Transform Set**, ensuring it includes `esp-aes 256`, `esp-sha512-hmac`, and `mode transport`.                         | **2.0 points** for missing transform set<br>**1.0 point** per missing encryption, hash, or mode transport |
|                 | - Verify **IPSec Profile** references the correct transform set.                                                                      | **2.0 points** for missing profile<br>**1.0 point** for missing transform-set reference |
|                 | - Ensure the **IPSec Profile is applied** to Tunnel1.                                                                                 | **1.0 point** per device missing profile application to Tunnel1 |

---

### **Task 7: Configure Routing**

| **Total Grade** | **Grading Criteria**                                                                                                                                 | **Deduction per Issue**                                   |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| **15 points**   | - Validate **static default route** for TOR-D1 and TOR-D2.                                                                                          | **1.0 point** per device missing static route            |
|                 | - Confirm the presence of **EIGRP process** for the remaining devices (Toronto, ISP, Ottawa, and Oshawa).                                           | **2.0 points** per device missing EIGRP process          |
|                 | - Check **EIGRP address-family ipv4** configuration for Autonomous System (`group_number`).                                                         | **5.0 points** for missing EIGRP address-family          |
|                 | - Validate **EIGRP network commands** for required prefixes.                                                                                        | **1.0 point** per missing network command                |
|                 | - Ensure **forbidden network prefixes** are not present in EIGRP configurations.                                                                    | **2.0 points** for each forbidden network present         |
|                 | - Verify the configuration of **Router-ID** under EIGRP address-family ipv4.                                                                        | **1.0 point** per missing Router-ID                      |
|                 | - Check the presence of **static route configuration** on Toronto for a specific network prefix (`172.16.0.0/16`).                                  | **1.0 point** if the static route is missing             |

---

### **Task 8: Configure IP Services**

| **Total Grade** | **Grading Criteria**                                                                                                                                       | **Deduction per Issue**                           |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| **8 points**    | - Validate **time zone configuration** (`clock timezone EST -5`) for all devices.                                                                         | **0.2 points** per device with incorrect time zone configuration |
|                 | - Check **daylight savings time configuration** (`clock summer-time EDT recurring`) for all devices.                                                     | **0.5 points** per device missing daylight savings configuration |
|                 | - Verify **ISP NTP server configuration** as Stratum 2 (`ntp master 2`).                                                                                 | **2.0 points** for missing or incorrect NTP server configuration on ISP |
|                 | - Ensure **NTP synchronization with ISP** (`ntp server 2.2.2.2`) for Toronto, Ottawa, and Oshawa.                                                        | **0.5 points** per device missing or incorrect synchronization |
|                 | - Ensure **NTP synchronization with Toronto** (`ntp server 1.1.1.1`) for TOR-D1, TOR-D2, TOR-A1, and TOR-A2.                                             | **0.5 points** per device missing or incorrect synchronization |
