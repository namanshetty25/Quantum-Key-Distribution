import qnode
from BB84 import simulate_bb84_stream

import threading
import time
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from mpl_toolkits.mplot3d import Axes3D  # needed for 3D projection
import matplotlib.pyplot as plt
from matplotlib import cm

def bit_basis_to_bloch_vector(bit, basis):
    if basis == 'Z':
        return np.array([0, 0, 1 if bit == 0 else -1])
    elif basis == 'X':
        return np.array([1 if bit == 0 else -1, 0, 0])
    else:
        return np.array([0, 0, 0])

class BB84App:
    def __init__(self, root):
        self.root = root
        root.title("BB84 Quantum Encryption")

        # Controls frame
        control = ttk.Frame(root, padding=8)
        control.grid(row=0, column=0, sticky="nw")

        self.batch_var = tk.BooleanVar(value=False)
        self.result_text = tk.StringVar()

        ttk.Label(control, text="Number of qubits:").grid(row=0, column=0, sticky="w")
        self.n_qubits_var = tk.IntVar(value=600)
        self.entry_nq = ttk.Entry(control, textvariable=self.n_qubits_var, width=10)
        self.entry_nq.grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(control, text="Eve prob (0-1):").grid(row=1, column=0, sticky="w")
        self.eve_prob_var = tk.DoubleVar(value=0.0)
        self.entry_eve = ttk.Entry(control, textvariable=self.eve_prob_var, width=10)
        self.entry_eve.grid(row=1, column=1, sticky="w", padx=6)

        ttk.Label(control, text="Test fraction:").grid(row=2, column=0, sticky="w")
        self.test_fraction_var = tk.DoubleVar(value=0.20)
        self.entry_tf = ttk.Entry(control, textvariable=self.test_fraction_var, width=10)
        self.entry_tf.grid(row=2, column=1, sticky="w", padx=6)

        # Buttons
        self.btn_run = ttk.Button(control, text="Run Single Trial", command=self.run_single)
        self.btn_run.grid(row=3, column=0, pady=6, sticky="w")
        self.btn_sweep = ttk.Button(control, text="Sweep Eve Prob (show curve)", command=self.run_sweep_thread)
        self.btn_sweep.grid(row=3, column=1, pady=6, sticky="w")
        self.btn_save = ttk.Button(control, text="Save Last Results CSV", command=self.save_csv)
        self.btn_save.grid(row=4, column=0, pady=6, sticky="w")

        ttk.Label(control, text="Trials per Eve point (for sweep):").grid(row=5, column=0, sticky="w")
        self.trials_var = tk.IntVar(value=5)
        self.entry_trials = ttk.Entry(control, textvariable=self.trials_var, width=10)
        self.entry_trials.grid(row=5, column=1, sticky="w", padx=6)

        ttk.Label(root, text="Trials (batch mode):").grid(row=3, column=0, sticky="w")
        entry_trials = ttk.Entry(root)
        entry_trials.insert(0, "50")
        entry_trials.grid(row=3, column=1)

        # Batch mode checkbox and button
        ttk.Checkbutton(root, text="Batch mode", variable=self.batch_var).grid(row=4, column=0, columnspan=2, sticky="w")
        self.btn_run = ttk.Button(root, text="Run Simulation", command=self.run_simulation)
        self.btn_run.grid(row=4, column=1, columnspan=2, pady=6, sticky="w")

        # Output frame
        out = ttk.Frame(root, padding=8)
        out.grid(row=0, column=1)

        self.text = tk.Text(out, width=60, height=12)
        self.text.grid(row=0, column=0, padx=6, pady=6)

        # Plot frame (matplotlib)
        plot_fr = ttk.Frame(root, padding=8)
        plot_fr.grid(row=1, column=0)

        self.fig = Figure(figsize=(3.5,4.5))
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.175)  # increase left margin (default ~0.125)
        self.ax.set_xlabel("Eve interception probability")
        self.ax.set_ylabel("Observed error rate")
        self.ax.set_ylim(0, 0.6)
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_fr)
        self.canvas.get_tk_widget().pack()

        # internal storage for last sweep results
        self.last_df = None

        # Lock for thread safety
        self._run_lock = threading.Lock()


        bloch_frame = ttk.Frame(root, padding=8)
        bloch_frame.grid(row=1, column=1, sticky="nsew")

        # Figure for Alice
        self.bloch_fig_alice = Figure(figsize=(3.5, 3.5))
        self.bloch_ax_alice = self.bloch_fig_alice.add_subplot(111, projection='3d')
        self.bloch_canvas_alice = FigureCanvasTkAgg(self.bloch_fig_alice, master=bloch_frame)
        self.bloch_canvas_alice.get_tk_widget().pack(side='left', fill='both', expand=True)

        # Figure for Bob
        self.bloch_fig_bob = Figure(figsize=(3.5, 3.5))
        self.bloch_ax_bob = self.bloch_fig_bob.add_subplot(111, projection='3d')
        self.bloch_canvas_bob = FigureCanvasTkAgg(self.bloch_fig_bob, master=bloch_frame)
        self.bloch_canvas_bob.get_tk_widget().pack(side='right', fill='both', expand=True)

        # Keep current vectors for animation
        self.current_bloch_vector_alice = np.array([0,0,1])
        self.current_bloch_vector_bob = np.array([0,0,1])
        self.animating = False

    def log(self, *args):
        self.text.insert("end", " ".join(map(str, args)) + "\n")
        self.text.see("end")

    def run_single(self):
        try:
            nq = int(self.n_qubits_var.get())
            eve_p = float(self.eve_prob_var.get())
            tf = float(self.test_fraction_var.get())
        except Exception as e:
            messagebox.showerror("Input error", str(e))
            return

        self.log(f"Running single BB84 trial: nq={nq}, eve_prob={eve_p:.3f}, test_frac={tf:.3f}")
        start = time.time()

        # create generator
        gen = simulate_bb84_stream(n_qubits=nq, eve_prob=eve_p, test_fraction=tf)
        res = None
        for data in gen:
            # you can optionally update Bloch sphere here per qubit:
            if not data.get("final", False):
                self.update_bloch_vector(data['alice_bit'], data['alice_basis'], data['bob_bit'], data['bob_basis'])
            else:
                res = data

        t = time.time() - start

        if res is None or res["observed_error_rate"] is None:
            self.log("No sifted bits produced (try larger n_qubits).")
            return

        # Use final dict result
        self.log(f"Observed error rate (on test subset): {res['observed_error_rate']:.4f}")
        self.log(f"Sift rate: {res['sift_rate']:.4f}  (sifted bits = {len(res['sifted_A'])})")
        pairs = list(zip(res['sifted_A'][:40], res['sifted_B'][:40]))
        self.log("First sifted bit pairs (Alice,Bob):", pairs)
        self.log(f"Time: {t:.3f} s\n")

        # store in last_df for possible save
        df = pd.DataFrame({
            "alice_sifted": res["sifted_A"],
            "bob_sifted": res["sifted_B"]
        })
        df["match"] = df["alice_sifted"] == df["bob_sifted"]
        self.last_df = df

    def draw_bloch_sphere(self, ax, vec, title=""):
        ax.clear()

        # Draw sphere surface
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x, y, z, color='lightblue', alpha=0.3, edgecolor='gray')

        # Draw axes
        ax.quiver(0, 0, 0, 1, 0, 0, color='r', arrow_length_ratio=0.1)
        ax.quiver(0, 0, 0, 0, 1, 0, color='g', arrow_length_ratio=0.1)
        ax.quiver(0, 0, 0, 0, 0, 1, color='b', arrow_length_ratio=0.1)
        ax.text(1.1, 0, 0, 'X', color='r')
        ax.text(0, 1.1, 0, 'Y', color='g')
        ax.text(0, 0, 1.1, 'Z', color='b')

        # Use passed vector
        vec = np.array(vec)

        # Draw qubit state vector
        ax.quiver(0, 0, 0, vec[0], vec[1], vec[2], color='m', arrow_length_ratio=0.1, linewidth=2)

        ax.set_xlim([-1, 1])
        ax.set_ylim([-1, 1])
        ax.set_zlim([-1, 1])
        ax.set_box_aspect([1, 1, 1])  # equal aspect ratio
        ax.set_title(title)
        ax.axis('off')


    def animate_bloch(self):
        if not self.animating:
            return

        angle = 0.1
        c, s = np.cos(angle), np.sin(angle)

        # Rotate Alice's vector
        x, y, z = self.current_bloch_vector_alice
        self.current_bloch_vector_alice = np.array([c*x - s*y, s*x + c*y, z])

        # Rotate Bob's vector
        x, y, z = self.current_bloch_vector_bob
        self.current_bloch_vector_bob = np.array([c*x - s*y, s*x + c*y, z])

        # Draw Alice Bloch sphere
        self.draw_bloch_sphere(self.bloch_ax_alice, self.current_bloch_vector_alice, title="Alice's Qubit")

        # Draw Bob Bloch sphere
        self.draw_bloch_sphere(self.bloch_ax_bob, self.current_bloch_vector_bob, title="Bob's Qubit")

        # Update both canvases
        self.bloch_canvas_alice.draw()
        self.bloch_canvas_bob.draw()

        self.root.after(100, self.animate_bloch)


    def update_bloch_vector(self, alice_bit, alice_basis, bob_bit=None, bob_basis=None):
        self.current_bloch_vector_alice = bit_basis_to_bloch_vector(alice_bit, alice_basis)
        if bob_bit is not None and bob_basis is not None:
            self.current_bloch_vector_bob = bit_basis_to_bloch_vector(bob_bit, bob_basis)


    def run_sweep_thread(self):
        if self._run_lock.locked():
            messagebox.showinfo("Busy", "A sweep is already running.")
            return

        # Start animation
        self.animating = True
        self.animate_bloch()

        def target():
            self.run_sweep()
            # Stop animation when done
            self.animating = False

        t = threading.Thread(target=target)
        t.daemon = True
        t.start()

    def run_sweep(self):
        with self._run_lock:
            try:
                nq = int(self.n_qubits_var.get())
                tf = float(self.test_fraction_var.get())
                trials = int(self.trials_var.get())
            except Exception as e:
                messagebox.showerror("Input error", str(e))
                return

            self.log(f"Starting sweep: nq={nq}, test_frac={tf}, trials/point={trials}")
            eve_probs = np.linspace(0.0, 1.0, 21)
            results = []

            self.ax.clear()
            self.ax.set_xlabel("Eve interception probability")
            self.ax.set_ylabel("Observed error rate")
            self.ax.set_ylim(0, 0.6)
            self.ax.grid(True)

            rng = np.random.default_rng()

            for p in eve_probs:
                errs = []
                sifts = []

                for _ in range(trials):
                    # Use the streaming simulation generator
                    gen = simulate_bb84_stream(n_qubits=nq, eve_prob=float(p), test_fraction=tf, rng=rng)
                    for data in gen:
                        if data.get("final"):
                            if data["observed_error_rate"] is None:
                                errs.append(0.0)
                            else:
                                errs.append(data["observed_error_rate"])
                            sifts.append(data["sift_rate"])

                            # Log final result of this trial
                            self.log(f"Eve={p:.2f} trial {_+1} complete, error rate: {data['observed_error_rate']}")
                        else:
                            # Update Bloch vector live during qubit processing
                            self.update_bloch_vector(data['alice_bit'], data['alice_basis'], data['bob_bit'], data['bob_basis'])

                mean_err = float(np.mean(errs))
                std_err = float(np.std(errs))
                mean_sift = float(np.mean(sifts))
                results.append((p, mean_err, std_err, mean_sift))

                # Update plot progressively
                xs = [r[0] for r in results]
                ys = [r[1] for r in results]
                yerr = [r[2] for r in results]
                self.ax.clear()
                self.ax.set_xlabel("Eve interception probability")
                self.ax.set_ylabel("Observed error rate")
                self.ax.set_ylim(0, 0.6)
                self.ax.grid(True)
                self.ax.errorbar(xs, ys, yerr=yerr, marker='o', linestyle='-')
                self.canvas.draw()
                self.root.update()
                time.sleep(0.01)

                self.log(f"Eve={p:.2f} -> mean_err={mean_err:.3f} std={std_err:.3f} mean_sift={mean_sift:.3f}")

            df = pd.DataFrame(results, columns=["eve_prob", "mean_error_rate", "std_error_rate", "mean_sift_rate"])
            self.last_df = df
            self.log("Sweep complete.\n")


    def run_simulation(self):
        n_qubits = self.n_qubits_var.get()
        eve_prob = self.eve_prob_var.get()
        test_fraction = self.test_fraction_var.get()
        trials = self.trials_var.get() if self.batch_var.get() else 1

        if self.batch_var.get():
            from runner import batch_run_bb84
            res = batch_run_bb84(n_qubits, eve_prob, test_fraction, trials)
            self.result_text.set(
                f"[BATCH] Eve={eve_prob:.2f} | Mean Err={res['mean_error']:.4f} ± {res['std_error']:.4f} | Mean Sift={res['mean_sift']:.4f}"
            )
        else:
            gen = simulate_bb84_stream(n_qubits, eve_prob, test_fraction)
            res = None
            for data in gen:
                if data.get("final", False):
                    res = data
            if res is None:
                messagebox.showerror("Error", "No final result from simulation.")
                return
            self.result_text.set(
                f"[SINGLE] Eve={eve_prob:.2f} | Err={res['observed_error_rate']:.4f} | Sift={res['sift_rate']:.4f}"
            )

    def save_csv(self):
        if self.last_df is None:
            messagebox.showinfo("No data", "No results available to save. Run a trial or sweep first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        self.last_df.to_csv(path, index=False)
        messagebox.showinfo("Saved", f"Saved CSV to {path}")

    