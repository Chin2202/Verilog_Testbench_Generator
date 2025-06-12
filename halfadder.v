module half_adder (
    input wire A,
    input wire B,
    output wire SUM,
    output wire CARRY
);
    assign SUM = A ^ B;
    assign CARRY = A & B;
endmodule
