// Full Adder Module in Verilog
module full_adder (
    input wire A,       // First input bit
    input wire B,       // Second input bit
    input wire Cin,     // Carry input
    output wire Sum,    // Sum output
    output wire Cout    // Carry output
);

    // Logic for Sum and Carry Output
    assign Sum = A ^ B ^ Cin;             // XOR for Sum
    assign Cout = (A & B) | (B & Cin) | (A & Cin); // Carry generation

endmodule
