"""
logic.py — Attack & Defense Engine
====================================
Pure simulation logic.
No sockets. No real network I/O. No real authentication.
Returns (success, log_lines, delay_seconds) tuples consumed by the GUI.
"""

import random
import time


class AttackEngine:
    """Simulates all attacker actions against a VirtualSystem instance."""

    def __init__(self, vsys):
        self.vsys = vsys

    # ── Internal helpers ──────────────────────────────────────

    @staticmethod
    def _rand_delay(base=1.0, jitter=0.5) -> float:
        return base + random.uniform(0, jitter)

    @staticmethod
    def _fake_mac() -> str:
        return ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))

    @staticmethod
    def _rand_port() -> int:
        return random.randint(40000, 65000)

    # ── SCAN ─────────────────────────────────────────────────

    def scan(self):
        """Simulated host discovery / ARP sweep."""
        vs = self.vsys
        lines = [
            f"[*] Starting host discovery  →  192.168.0.0/24",
            f"[*] Sending ARP probes ... ",
            f"[+] Host UP :  {vs.target_ip}    MAC: {self._fake_mac()}",
            f"[*] OS fingerprint   :  Linux 5.15 (Ubuntu 22.04 LTS)",
            f"[*] Hostname         :  target-host.local",
            f"[*] TTL: 64   RTT: {random.randint(1, 9)} ms",
        ]
        if vs.firewall:
            lines.append("[!] Firewall detected — ICMP packets are filtered")
        if vs.ids:
            lines.append("[IDS] Scan activity logged by target IDS")
            vs.record_intrusion()
        lines.append(f"[+] Scan complete.  1 host reachable.")
        return True, lines, self._rand_delay(1.5)

    # ── PORT SCAN ────────────────────────────────────────────

    def port_scan(self):
        """Simulated TCP SYN port scan."""
        vs = self.vsys
        lines = [
            f"[*] Initiating SYN stealth scan  →  {vs.target_ip}",
            f"[*] Scanning top 1000 ports ...",
            "",
        ]
        # Firewall hides most ports
        visible = {22: vs.ports[22]} if vs.firewall and 22 in vs.ports else vs.ports

        lines.append(f"{'PORT':<13}{'STATE':<11}{'SERVICE':<13}BANNER")
        lines.append("─" * 56)
        for port, (svc, banner) in visible.items():
            state = "filtered" if vs.firewall else "open"
            lines.append(f"{str(port)+'/tcp':<13}{state:<11}{svc:<13}{banner}")

        if vs.ids:
            lines.append("")
            lines.append("[IDS] Port-scan signature detected — logged!")
            vs.record_intrusion()

        lines += [
            "",
            f"[+] {len(visible)} port(s) visible  |  {1000 - len(visible)} filtered/closed",
            f"[*] Elapsed: {random.uniform(2, 8):.2f} s",
        ]
        return True, lines, self._rand_delay(2.0)

    # ── BRUTE FORCE ──────────────────────────────────────────

    def brute_force(self, wordlist: list):
        """
        Simulated credential brute-force.
        Iterates wordlist; succeeds only if a word matches vs.password.
        """
        vs = self.vsys
        lines = [
            f"[*] Starting brute-force  →  {vs.target_ip}:22  (SSH)",
            f"[*] Target user : admin",
            f"[*] Wordlist    : {len(wordlist)} entries",
            "",
        ]

        # Both firewall AND ids = hard block
        if vs.firewall and vs.ids:
            lines += [
                "[FW]  SSH rate-limit rule ACTIVE",
                "[IDS] Brute-force pattern matched — IP BLOCKED",
                f"[!]  {vs.attacker_ip} added to block-list",
                "[✗]  Attack terminated before first attempt.",
            ]
            vs.record_intrusion()
            return False, lines, self._rand_delay(0.8)

        found = False
        cracked = None
        for i, word in enumerate(wordlist):
            status = "✓ HIT" if word == vs.password else "✗ fail"
            lines.append(f"  [{i+1:03d}]  admin : {word:<22} {status}")
            if word == vs.password:
                found = True
                cracked = word
                break
            # IDS fires periodically
            if vs.ids and i > 0 and i % 5 == 0:
                lines.append(f"  [IDS]  Anomaly spike at attempt #{i+1}")
                vs.record_intrusion()

        lines.append("")
        if found:
            vs.access_granted = True
            lines += [
                f"[+] *** PASSWORD CRACKED  →  '{cracked}' ***",
                f"[+] Credentials  :  admin : {cracked}",
                f"[+] SSH session  :  {vs.attacker_ip} → {vs.target_ip}:22",
                f"[*] Shell opened as: admin",
            ]
        else:
            lines += [
                "[✗] Password not in wordlist.",
                "[~] Hint: try  brute <word1> <word2> ...  or use 'exploit'.",
            ]

        delay = self._rand_delay(max(0.5, len(wordlist) * 0.06))
        return found, lines, delay

    # ── EXPLOIT ──────────────────────────────────────────────

    def exploit(self):
        """
        Generic simulated exploit.
        Result depends on how many defenses are active.
        """
        vs = self.vsys
        cve  = f"CVE-2024-{random.randint(10000, 99999)}"
        lport = self._rand_port()
        lines = [
            f"[*] Loading exploit  :  {cve}",
            f"[*] Target           :  {vs.target_ip}",
            f"[*] Payload          :  linux/x64/reverse_shell",
            f"[*] LHOST={vs.attacker_ip}  LPORT={lport}",
            "",
        ]
        dlevel = vs.defense_level()

        if dlevel == 0:
            lines += [
                f"[*] Probing for {cve} ...",
                "[+] Target IS VULNERABLE",
                "[*] Sending payload ...",
                "[*] Waiting for callback ...",
                "",
                "[+] *** SHELL OBTAINED — ROOT ACCESS GRANTED ***",
                f"[+] Session opened  :  {vs.attacker_ip}:{lport} ← {vs.target_ip}",
                f"[*] uid=0(root) gid=0(root)  hostname=target-host",
            ]
            vs.access_granted = True
            return True, lines, self._rand_delay(2.0)

        elif dlevel == 1:
            lines.append("[~] Partial defenses detected — attempting bypass ...")
            if random.random() < 0.38:
                lines += [
                    "[+] Firewall rule bypassed via fragmented packets",
                    "",
                    "[+] *** LIMITED SHELL OBTAINED ***",
                    f"[+] Session opened  :  {vs.attacker_ip}:{lport} ← {vs.target_ip}",
                    f"[*] uid=33(www-data)  — privilege escalation required",
                ]
                vs.access_granted = True
                vs.record_intrusion()
                return True, lines, self._rand_delay(2.5)
            else:
                lines += [
                    "[FW]  Exploit payload dropped at firewall",
                    "[✗]  Exploit failed. Defenses held.",
                ]
                vs.record_intrusion()
                return False, lines, self._rand_delay(1.5)

        else:  # full defense
            lines += [
                "[FW]  Connection reset by firewall",
                "[IDS] Exploit signature matched — BLOCKED & LOGGED",
                "[HP]  Honeypot engaged — attacker fingerprinted",
                f"[!]  {vs.attacker_ip} permanently blocked",
                "",
                "[✗]  Exploit failed. All defenses are active.",
            ]
            vs.record_intrusion()
            return False, lines, self._rand_delay(1.0)

    # ── FILE OPS (post-exploit) ───────────────────────────────

    def ls(self, dirname: str = None):
        """List directory contents — requires access."""
        vs = self.vsys
        if not vs.access_granted:
            return False, ["[✗] ACCESS DENIED — gain access first (brute / exploit)"], 0
        d = dirname or vs.current_dir
        contents = vs.fs.get(d)
        if contents is None:
            return False, [f"[✗] Directory not found: {d}"], 0
        lines = [f"[*] Listing: /{d}", ""]
        if contents["dirs"]:
            for sub in contents["dirs"]:
                lines.append(f"  drwxr-xr-x  {sub}/")
        if contents["files"]:
            for f in contents["files"]:
                size = random.randint(512, 204800)
                lines.append(f"  -rw-r--r--  {f:<30} {size:>8} bytes")
        if not contents["dirs"] and not contents["files"]:
            lines.append("  (empty)")
        return True, lines, self._rand_delay(0.2, 0.1)

    def cd(self, dirname: str):
        """Change virtual directory — requires access."""
        vs = self.vsys
        if not vs.access_granted:
            return False, ["[✗] ACCESS DENIED"], 0
        if dirname == "..":
            vs.current_dir = "root"
            return True, [f"[*] Changed to /root"], 0
        if dirname in vs.fs:
            vs.current_dir = dirname
            return True, [f"[*] Changed to /{dirname}"], 0
        return False, [f"[✗] No such directory: {dirname}"], 0

    def cat(self, filename: str):
        """Read a file — requires access."""
        from system import FILE_CONTENTS
        vs = self.vsys
        if not vs.access_granted:
            return False, ["[✗] ACCESS DENIED — gain access first"], 0
        for dname, contents in vs.fs.items():
            if filename in contents["files"]:
                text = FILE_CONTENTS.get(
                    filename,
                    f"[FILE: {filename}]\n[Binary or empty — no preview]"
                )
                lines = [f"[*] //{dname}/{filename}", "─" * 48] + text.splitlines()
                return True, lines, self._rand_delay(0.3, 0.2)
        return False, [f"[✗] File not found: {filename}"], 0


# ─────────────────────────────────────────────────────────────
#  COMMAND PARSER
# ─────────────────────────────────────────────────────────────
class CommandParser:
    """
    Parses raw terminal input and dispatches to AttackEngine or defender
    mutations on VirtualSystem.
    Returns (success, log_lines, delay) — same signature as engine methods.
    """

    def __init__(self, vsys, engine: AttackEngine):
        self.vsys   = vsys
        self.engine = engine

    def parse(self, raw: str):
        parts = raw.strip().split()
        if not parts:
            return None, [], 0
        cmd  = parts[0].lower()
        args = parts[1:]

        # ── Attacker commands ─────────────────────────────────
        if cmd == "scan":
            return self.engine.scan()

        if cmd == "ports":
            return self.engine.port_scan()

        if cmd in ("brute", "bruteforce"):
            from system import BUILTIN_WORDLIST
            wordlist = args if args else BUILTIN_WORDLIST
            return self.engine.brute_force(wordlist)

        if cmd == "exploit":
            return self.engine.exploit()

        # ── File system commands ──────────────────────────────
        if cmd == "ls":
            return self.engine.ls(args[0] if args else None)

        if cmd == "cd":
            if not args:
                return False, ["Usage: cd <dirname>"], 0
            return self.engine.cd(args[0])

        if cmd == "cat":
            if not args:
                return False, ["Usage: cat <filename>"], 0
            return self.engine.cat(args[0])

        # ── Defender commands ─────────────────────────────────
        if cmd == "setpass":
            if not args:
                return False, ["Usage: setpass <newpassword>"], 0
            self.vsys.set_password(args[0])
            return True, [f"[DEF] Password updated → '{args[0]}'"], 0.1

        if cmd == "addfile":
            if not args:
                return False, ["Usage: addfile <filename> [dirname]"], 0
            d = args[1] if len(args) > 1 else None
            ok = self.vsys.add_file(args[0], d)
            msg = f"[DEF] File '{args[0]}' added" if ok else f"[!] File already exists"
            return ok, [msg], 0.1

        if cmd == "rmfile":
            if not args:
                return False, ["Usage: rmfile <filename> [dirname]"], 0
            d = args[1] if len(args) > 1 else None
            ok = self.vsys.remove_file(args[0], d)
            msg = f"[DEF] File '{args[0]}' removed" if ok else "[!] File not found"
            return ok, [msg], 0.1

        if cmd == "addfolder":
            if not args:
                return False, ["Usage: addfolder <foldername>"], 0
            ok = self.vsys.add_folder(args[0])
            msg = f"[DEF] Folder '{args[0]}' created" if ok else "[!] Folder already exists"
            return ok, [msg], 0.1

        if cmd in ("firewall", "fw"):
            action = args[0].lower() if args else "on"
            if action in ("on", "enable"):
                self.vsys.enable_firewall() if hasattr(self.vsys, "enable_firewall") \
                    else setattr(self.vsys, "firewall", True)
                return True, ["[DEF] Firewall ENABLED"], 0.1
            else:
                self.vsys.firewall = False
                return True, ["[DEF] Firewall DISABLED"], 0.1

        if cmd == "ids":
            action = args[0].lower() if args else "on"
            if action in ("on", "enable"):
                self.vsys.ids = True
                return True, ["[DEF] IDS ENABLED"], 0.1
            else:
                self.vsys.ids = False
                return True, ["[DEF] IDS DISABLED"], 0.1

        if cmd == "honeypot":
            action = args[0].lower() if args else "on"
            self.vsys.honeypot = (action in ("on", "enable"))
            state = "ENABLED" if self.vsys.honeypot else "DISABLED"
            return True, [f"[DEF] Honeypot {state}"], 0.1

        if cmd in ("reset", "newgame"):
            self.vsys.reset()
            return True, ["[SYS] System reset to defaults. New session started."], 0.2

        if cmd in ("help", "?"):
            return True, HELP_TEXT.splitlines(), 0

        if cmd in ("status", "info"):
            s = self.vsys.status_summary()
            lines = [
                "┌─ System Status ─────────────────────────┐",
                f"│  Target IP   : {s['target_ip']:<26}│",
                f"│  Access      : {'GRANTED ✓' if s['access'] else 'DENIED ✗':<26}│",
                f"│  Firewall    : {'ON ✓' if s['firewall'] else 'OFF ✗':<26}│",
                f"│  IDS         : {'ON ✓' if s['ids'] else 'OFF ✗':<26}│",
                f"│  Honeypot    : {'ON ✓' if s['honeypot'] else 'OFF ✗':<26}│",
                f"│  Password    : {s['password']:<26}│",
                f"│  Intrusions  : {str(s['intrusions']):<26}│",
                "└─────────────────────────────────────────┘",
            ]
            return True, lines, 0

        return False, [f"[!] Unknown command: '{cmd}'  (type 'help' for commands)"], 0


# ─────────────────────────────────────────────────────────────
#  HELP TEXT
# ─────────────────────────────────────────────────────────────
HELP_TEXT = """
╔══════════════════════════════════════════════════════╗
║            CYBER ATTACK vs DEFENSE LAB               ║
║                  Command Reference                   ║
╠══════════════════════════════════════════════════════╣
║  ATTACKER COMMANDS                                   ║
║  ─────────────────────────────────────────────────  ║
║  scan              Host discovery sweep              ║
║  ports             TCP SYN port scan                 ║
║  brute [w1 w2 ..]  Brute-force SSH (custom wordlist) ║
║  exploit           Launch simulated exploit          ║
║                                                      ║
║  POST-EXPLOIT (requires access)                      ║
║  ─────────────────────────────────────────────────  ║
║  ls [dir]          List directory                    ║
║  cd <dir>          Change directory                  ║
║  cat <file>        Read file contents                ║
║                                                      ║
║  DEFENDER COMMANDS                                   ║
║  ─────────────────────────────────────────────────  ║
║  setpass <pw>      Change system password            ║
║  addfile <f> [dir] Add file to filesystem            ║
║  rmfile <f> [dir]  Remove file                       ║
║  addfolder <name>  Create new directory              ║
║  firewall on|off   Toggle firewall                   ║
║  ids on|off        Toggle IDS                        ║
║  honeypot on|off   Toggle honeypot                   ║
║                                                      ║
║  SYSTEM                                              ║
║  ─────────────────────────────────────────────────  ║
║  status            Show system status                ║
║  reset             Reset to defaults                 ║
║  help              Show this help                    ║
╚══════════════════════════════════════════════════════╝
""".strip()
