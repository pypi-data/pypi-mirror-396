`timescale 1ns/1ps

module signed_adder #(
  parameter integer DATA_WIDTH = 8
) (
  input  logic signed [DATA_WIDTH-1:0] A,
  input  logic signed [DATA_WIDTH-1:0] B,
  output logic signed [DATA_WIDTH:0]   X
);

  assign X = A + B;

endmodule
