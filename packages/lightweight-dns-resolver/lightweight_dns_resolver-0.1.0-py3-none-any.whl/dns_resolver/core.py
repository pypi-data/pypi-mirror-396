import socket
import struct
import random
import os
import subprocess
import re
import platform

# --- DNS Record Type Constants ---
TYPE_A     = 1
TYPE_NS    = 2
TYPE_CNAME = 5
TYPE_SOA   = 6
TYPE_PTR   = 12
TYPE_MX    = 15
TYPE_TXT   = 16
TYPE_AAAA  = 28

# Map for user strings to constants
RECORD_MAP = {
    'A': TYPE_A, 'AAAA': TYPE_AAAA, 'TXT': TYPE_TXT, 'MX': TYPE_MX,
    'CNAME': TYPE_CNAME, 'NS': TYPE_NS, 'SOA': TYPE_SOA, 'PTR': TYPE_PTR
}

class DNSQueryBuilder:
    # ... [Copy your DNSQueryBuilder class here] ...
    def encode_domain_name(self, domain):
        parts = domain.split('.')
        encoded = b""
        for part in parts:
            encoded += bytes([len(part)]) + part.encode('utf-8')
        encoded += b"\x00"
        return encoded

    def create_query(self, domain, record_type):
        transaction_id = random.randint(0, 65535)
        flags = 0x0100 
        header = struct.pack('!HHHHHH', transaction_id, flags, 1, 0, 0, 0)
        qname = self.encode_domain_name(domain)
        question = qname + struct.pack('!HH', record_type, 1) 
        return header + question

class DNSResponseParser:
    # ... [Copy your DNSResponseParser class here] ...
    def __init__(self, data):
        self.data = data
        self.offset = 0

    def read_bytes(self, length):
        chunk = self.data[self.offset : self.offset + length]
        self.offset += length
        return chunk

    def decode_name(self):
        labels = []
        original_offset = None
        while True:
            length_byte = self.data[self.offset]
            if length_byte == 0:
                self.offset += 1
                break
            if (length_byte & 0xC0) == 0xC0:
                pointer_bytes = self.data[self.offset : self.offset + 2]
                pointer_val = struct.unpack('!H', pointer_bytes)[0]
                offset_ptr = pointer_val & 0x3FFF
                if original_offset is None:
                    original_offset = self.offset + 2
                self.offset = offset_ptr 
                continue
            self.offset += 1
            label = self.read_bytes(length_byte)
            labels.append(label.decode('utf-8', errors='ignore'))
        if original_offset is not None:
            self.offset = original_offset
        return ".".join(labels)

    def parse_txt_rdata(self, length):
        txt_parts = []
        start_offset = self.offset
        while (self.offset - start_offset) < length:
            txt_len = self.data[self.offset]
            self.offset += 1
            txt_string = self.read_bytes(txt_len)
            txt_parts.append(txt_string.decode('utf-8', errors='ignore'))
        return " ".join(txt_parts)
    
    def parse_soa_rdata(self):
        mname = self.decode_name() 
        rname = self.decode_name() 
        serial, refresh, retry, expire, minimum = struct.unpack('!IIIII', self.read_bytes(20))
        return (f"Primary NS: {mname}, Mailbox: {rname}, Serial: {serial}")

    def parse_mx_rdata(self):
        preference = struct.unpack('!H', self.read_bytes(2))[0]
        exchange = self.decode_name()
        return f"{preference} {exchange}"

    def parse(self):
        results = []
        header_data = self.read_bytes(12)
        _, _, qdcount, ancount, _, _ = struct.unpack('!HHHHHH', header_data)
        
        for _ in range(qdcount):
            self.decode_name()
            self.read_bytes(4) 

        for _ in range(ancount):
            name = self.decode_name() 
            type_, class_, ttl, data_len = struct.unpack('!HHIH', self.read_bytes(10))
            
            result_str = ""
            if type_ == TYPE_A:
                ip_addr = socket.inet_ntoa(self.read_bytes(data_len))
                result_str = f"[A] {name} -> {ip_addr}"
            elif type_ == TYPE_AAAA:
                try:
                    ip_addr = socket.inet_ntop(socket.AF_INET6, self.read_bytes(data_len))
                    result_str = f"[AAAA] {name} -> {ip_addr}"
                except:
                    result_str = f"[AAAA] {name} -> (IPv6 error)"
            elif type_ == TYPE_NS:
                result_str = f"[NS] {name} -> {self.decode_name()}"
            elif type_ == TYPE_CNAME:
                result_str = f"[CNAME] {name} -> {self.decode_name()}"
            elif type_ == TYPE_MX:
                result_str = f"[MX] {name} -> {self.parse_mx_rdata()}"
            elif type_ == TYPE_SOA:
                result_str = f"[SOA] {name} -> {self.parse_soa_rdata()}"
            elif type_ == TYPE_TXT:
                result_str = f"[TXT] {name} -> {self.parse_txt_rdata(data_len)}"
            elif type_ == TYPE_PTR:
                result_str = f"[PTR] {name} -> {self.decode_name()}"
            else:
                self.read_bytes(data_len)
            
            if result_str:
                results.append(result_str)
                print(result_str) # Keep printing for CLI feedback
        
        return results

def get_system_dns_server():
    # ... [Copy your NEW robust system DNS function here] ...
    system = platform.system()
    if system == "Windows":
        try:
            cmd = ["powershell", "-Command", "(Get-DnsClientServerAddress -AddressFamily IPv4).ServerAddresses"]
            output = subprocess.check_output(cmd, text=True)
            for line in output.splitlines():
                line = line.strip()
                if line and re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", line):
                    return line
        except: pass
    else:
        try:
            output = subprocess.check_output(["resolvectl", "dns"], text=True, stderr=subprocess.DEVNULL)
            ips = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", output)
            if ips: return ips[0]
        except: pass
        if os.path.exists("/etc/resolv.conf"):
            try:
                with open("/etc/resolv.conf", "r") as f:
                    for line in f:
                        if line.startswith("nameserver") and not "127." in line:
                            return line.split()[1]
            except: pass
    return "8.8.8.8"

def ipv4_to_reverse_dns(ip):
    return ".".join(reversed(ip.split('.'))) + ".in-addr.arpa"

def resolve(domain, record_type='A', custom_server=None):
    if custom_server:
        dns_server = custom_server
    else:
        dns_server = get_system_dns_server()
    
    key = record_type.upper()
    if key not in RECORD_MAP:
        raise ValueError(f"Unsupported record type: {record_type}")

    rtype = RECORD_MAP[key]
    
    if rtype == TYPE_PTR and re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
        domain = ipv4_to_reverse_dns(domain)

    builder = DNSQueryBuilder()
    packet = builder.create_query(domain, rtype)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(4)
    try:
        sock.sendto(packet, (dns_server, 53))
        data, _ = sock.recvfrom(4096)
        parser = DNSResponseParser(data)
        return parser.parse() # Now returns list of strings
    except Exception as e:
        print(f"Error: {e}")
        return []
