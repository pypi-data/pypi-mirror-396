# DNS Resolver

A robust, pure-Python DNS resolver built from scratch. This library allows you to perform DNS queries without relying on the OS's internal resolver or heavy external dependencies like `dnspython`.

It constructs raw DNS packets, sends them over UDP, and parses the binary response manually.

## Features

* **Zero Dependencies:** Runs on standard Python libraries (`socket`, `struct`, `os`, `platform`).
* **Cross-Platform:** Automatically detects the system DNS server on **Windows** (via PowerShell), **Linux** (via `resolvectl` or `/etc/resolv.conf`), and **macOS**.
* **Wide Record Support:** Supports `A`, `AAAA` (IPv6), `MX`, `TXT`, `NS`, `CNAME`, `SOA`, and `PTR`.
* **Reverse DNS:** Automatically handles reverse IP lookups when querying `PTR` records.
* **Robust Parsing:** Correctly handles DNS pointer compression.

## Installation

```bash
pip install dns-resolver-yourname
```
## Usage
**Command Line Interface (CLI)**

You can use the tool directly from your terminal after installation:

**Basic Lookup (A Record)**
```bash
dns-resolve google.com A
```

**Get Mail Servers (MX)**
```bash
**dns-resolve yahoo.com MX**
```

**Reverse DNS (PTR) Simply enter the IP address, and the tool will format the query for you.**
```bash
dns-resolve 8.8.8.8 PTR
```
**Custom Server Query a specific DNS server (e.g., Cloudflare).**
```bash
*dns-resolve google.com A --server 1.1.1.1
```
## Python Library

You can also use it inside your own Python scripts:
```python

from dns_resolver import resolve

# 1. Simple A Record lookup
# Returns a list of strings
results = resolve("example.com", "A")
for record in results:
    print(record)

# 2. Check for TXT records (useful for verification tokens)
txt_records = resolve("openai.com", "TXT")
print(txt_records)

# 3. Custom DNS Server
# Query 1.1.1.1 directly instead of the system default
resolve("google.com", "A", custom_server="1.1.1.1")
```

**Supported Record Types**

| Type | Description | 
|---------|-------------|
|A	| IPv4 Address |
|AAAA	| IPv6 Address |
|MX	Mail | Exchange |
|TXT	| Text strings (SPF, verification) |
|NS	Name | Server |
|CNAME	| Canonical Name (Alias) |
|SOA	| Start of Authority |
|PTR	| Pointer (Reverse DNS) |
