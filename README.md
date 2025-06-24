# Verilog Testbench Generator AKA VeriTB STUDIO
Verilog Testbench Generator is a Python-based tool designed to simplify the creation of Verilog testbenches for digital circuit verification. It generates ready-to-run Verilog testbench files for given module descriptions, reducing manual errors and accelerating your verification process.

Features
- Generate customizable Verilog testbenches
- Supports multiple inputs, outputs, and modules
- Generates output as `.v` files
- Integrated with GTKWave for simulation viewing
- Simple GUI interface (using Tkinter)

## Installation

```bash
git clone https://github.com/Chin2202/Verilog_Testbench_Generator.git
cd Verilog_Testbench_Generator
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```
## Usage
1.Run the GUI:
bash
Copy
Edit
python generator.py
2.Enter your Verilog module details.
3.Generate your testbench.
4.Simulate using your preferred Verilog simulator (e.g., Icarus Verilog).
5.View waveforms using GTKWave.

-Example
Given a Verilog module like:

verilog
Copy
Edit
module or_gate (
    input wire A,
    input wire B,
    output wire Y
);
    assign Y = A | B;
endmodule
→ This tool will generate a corresponding or_gate_tb.v for simulation.

## Requirements
1.Python 3.x
2.Icarus Verilog
3.GTKWave

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT

## Authors
Chinmayi C{https://github.com/Chin2202}
Aditya M Khiroji{https://github.com/adityamk123}
