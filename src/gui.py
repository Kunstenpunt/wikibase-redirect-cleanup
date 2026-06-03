import queue
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext

from config.wikibase_setup import create_login
from fix_statement_redirects import run_fix_statement_redirects
from resolve_double_redirects import run_resolve_double_redirects


class OutputQueue:
    """Wraps a queue.Queue so it can be passed as the `output` callback to scripts."""

    def __init__(self, q: queue.Queue):
        self.q = q

    def write(self, message: str):
        self.q.put(str(message))

    def flush(self):
        pass


class RedirectCleanupGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Wikibase Redirect Cleanup")
        self.root.geometry("800x600")
        self.root.minsize(300, 200)

        self.task_running = False

        # --- Credentials frame ---
        cred_frame = tk.Frame(root)
        cred_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        tk.Label(cred_frame, text="Username:").pack(side=tk.LEFT)
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(cred_frame, textvariable=self.username_var, width=20)
        username_entry.pack(side=tk.LEFT, padx=(4, 16))

        tk.Label(cred_frame, text="Botpassword:").pack(side=tk.LEFT)
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(
            cred_frame, textvariable=self.password_var, width=20, show="*"
        )
        password_entry.pack(side=tk.LEFT, padx=(4, 0))

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

        # --- Error log path ---
        log_frame = tk.Frame(root)
        log_frame.pack(fill=tk.X, padx=10, pady=(8, 0))

        tk.Label(log_frame, text="Error CSV log (optional):").pack(side=tk.LEFT)
        self.log_path_var = tk.StringVar()
        log_entry = tk.Entry(log_frame, textvariable=self.log_path_var, width=50)
        log_entry.pack(side=tk.LEFT, padx=(8, 8), fill=tk.X, expand=True)
        btn_browse = tk.Button(
            log_frame, text="Browse...", command=self.browse_log_path
        )
        btn_browse.pack(side=tk.LEFT)

        # --- Output text area ---
        self.text_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))

        # --- Queue for thread-safe output ---
        self.queue = queue.Queue()
        self.root.after(100, self.poll_queue)

    def browse_log_path(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.log_path_var.set(path)

    def write_output(self, text: str):
        """Insert text into the output area (must be called from the main thread)."""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def poll_queue(self):
        """Periodically check the queue for new output from worker threads."""
        try:
            while True:
                msg = self.queue.get_nowait()
                self.write_output(msg)
        except queue.Empty:
            pass
        self.root.after(100, self.poll_queue)

    def on_task_done(self):
        """Re-enable buttons when a task finishes."""
        self.task_running = False
        self.write_output("--- Task finished ---")
        self.enable_buttons(True)

    def enable_buttons(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        for child in self.root.winfo_children():
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Button):
                        grandchild.config(state=state)

    def run_script(self, script_name: str):
        # Validate credentials
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            self.write_output("Please enter both username and password.")
            return

        if self.task_running:
            self.write_output("A task is already running. Please wait.")
            return

        self.task_running = True
        self.enable_buttons(False)

        error_log_path = self.log_path_var.get().strip() or None

        # Clear previous output
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)

        output_writer = OutputQueue(self.queue)

        self.write_output(f"--- Starting: {script_name} ---")

        thread = threading.Thread(
            target=self._run_script_thread,
            args=(script_name, output_writer, error_log_path, username, password),
            daemon=True,
        )
        thread.start()

    def _run_script_thread(
        self,
        script_name: str,
        output_writer: OutputQueue,
        error_log_path: str | None,
        username: str,
        password: str,
    ):
        try:
            login = create_login(username, password)
            if script_name == "fix_statement_redirects":
                run_fix_statement_redirects(
                    login, output=output_writer.write, error_log_path=error_log_path
                )
            elif script_name == "resolve_double_redirects":
                run_resolve_double_redirects(
                    login, output=output_writer.write, error_log_path=error_log_path
                )
        except Exception as exc:
            output_writer.write(f"Unhandled error: {exc}")
        finally:
            # Schedule the "task done" callback back on the main thread
            self.root.after(0, self.on_task_done)


def main():
    root = tk.Tk()
    RedirectCleanupGUI(root)  # reference kept by root's event loop
    root.mainloop()


if __name__ == "__main__":
    main()
