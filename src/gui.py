import queue
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext

from config.wikibase_setup import CONFIG_FILE, create_login
from config.wikibase_setup import apply as apply_config
from config.wikibase_setup import load as load_config
from config.wikibase_setup import sanitize as sanitize_config
from config.wikibase_setup import save as save_config
from fix_statement_redirects import run_fix_statement_redirects
from resolve_double_redirects import run_resolve_double_redirects


class RedirectCleanupGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Wikibase Redirect Cleanup")
        self.root.geometry("800x600")
        self.root.minsize(300, 200)

        self.task_running = False

        # --- Wikibase setup frame ---
        setup_frame = tk.Frame(root)
        setup_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        tk.Label(setup_frame, text="Username:").pack(side=tk.LEFT)
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(setup_frame, textvariable=self.username_var, width=20)
        username_entry.pack(side=tk.LEFT, padx=(4, 16))

        tk.Label(setup_frame, text="Botpassword:").pack(side=tk.LEFT)
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(
            setup_frame, textvariable=self.password_var, width=20, show="*"
        )
        password_entry.pack(side=tk.LEFT, padx=(4, 0))

        button_settings = tk.Button(
            setup_frame,
            text="Wikibase Instance Config",
            command=self.open_wikibase_settings,
            width=22,
        )
        button_settings.pack(side=tk.RIGHT)

        # --- Buttons frame ---
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        button_single_redirects = tk.Button(
            button_frame,
            text="Fix statement redirects",
            command=lambda: self.run_script("fix_statement_redirects"),
            width=22,
        )
        button_single_redirects.pack(side=tk.LEFT, padx=(0, 10))

        button_double_redirects = tk.Button(
            button_frame,
            text="Resolve double redirects",
            command=lambda: self.run_script("resolve_double_redirects"),
            width=22,
        )
        button_double_redirects.pack(side=tk.LEFT)

        self.cancel_event: threading.Event | None = None
        self.button_cancel = tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel_task,
            width=22,
            state=tk.DISABLED,
            fg="red",
        )
        self.button_cancel.pack(side=tk.RIGHT)

        # --- Error log path ---
        log_frame = tk.Frame(root)
        log_frame.pack(fill=tk.X, padx=10, pady=(8, 0))

        tk.Label(log_frame, text="Error CSV log (optional):").pack(side=tk.LEFT)
        self.log_path_var = tk.StringVar()
        log_entry = tk.Entry(log_frame, textvariable=self.log_path_var, width=50)
        log_entry.pack(side=tk.LEFT, padx=(8, 8), fill=tk.X, expand=True)
        button_browse = tk.Button(
            log_frame, text="Browse...", command=self.browse_log_path
        )
        button_browse.pack(side=tk.LEFT)

        # --- Output text area ---
        self.text_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))

        # --- Load config from file (or create file with defaults) ---
        config = sanitize_config(load_config())
        apply_config(config)
        if not CONFIG_FILE.exists():
            save_config(config)

        # --- Queue for thread-safe output ---
        self.queue: queue.Queue[str] = queue.Queue()
        self.root.after(100, self.poll_queue)

        # --- Keep list of buttons for easy enabling / disabling ---
        self.buttons = [
            button_settings,
            button_single_redirects,
            button_double_redirects,
            button_browse,
        ]

    def cancel_task(self) -> None:
        if self.cancel_event is not None:
            self.queue.put(
                "--- Cancellation requested — finishing current item then stopping... ---"
            )
            self.cancel_event.set()
            self.button_cancel.config(state=tk.DISABLED)

    def browse_log_path(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.log_path_var.set(path)

    def open_wikibase_settings(self) -> None:
        """Open a settings dialog to view / edit the Wikibase configuration."""
        current_config = sanitize_config(load_config())

        dialog = tk.Toplevel(self.root)
        dialog.title("Wikibase Settings")
        dialog.resizable(False, False)

        fields = [
            ("DEFAULT_LANGUAGE", "Default language"),
            ("WIKIBASE_URL", "Wikibase URL"),
            ("MEDIAWIKI_API_URL", "MediaWiki API URL"),
            ("MEDIAWIKI_INDEX_URL", "MediaWiki index URL"),
            ("MEDIAWIKI_REST_URL", "MediaWiki REST URL"),
            ("SPARQL_ENDPOINT_URL", "SPARQL endpoint URL"),
        ]

        entries = {}
        for row, (key, label) in enumerate(fields):
            tk.Label(dialog, text=label + ":", anchor="e").grid(
                row=row, column=0, sticky="e", padx=(10, 4), pady=4
            )
            var = tk.StringVar(value=current_config.get(key, ""))
            entry = tk.Entry(dialog, textvariable=var, width=70)
            entry.grid(row=row, column=1, sticky="we", padx=(0, 10), pady=4)
            entries[key] = var

        # Config file location
        separator_row = len(fields)
        tk.Frame(dialog, height=2, relief="sunken", bd=1).grid(
            row=separator_row, column=0, columnspan=2, sticky="we", padx=10, pady=(8, 4)
        )
        tk.Label(dialog, text="Config file:", anchor="e", width=24).grid(
            row=separator_row + 1, column=0, sticky="e", padx=(10, 4), pady=2
        )
        tk.Label(
            dialog,
            text=str(CONFIG_FILE),
            anchor="w",
            fg="gray",
            font=("Consolas", 9),
        ).grid(row=separator_row + 1, column=1, sticky="w", padx=(0, 10), pady=2)

        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=separator_row + 2, column=0, columnspan=2, pady=(10, 10))

        def do_save() -> None:
            new_config = {key: var.get() for key, var in entries.items()}
            new_config = sanitize_config(new_config)
            save_config(new_config)
            apply_config(new_config)
            dialog.destroy()
            self.queue.put("Settings saved and applied.")

        tk.Button(btn_frame, text="Save", width=12, command=do_save).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        tk.Button(btn_frame, text="Cancel", width=12, command=dialog.destroy).pack(
            side=tk.LEFT
        )

    def write_output(self, text: str) -> None:
        """Insert text into the output area (must be called from the main thread)."""
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state="disabled")

    def poll_queue(self) -> None:
        """Periodically check the queue for new output from worker threads."""
        try:
            while True:
                msg = self.queue.get_nowait()
                self.write_output(msg)
        except queue.Empty:
            pass
        self.root.after(100, self.poll_queue)

    def on_task_done(self) -> None:
        """Re-enable buttons when a task finishes."""
        self.task_running = False
        self.cancel_event = None
        self.queue.put("--- Task finished ---")
        self.enable_buttons(True)

    def enable_buttons(self, enabled: bool) -> None:
        for button in self.buttons:
            button.config(state="normal" if enabled else "disabled")
        self.button_cancel.config(state="normal" if not enabled else "disabled")

    def run_script(self, script_name: str) -> None:
        # Validate credentials
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            self.queue.put("Please enter both username and password.")
            return

        if self.task_running:
            self.queue.put("A task is already running. Please wait.")
            return

        self.task_running = True
        self.cancel_event = threading.Event()
        self.enable_buttons(False)

        error_log_path = self.log_path_var.get().strip() or None

        self.queue.put(f"--- Starting: {script_name} ---")

        thread = threading.Thread(
            target=self._run_script_thread,
            args=(script_name, error_log_path, username, password),
            daemon=True,
        )
        thread.start()

    def _run_script_thread(
        self,
        script_name: str,
        error_log_path: str | None,
        username: str,
        password: str,
    ) -> None:
        try:
            login = create_login(username, password)
            if script_name == "fix_statement_redirects":
                run_fix_statement_redirects(
                    login,
                    output=self.queue.put,
                    error_log_path=error_log_path,
                    cancel_event=self.cancel_event,
                )
            elif script_name == "resolve_double_redirects":
                run_resolve_double_redirects(
                    login,
                    output=self.queue.put,
                    error_log_path=error_log_path,
                    cancel_event=self.cancel_event,
                )
        except Exception as exc:
            self.queue.put(f"Unhandled error: {exc}")
        finally:
            # Schedule the "task done" callback back on the main thread
            self.root.after(0, self.on_task_done)


def main() -> None:
    root = tk.Tk()
    RedirectCleanupGUI(root)  # reference kept by root's event loop
    root.mainloop()


if __name__ == "__main__":
    main()
