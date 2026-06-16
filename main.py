"""
main.py — Cyber Attack vs Defense Lab
======================================
Entry point & full Tkinter GUI.
Dark hacker-terminal aesthetic with split attacker / defender panels
and a shared command-line terminal at the bottom.

Run:  python main.py
"""

import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox
import threading
import time
import random
import sys

from system import VirtualSystem, BUILTIN_WORDLIST
from logic  import AttackEngine, CommandParser, HELP_TEXT

# ─────────────────────────────────────────────────────────────
#  COLOUR PALETTE  (dark terminal theme)
# ─────────────────────────────────────────────────────────────
C = {
    "bg":        "#0d0f14",   # main background
    "panel":     "#12151c",   # card / panel bg
    "border":    "#1e2330",   # subtle border
    "accent_r":  "#ff3e3e",   # red  — attack
    "accent_g":  "#39ff88",   # green — success / defend
    "accent_b":  "#4da6ff",   # blue — info
    "accent_y":  "#ffd23f",   # yellow — warning
    "accent_p":  "#b06bff",   # purple — system
    "text":      "#c8d0e0",   # normal text
    "text_dim":  "#4a5470",   # dimmed text
    "text_hi":   "#ffffff",   # bright white
    "btn_atk":   "#1f0a0a",   # button bg (attack)
    "btn_def":   "#081a10",   # button bg (defend)
    "terminal":  "#080b10",   # terminal background
    "prompt":    "#39ff88",   # terminal prompt colour
}

# ─────────────────────────────────────────────────────────────
#  APP CLASS
# ─────────────────────────────────────────────────────────────
class CyberLabApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Cyber Attack vs Defense Lab  //  SIMULATION")
        self.configure(bg=C["bg"])
        self.geometry("1200x820")
        self.minsize(960, 700)
        self.resizable(True, True)

        # ── Core simulation objects ───────────────────────────
        self.vsys   = VirtualSystem()
        self.engine = AttackEngine(self.vsys)
        self.parser = CommandParser(self.vsys, self.engine)

        # ── Fonts ─────────────────────────────────────────────
        self._setup_fonts()

        # ── Build layout ──────────────────────────────────────
        self._build_header()
        self._build_main_panels()
        self._build_terminal()
        self._build_statusbar()

        # ── Welcome message ───────────────────────────────────
        self._welcome()

        # ── Bind keyboard shortcut ───────────────────────────
        self.bind("<Control-l>", lambda e: self._clear_console())
        self.bind("<Control-r>", lambda e: self._reset_session())

    # ─────────────────────────────────────────────────────────
    #  FONT SETUP
    # ─────────────────────────────────────────────────────────
    def _setup_fonts(self):
        self.font_mono   = tkfont.Font(family="Courier New",  size=10)
        self.font_mono_s = tkfont.Font(family="Courier New",  size=9)
        self.font_ui     = tkfont.Font(family="Courier New",  size=11, weight="bold")
        self.font_title  = tkfont.Font(family="Courier New",  size=14, weight="bold")
        self.font_label  = tkfont.Font(family="Courier New",  size=9)

    # ─────────────────────────────────────────────────────────
    #  HEADER
    # ─────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=C["panel"], height=52)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # Left — logo
        tk.Label(
            hdr, text="⚡ CYBER ATTACK vs DEFENSE LAB",
            bg=C["panel"], fg=C["accent_g"],
            font=self.font_title, padx=16
        ).pack(side="left", pady=10)


        # Right — controls
        right = tk.Frame(hdr, bg=C["panel"])
        right.pack(side="right", padx=12)

        self._hdr_btn(right, "⟳ RESET",  self._reset_session, C["accent_y"])
        self._hdr_btn(right, "? HELP",   self._show_help,     C["accent_b"])
        self._hdr_btn(right, "✕ QUIT",   self.quit,           C["accent_r"])

        # IP label
        self.ip_var = tk.StringVar(value=f"TARGET: {self.vsys.target_ip}")
        tk.Label(
            hdr, textvariable=self.ip_var,
            bg=C["panel"], fg=C["accent_p"],
            font=self.font_label, padx=14
        ).pack(side="right", pady=10)

    def _hdr_btn(self, parent, text, cmd, color):
        b = tk.Button(
            parent, text=text, command=cmd,
            bg=C["panel"], fg=color,
            activebackground=C["border"], activeforeground=color,
            font=self.font_label, relief="flat",
            padx=8, pady=4, cursor="hand2",
            bd=0
        )
        b.pack(side="right", padx=4, pady=8)

    # ─────────────────────────────────────────────────────────
    #  MAIN PANELS
    # ─────────────────────────────────────────────────────────
    def _build_main_panels(self):
        """Left = attacker, Right = defender, shared console in middle."""
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=8, pady=(4, 0))

        # ── Attacker panel (left) ─────────────────────────────
        atk_outer = tk.Frame(body, bg=C["border"], bd=0)
        atk_outer.pack(side="left", fill="both", expand=True, padx=(0, 4))

        atk = tk.Frame(atk_outer, bg=C["panel"], padx=10, pady=10)
        atk.pack(fill="both", expand=True, padx=1, pady=1)

        self._section_label(atk, "◈  ATTACKER", C["accent_r"])
        self._attacker_controls(atk)

        # ── Console (centre) ──────────────────────────────────
        con_outer = tk.Frame(body, bg=C["border"])
        con_outer.pack(side="left", fill="both", expand=True, padx=4)

        con = tk.Frame(con_outer, bg=C["panel"], padx=6, pady=6)
        con.pack(fill="both", expand=True, padx=1, pady=1)

        self._section_label(con, "◈  CONSOLE LOG", C["accent_b"])
        self._build_console(con)

        # ── Defender panel (right) ────────────────────────────
        def_outer = tk.Frame(body, bg=C["border"])
        def_outer.pack(side="left", fill="both", expand=True, padx=(4, 0))

        dfn = tk.Frame(def_outer, bg=C["panel"], padx=10, pady=10)
        dfn.pack(fill="both", expand=True, padx=1, pady=1)

        self._section_label(dfn, "◈  DEFENDER", C["accent_g"])
        self._defender_controls(dfn)

    def _section_label(self, parent, text, color):
        f = tk.Frame(parent, bg=C["panel"])
        f.pack(fill="x", pady=(0, 8))
        tk.Label(
            f, text=text, bg=C["panel"], fg=color,
            font=self.font_ui
        ).pack(side="left")
        tk.Frame(f, bg=color, height=1).pack(
            side="left", fill="x", expand=True, padx=(8, 0), pady=6
        )

    # ─────────────────────────────────────────────────────────
    #  ATTACKER CONTROLS
    # ─────────────────────────────────────────────────────────
    def _attacker_controls(self, parent):
        # Wordlist input
        self._field_label(parent, "Custom Wordlist  (space-separated)")
        self.wordlist_var = tk.StringVar(value="admin password 1234 root admin123")
        tk.Entry(
            parent, textvariable=self.wordlist_var,
            bg=C["terminal"], fg=C["accent_y"],
            insertbackground=C["accent_y"],
            font=self.font_mono_s, relief="flat",
            bd=0, highlightthickness=1,
            highlightbackground=C["border"],
            highlightcolor=C["accent_r"]
        ).pack(fill="x", pady=(0, 10), ipady=5, padx=2)

        # Attack buttons
        attacks = [
            ("⟳  HOST SCAN",    self._do_scan,       C["accent_b"],  "Simulate network host discovery"),
            ("⬡  PORT SCAN",    self._do_port_scan,  C["accent_b"],  "Enumerate open TCP ports"),
            ("⚡ BRUTE FORCE",  self._do_brute,      C["accent_y"],  "Credential brute-force attack"),
            ("☠  EXPLOIT",      self._do_exploit,    C["accent_r"],  "Launch exploit payload"),
        ]
        for label, cmd, color, tip in attacks:
            self._attack_btn(parent, label, cmd, color, tip)

        # Status indicators
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", pady=12)
        self._field_label(parent, "Post-Exploit File Access")

        fs_cmds = [
            ("LS  List Files",   lambda: self._run_cmd("ls"),         C["accent_g"]),
            ("CAT secrets.txt",  lambda: self._run_cmd("cat secrets.txt"), C["accent_y"]),
            ("CAT creds.bak",    lambda: self._run_cmd("cat creds.bak"),   C["accent_y"]),
            ("CAT auth.log",     lambda: self._run_cmd("cat auth.log"),    C["accent_p"]),
        ]
        for label, cmd, color in fs_cmds:
            self._small_btn(parent, label, cmd, color)

        # Access indicator
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", pady=12)
        self.access_label = tk.Label(
            parent, text="● ACCESS: DENIED",
            bg=C["panel"], fg=C["accent_r"],
            font=self.font_ui
        )
        self.access_label.pack(anchor="w")

    def _attack_btn(self, parent, text, cmd, color, tooltip=""):
        btn = tk.Button(
            parent, text=text, command=cmd,
            bg=C["btn_atk"], fg=color,
            activebackground=C["border"], activeforeground=color,
            font=self.font_ui, relief="flat",
            pady=9, cursor="hand2", bd=0,
            highlightthickness=1,
            highlightbackground=color,
        )
        btn.pack(fill="x", pady=3)
        if tooltip:
            self._bind_tooltip(btn, tooltip)

    def _small_btn(self, parent, text, cmd, color):
        tk.Button(
            parent, text=text, command=cmd,
            bg=C["panel"], fg=color,
            activebackground=C["border"], activeforeground=color,
            font=self.font_label, relief="flat",
            pady=5, cursor="hand2", bd=0,
            highlightthickness=1,
            highlightbackground=C["border"],
        ).pack(fill="x", pady=2)

    # ─────────────────────────────────────────────────────────
    #  DEFENDER CONTROLS
    # ─────────────────────────────────────────────────────────
    def _defender_controls(self, parent):
        # Password
        self._field_label(parent, "System Password")
        pw_row = tk.Frame(parent, bg=C["panel"])
        pw_row.pack(fill="x", pady=(0, 8))

        self.pw_var = tk.StringVar(value=self.vsys.password)
        pw_entry = tk.Entry(
            pw_row, textvariable=self.pw_var,
            bg=C["terminal"], fg=C["accent_g"],
            insertbackground=C["accent_g"],
            font=self.font_mono, show="●",
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=C["border"],
            highlightcolor=C["accent_g"]
        )
        pw_entry.pack(side="left", fill="x", expand=True, ipady=5)

        tk.Button(
            pw_row, text="SET",
            command=self._do_setpass,
            bg=C["btn_def"], fg=C["accent_g"],
            activebackground=C["border"],
            font=self.font_label, relief="flat",
            cursor="hand2", bd=0, padx=10,
            highlightthickness=1,
            highlightbackground=C["accent_g"]
        ).pack(side="left", padx=(4, 0), ipady=5)

        # Show/hide password
        self._show_pw = False
        def toggle_pw():
            self._show_pw = not self._show_pw
            pw_entry.config(show="" if self._show_pw else "●")
        tk.Button(
            pw_row, text="👁",
            command=toggle_pw,
            bg=C["panel"], fg=C["text_dim"],
            activebackground=C["border"],
            font=self.font_label, relief="flat",
            cursor="hand2", bd=0, padx=6
        ).pack(side="left", padx=(2, 0))

        # Defense toggles
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", pady=8)
        self._field_label(parent, "Defenses")

        self.fw_var  = tk.BooleanVar(value=False)
        self.ids_var = tk.BooleanVar(value=False)
        self.hp_var  = tk.BooleanVar(value=False)

        defenses = [
            ("🔥  FIREWALL",  self.fw_var,  self._toggle_firewall,  "Blocks port scanning & filters exploits"),
            ("👁  IDS",       self.ids_var, self._toggle_ids,       "Intrusion Detection System"),
            ("🍯  HONEYPOT",  self.hp_var,  self._toggle_honeypot,  "Lure and fingerprint attackers"),
        ]
        for label, var, cmd, tip in defenses:
            self._defense_toggle(parent, label, var, cmd, tip)

        # Filesystem management
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", pady=10)
        self._field_label(parent, "File System")

        file_row = tk.Frame(parent, bg=C["panel"])
        file_row.pack(fill="x", pady=(0, 4))
        self.new_file_var = tk.StringVar(value="newfile.txt")
        tk.Entry(
            file_row, textvariable=self.new_file_var,
            bg=C["terminal"], fg=C["accent_g"],
            insertbackground=C["accent_g"],
            font=self.font_mono_s, relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=C["border"]
        ).pack(side="left", fill="x", expand=True, ipady=4)
        tk.Button(
            file_row, text="+ FILE",
            command=self._do_addfile,
            bg=C["btn_def"], fg=C["accent_g"],
            font=self.font_label, relief="flat",
            cursor="hand2", bd=0, padx=8,
            highlightthickness=1,
            highlightbackground=C["accent_g"]
        ).pack(side="left", padx=(4, 0), ipady=4)

        folder_row = tk.Frame(parent, bg=C["panel"])
        folder_row.pack(fill="x", pady=(0, 4))
        self.new_folder_var = tk.StringVar(value="newfolder")
        tk.Entry(
            folder_row, textvariable=self.new_folder_var,
            bg=C["terminal"], fg=C["accent_g"],
            insertbackground=C["accent_g"],
            font=self.font_mono_s, relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=C["border"]
        ).pack(side="left", fill="x", expand=True, ipady=4)
        tk.Button(
            folder_row, text="+ DIR",
            command=self._do_addfolder,
            bg=C["btn_def"], fg=C["accent_b"],
            font=self.font_label, relief="flat",
            cursor="hand2", bd=0, padx=8,
            highlightthickness=1,
            highlightbackground=C["accent_b"]
        ).pack(side="left", padx=(4, 0), ipady=4)

        # Defense level indicator
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", pady=10)
        self.defense_label = tk.Label(
            parent, text="◉ DEFENSE LEVEL: NONE",
            bg=C["panel"], fg=C["accent_r"],
            font=self.font_ui
        )
        self.defense_label.pack(anchor="w")

    def _defense_toggle(self, parent, label, var, cmd, tooltip):
        row = tk.Frame(parent, bg=C["panel"])
        row.pack(fill="x", pady=3)
        cb = tk.Checkbutton(
            row, text=label, variable=var, command=cmd,
            bg=C["panel"], fg=C["text"],
            activebackground=C["panel"],
            selectcolor=C["terminal"],
            font=self.font_ui,
            cursor="hand2"
        )
        cb.pack(side="left")
        if tooltip:
            self._bind_tooltip(cb, tooltip)

    def _field_label(self, parent, text):
        tk.Label(
            parent, text=text,
            bg=C["panel"], fg=C["text_dim"],
            font=self.font_label
        ).pack(anchor="w", pady=(2, 1))

    # ─────────────────────────────────────────────────────────
    #  CONSOLE
    # ─────────────────────────────────────────────────────────
    def _build_console(self, parent):
        frame = tk.Frame(parent, bg=C["terminal"],
                         highlightthickness=1,
                         highlightbackground=C["border"])
        frame.pack(fill="both", expand=True)

        self.console = tk.Text(
            frame,
            bg=C["terminal"], fg=C["text"],
            insertbackground=C["accent_g"],
            font=self.font_mono_s,
            relief="flat", bd=0,
            wrap="word",
            state="disabled",
            selectbackground=C["border"],
        )
        sb = ttk.Scrollbar(frame, orient="vertical",
                           command=self.console.yview)
        self.console.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.console.pack(fill="both", expand=True, padx=4, pady=4)

        # Configure colour tags
        self.console.tag_config("success", foreground=C["accent_g"])
        self.console.tag_config("error",   foreground=C["accent_r"])
        self.console.tag_config("warn",    foreground=C["accent_y"])
        self.console.tag_config("info",    foreground=C["accent_b"])
        self.console.tag_config("system",  foreground=C["accent_p"])
        self.console.tag_config("dim",     foreground=C["text_dim"])
        self.console.tag_config("header",  foreground=C["text_hi"])

        # Clear button
        tk.Button(
            parent, text="CLR",
            command=self._clear_console,
            bg=C["panel"], fg=C["text_dim"],
            font=self.font_label, relief="flat",
            cursor="hand2", bd=0, padx=6, pady=2,
            activebackground=C["border"]
        ).pack(anchor="e", pady=(4, 0))

    # ─────────────────────────────────────────────────────────
    #  TERMINAL
    # ─────────────────────────────────────────────────────────
    def _build_terminal(self):
        outer = tk.Frame(self, bg=C["border"], height=1)
        outer.pack(fill="x")

        term_frame = tk.Frame(self, bg=C["terminal"])
        term_frame.pack(fill="x", padx=8, pady=(0, 4))

        # Label
        tk.Label(
            term_frame,
            text="TERMINAL",
            bg=C["terminal"], fg=C["text_dim"],
            font=self.font_label
        ).pack(side="left", padx=8, pady=6)

        # Prompt
        tk.Label(
            term_frame,
            text="root@kali:~$",
            bg=C["terminal"], fg=C["prompt"],
            font=self.font_mono
        ).pack(side="left", pady=6)

        # Input
        self.cmd_var = tk.StringVar()
        self.cmd_entry = tk.Entry(
            term_frame,
            textvariable=self.cmd_var,
            bg=C["terminal"], fg=C["accent_g"],
            insertbackground=C["accent_g"],
            font=self.font_mono,
            relief="flat", bd=0,
        )
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=6, pady=6)
        self.cmd_entry.bind("<Return>", self._on_terminal_enter)
        self.cmd_entry.bind("<Up>",     self._history_up)
        self.cmd_entry.bind("<Down>",   self._history_down)
        self.cmd_entry.focus_set()

        # Run button
        tk.Button(
            term_frame, text="▶ RUN",
            command=self._on_terminal_enter,
            bg=C["btn_def"], fg=C["accent_g"],
            activebackground=C["border"],
            font=self.font_label, relief="flat",
            cursor="hand2", bd=0, padx=10,
            highlightthickness=1,
            highlightbackground=C["accent_g"]
        ).pack(side="left", padx=6, pady=4, ipady=4)

        # Command history
        self._history     = []
        self._hist_cursor = -1

    # ─────────────────────────────────────────────────────────
    #  STATUS BAR
    # ─────────────────────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self, bg=C["border"], height=24)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.status_var = tk.StringVar(
            value="Ready  |  Type 'help' in the terminal  |  Ctrl+R = Reset  |  Ctrl+L = Clear"
        )
        tk.Label(
            bar, textvariable=self.status_var,
            bg=C["border"], fg=C["text_dim"],
            font=self.font_label, padx=10
        ).pack(side="left", pady=3)

        # Intrusion counter
        self.intr_var = tk.StringVar(value="Intrusions: 0")
        tk.Label(
            bar, textvariable=self.intr_var,
            bg=C["border"], fg=C["accent_y"],
            font=self.font_label, padx=10
        ).pack(side="right", pady=3)

    # ─────────────────────────────────────────────────────────
    #  CONSOLE WRITE HELPERS
    # ─────────────────────────────────────────────────────────
    def _log(self, text: str, tag: str = ""):
        """Thread-safe console write."""
        def _write():
            self.console.config(state="normal")
            self.console.insert("end", text + "\n", tag)
            self.console.see("end")
            self.console.config(state="disabled")
        self.after(0, _write)

    def _log_lines(self, lines: list, success: bool = True):
        for line in lines:
            if not line.strip():
                self._log("", "dim")
                continue
            if line.startswith("[+]") or line.startswith("[✓]") or "GRANTED" in line or "CRACKED" in line:
                tag = "success"
            elif line.startswith("[✗]") or "DENIED" in line or "BLOCKED" in line or "failed" in line.lower():
                tag = "error"
            elif line.startswith("[!]") or line.startswith("[FW]") or line.startswith("[IDS]"):
                tag = "warn"
            elif line.startswith("[*]") or line.startswith("[~]") or line.startswith("[HP]"):
                tag = "info"
            elif line.startswith("[SYS]") or line.startswith("[DEF]"):
                tag = "system"
            elif line.startswith("╔") or line.startswith("║") or line.startswith("╚") \
                 or line.startswith("┌") or line.startswith("│") or line.startswith("└"):
                tag = "header"
            elif line.startswith("─") or line.startswith("═"):
                tag = "dim"
            else:
                tag = ""
            self._log(line, tag)

    def _log_separator(self, char="─", color="dim"):
        self._log(char * 54, color)

    def _log_cmd_header(self, cmd: str):
        self._log("", "")
        self._log_separator()
        ts = time.strftime("%H:%M:%S")
        self._log(f"[{ts}]  >> {cmd.upper()}", "header")
        self._log_separator()

    def _clear_console(self, *_):
        self.console.config(state="normal")
        self.console.delete("1.0", "end")
        self.console.config(state="disabled")
        self._log("[SYS] Console cleared.", "system")

    # ─────────────────────────────────────────────────────────
    #  EXECUTION HELPERS
    # ─────────────────────────────────────────────────────────
    def _run_threaded(self, label: str, fn, *args):
        """Run fn(*args) in a background thread with simulated delay."""
        self._set_busy(True)
        self._log_cmd_header(label)

        def worker():
            try:
                success, lines, delay = fn(*args)
                if delay > 0:
                    time.sleep(delay)
                self.after(0, lambda: self._log_lines(lines, success))
                self.after(0, self._refresh_indicators)
            finally:
                self.after(0, lambda: self._set_busy(False))

        threading.Thread(target=worker, daemon=True).start()

    def _set_busy(self, busy: bool):
        state = "disabled" if busy else "normal"
        self.cmd_entry.config(state=state)
        txt = "Processing..." if busy else "Ready"
        self.status_var.set(txt)

    def _run_cmd(self, cmd_text: str):
        self._log_cmd_header(cmd_text)
        self._set_busy(True)

        def worker():
            try:
                success, lines, delay = self.parser.parse(cmd_text)
                if delay:
                    time.sleep(delay)
                self.after(0, lambda: self._log_lines(lines, success))
                self.after(0, self._refresh_indicators)
            finally:
                self.after(0, lambda: self._set_busy(False))

        threading.Thread(target=worker, daemon=True).start()

    # ─────────────────────────────────────────────────────────
    #  ATTACK BUTTON HANDLERS
    # ─────────────────────────────────────────────────────────
    def _do_scan(self):
        self._run_threaded("HOST SCAN", self.engine.scan)

    def _do_port_scan(self):
        self._run_threaded("PORT SCAN", self.engine.port_scan)

    def _do_brute(self):
        raw = self.wordlist_var.get().strip()
        wordlist = raw.split() if raw else BUILTIN_WORDLIST
        self._run_threaded("BRUTE FORCE", self.engine.brute_force, wordlist)

    def _do_exploit(self):
        self._run_threaded("EXPLOIT", self.engine.exploit)

    # ─────────────────────────────────────────────────────────
    #  DEFENDER BUTTON HANDLERS
    # ─────────────────────────────────────────────────────────
    def _do_setpass(self):
        pw = self.pw_var.get().strip()
        if not pw:
            self._log("[!] Password cannot be empty.", "warn")
            return
        self.vsys.set_password(pw)
        self._log(f"[DEF] Password updated successfully.", "system")
        self._refresh_indicators()

    def _toggle_firewall(self):
        self.vsys.firewall = self.fw_var.get()
        state = "ENABLED" if self.vsys.firewall else "DISABLED"
        self._log(f"[DEF] Firewall {state}", "system")
        self._refresh_indicators()

    def _toggle_ids(self):
        self.vsys.ids = self.ids_var.get()
        state = "ENABLED" if self.vsys.ids else "DISABLED"
        self._log(f"[DEF] IDS {state}", "system")
        self._refresh_indicators()

    def _toggle_honeypot(self):
        self.vsys.honeypot = self.hp_var.get()
        state = "ENABLED" if self.vsys.honeypot else "DISABLED"
        self._log(f"[DEF] Honeypot {state}", "system")
        self._refresh_indicators()

    def _do_addfile(self):
        name = self.new_file_var.get().strip()
        if not name:
            return
        ok = self.vsys.add_file(name)
        msg = f"[DEF] File '{name}' added to /{self.vsys.current_dir}" if ok \
              else f"[!] File '{name}' already exists"
        self._log(msg, "system" if ok else "warn")

    def _do_addfolder(self):
        name = self.new_folder_var.get().strip()
        if not name:
            return
        ok = self.vsys.add_folder(name)
        msg = f"[DEF] Folder '/{name}' created" if ok \
              else f"[!] Folder '{name}' already exists"
        self._log(msg, "system" if ok else "warn")

    # ─────────────────────────────────────────────────────────
    #  TERMINAL INPUT
    # ─────────────────────────────────────────────────────────
    def _on_terminal_enter(self, *_):
        raw = self.cmd_var.get().strip()
        if not raw:
            return
        # Echo to console
        self._log(f"root@kali:~$ {raw}", "success")
        # Save history
        self._history.append(raw)
        self._hist_cursor = len(self._history)
        self.cmd_var.set("")

        self._run_cmd(raw)

    def _history_up(self, *_):
        if self._history and self._hist_cursor > 0:
            self._hist_cursor -= 1
            self.cmd_var.set(self._history[self._hist_cursor])

    def _history_down(self, *_):
        if self._hist_cursor < len(self._history) - 1:
            self._hist_cursor += 1
            self.cmd_var.set(self._history[self._hist_cursor])
        else:
            self._hist_cursor = len(self._history)
            self.cmd_var.set("")

    # ─────────────────────────────────────────────────────────
    #  REFRESH INDICATORS
    # ─────────────────────────────────────────────────────────
    def _refresh_indicators(self):
        # Access label
        if self.vsys.access_granted:
            self.access_label.config(text="● ACCESS: GRANTED ✓", fg=C["accent_g"])
        else:
            self.access_label.config(text="● ACCESS: DENIED",    fg=C["accent_r"])

        # Defense level
        dlevel = self.vsys.defense_level()
        labels = {0: ("◉ DEFENSE LEVEL: NONE",    C["accent_r"]),
                  1: ("◉ DEFENSE LEVEL: PARTIAL",  C["accent_y"]),
                  2: ("◉ DEFENSE LEVEL: MAXIMUM",  C["accent_g"])}
        txt, col = labels[dlevel]
        self.defense_label.config(text=txt, fg=col)

        # Sync checkboxes (in case terminal changed state)
        self.fw_var.set(self.vsys.firewall)
        self.ids_var.set(self.vsys.ids)
        self.hp_var.set(self.vsys.honeypot)

        # Intrusion counter
        self.intr_var.set(f"Intrusions: {self.vsys.intrusion_count}")

        # IP label
        self.ip_var.set(f"TARGET: {self.vsys.target_ip}")

    # ─────────────────────────────────────────────────────────
    #  RESET / HELP
    # ─────────────────────────────────────────────────────────
    def _reset_session(self, *_):
        if messagebox.askyesno(
            "Reset Session",
            "Reset the virtual system to defaults?\n(All progress will be lost)"
        ):
            self.vsys.reset()
            self.engine = AttackEngine(self.vsys)
            self.parser = CommandParser(self.vsys, self.engine)
            self._clear_console()
            self.fw_var.set(False)
            self.ids_var.set(False)
            self.hp_var.set(False)
            self._refresh_indicators()
            self._log("[SYS] New session started. System reset to defaults.", "system")
            self._log(f"[SYS] Target IP: {self.vsys.target_ip}", "system")

    def _show_help(self):
        self._log_lines(HELP_TEXT.splitlines())

    # ─────────────────────────────────────────────────────────
    #  WELCOME MESSAGE
    # ─────────────────────────────────────────────────────────
    def _welcome(self):
        lines = [
            "╔═══════════════════════════════════════════════════════╗",
            "║      CYBER ATTACK vs DEFENSE LAB  v1.0                ║",
            "║      Educational Simulation — No Real Network I/O     ║",
            "╚═══════════════════════════════════════════════════════╝",
            "",
            "[SYS] Virtual target system initialised",
            f"[SYS] Target IP     : {self.vsys.target_ip}",
            f"[SYS] Attacker IP   : {self.vsys.attacker_ip}",
            f"[SYS] Default pass  : admin123",
            "",
            "[*] Quick start:",
            "    1. (Defender) Enable Firewall + IDS in the right panel",
            "    2. (Attacker) Click SCAN → PORT SCAN → BRUTE FORCE",
            "    3. If access granted → click 'LS' or 'CAT secrets.txt'",
            "    4. Terminal: type 'help' for all commands",
            "",
        ]
        self._log_lines(lines)

    # ─────────────────────────────────────────────────────────
    #  TOOLTIP HELPER
    # ─────────────────────────────────────────────────────────
    def _bind_tooltip(self, widget, text: str):
        tip_win = None

        def show(event):
            nonlocal tip_win
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + widget.winfo_height() + 4
            tip_win = tk.Toplevel(widget)
            tip_win.wm_overrideredirect(True)
            tip_win.wm_geometry(f"+{x}+{y}")
            tk.Label(
                tip_win, text=text,
                bg=C["border"], fg=C["text"],
                font=self.font_label, padx=6, pady=3
            ).pack()

        def hide(event):
            nonlocal tip_win
            if tip_win:
                tip_win.destroy()
                tip_win = None

        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = CyberLabApp()
    app.mainloop()
