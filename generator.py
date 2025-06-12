import os
import re
import subprocess
import zipfile
from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox
from rich.console import Console

console = Console()

APP_NAME = "VeriTB Studio"
APP_VERSION = "v5.0"
THEME_COLOR = "#1E1E2F"
ACCENT_COLOR = "#2ECC71"
TEXT_COLOR = "#FFFFFF"


def extract_modules(verilog_file):
    with open(verilog_file, 'r') as f:
        content = f.read()
    return re.findall(r"module\s+(\w+)\s*\(([^)]*)\)", content)


def parse_ports(ports_raw):
    inputs, outputs = [], []
    for line in ports_raw.split(','):
        line = line.strip()
        if line.startswith("input"):
            match = re.findall(r"\w+$", line)
            if match:
                inputs.append(match[0])
        elif line.startswith("output"):
            match = re.findall(r"\w+$", line)
            if match:
                outputs.append(match[0])
    return inputs, outputs


def generate_testbench(module_name, inputs, outputs, assertion_expr, num_tests=20):
    tb = f"`timescale 1ns / 1ps\n\n"
    tb += f"module {module_name}_tb;\n"
    for sig in inputs:
        tb += f"  reg {sig};\n"
    for sig in outputs:
        tb += f"  wire {sig};\n"

    tb += f"\n  {module_name} DUT (\n"
    tb += ",\n".join([f"    .{sig}({sig})" for sig in inputs + outputs]) + "\n  );\n"

    tb += """
  initial begin
    $dumpfile("wave.vcd");
    $dumpvars(0, DUT);
  end

  initial begin
"""
    for sig in inputs:
        tb += f"    {sig} = 0;\n"

    tb += f"    repeat ({num_tests}) begin\n"
    for sig in inputs:
        tb += f"      {sig} = $random % 2;\n"
    tb += f"      #1;\n      if ({assertion_expr}) $display(\"ERROR: Assertion failed at inputs...\");\n      #9;\n    end\n"

    tb += "    #50;\n    $finish;\n  end\nendmodule"
    return tb


def generate_gtkw_file(gtkw_file, signals):
    with open(gtkw_file, "w") as f:
        f.write("$dumpfile wave.vcd\n")
        f.write("$dumpon\n")
        for sig in signals:
            f.write(f"*signal /{sig}\n")
        f.write("$end\n")


def simulate(verilog_file, tb_file, gtkw_file, output_dir):
    exe_file = os.path.join(output_dir, "simulation.out")
    log_file = os.path.join(output_dir, "simulation.log")
    try:
        with open(log_file, "w") as log:
            subprocess.run(["iverilog", "-o", exe_file, verilog_file, tb_file], check=True, stdout=log, stderr=log)
            subprocess.run(["vvp", exe_file], check=True, stdout=log, stderr=log)
        subprocess.run(["gtkwave", "wave.vcd", gtkw_file])
        messagebox.showinfo("Simulation Complete", f"Simulation finished. See log: {log_file}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", f"Simulation failed. See log: {log_file}")


def create_zip(files, output_zip):
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for file in files:
            if os.path.exists(file):
                zipf.write(file, arcname=os.path.basename(file))


def run_gui():
    def select_file():
        file_path = filedialog.askopenfilename(title="Select Verilog File", filetypes=[("Verilog Files", "*.v")])
        if not file_path:
            return
        modules = extract_modules(file_path)
        if not modules:
            messagebox.showerror("Error", "No modules found in the Verilog file.")
            return
        module_names = [m[0] for m in modules]
        module_dropdown['menu'].delete(0, 'end')
        for name in module_names:
            module_dropdown['menu'].add_command(label=name, command=lambda value=name: selected_module.set(value))
        selected_module.set(module_names[0])
        selected_file.set(file_path)

    def generate_and_simulate():
        file_path = selected_file.get()
        if not file_path:
            messagebox.showerror("Error", "Select a Verilog file first.")
            return
        module_to_test = selected_module.get()
        modules = extract_modules(file_path)
        ports_raw = next((p for n, p in modules if n == module_to_test), None)
        if not ports_raw:
            messagebox.showerror("Error", "Selected module not found.")
            return

        try:
            num_tests = int(num_tests_var.get())
        except ValueError:
            num_tests = 20

        assertion_expr = assertion_text.get("1.0", END).strip()
        inputs, outputs = parse_ports(ports_raw)
        tb = generate_testbench(module_to_test, inputs, outputs, assertion_expr, num_tests)
        output_dir = os.path.dirname(file_path)
        tb_file = os.path.join(output_dir, f"{module_to_test}_tb.v")
        gtkw_file = os.path.join(output_dir, "default.gtkw")
        with open(tb_file, "w") as f:
            f.write(tb)
        generate_gtkw_file(gtkw_file, [f"DUT.{sig}" for sig in inputs + outputs])
        simulate(file_path, tb_file, gtkw_file, output_dir)

        generated_files.extend([file_path, tb_file, gtkw_file, os.path.join(output_dir, "simulation.log"), os.path.join(output_dir, "wave.vcd")])

    def export_zip():
        if not generated_files:
            messagebox.showerror("Error", "No generated files to export.")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"VeriTB_{timestamp}.zip"
        zip_file = filedialog.asksaveasfilename(title="Save ZIP As", defaultextension=".zip", initialfile=default_name, filetypes=[("ZIP files", "*.zip")])
        if zip_file:
            create_zip(generated_files, zip_file)
            messagebox.showinfo("ZIP Created", f"ZIP created: {zip_file}")

    root = Tk()
    root.title(f"{APP_NAME} {APP_VERSION}")
    root.configure(bg=THEME_COLOR)
    root.geometry("750x600")

    global generated_files
    generated_files = []

    selected_file = StringVar()
    selected_module = StringVar()

    Label(root, text=APP_NAME, font=("Arial", 20, "bold"), fg=ACCENT_COLOR, bg=THEME_COLOR).pack(pady=10)
    Button(root, text="Select Verilog File", command=select_file, bg=ACCENT_COLOR, fg="white", width=25).pack(pady=5)
    Label(root, textvariable=selected_file, bg=THEME_COLOR, fg=TEXT_COLOR, wraplength=700).pack()

    Label(root, text="Module to Generate TB For:", fg=TEXT_COLOR, bg=THEME_COLOR).pack(pady=5)
    module_dropdown = OptionMenu(root, selected_module, '')
    module_dropdown.config(bg="white")
    module_dropdown.pack(pady=5)

    Label(root, text="Number of Random Tests:", fg=TEXT_COLOR, bg=THEME_COLOR).pack()
    num_tests_var = StringVar(value="20")
    Entry(root, textvariable=num_tests_var, width=10).pack(pady=5)

    Label(root, text="Custom Assertion (Verilog syntax):", fg=TEXT_COLOR, bg=THEME_COLOR).pack()
    assertion_text = Text(root, height=4, width=80)
    assertion_text.insert("1.0", "Y !== (A | B)")
    assertion_text.pack(pady=5)

    Button(root, text="Generate TB & Simulate", command=generate_and_simulate, bg=ACCENT_COLOR, fg="white", width=30).pack(pady=15)
    Button(root, text="Export All as ZIP", command=export_zip, bg="darkgreen", fg="white", width=30).pack(pady=10)

    Label(root, text=f"{APP_NAME} {APP_VERSION} | Developed by You", fg="gray", bg=THEME_COLOR).pack(side=BOTTOM, pady=10)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
