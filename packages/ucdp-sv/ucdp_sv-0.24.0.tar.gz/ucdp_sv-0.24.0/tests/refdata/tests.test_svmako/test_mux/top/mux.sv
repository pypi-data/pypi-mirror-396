// =============================================================================
//
//   @generated @fully-generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
//
//  MIT License
//
//  Copyright (c) 2024-2025 nbiotcloud
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy
//  of this software and associated documentation files (the "Software"), to deal
//  in the Software without restriction, including without limitation the rights
//  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//  copies of the Software, and to permit persons to whom the Software is
//  furnished to do so, subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
//  SOFTWARE.
//
// =============================================================================
//
// Update via:  ucdp gen top.mux
//
// Library:     top
// Module:      mux
// Data Model:  MuxMod
//              top/mux.py
//
// =============================================================================

`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden

module mux (
  input  wire  [3:0] a0_i,
  input  wire  [3:0] b0_i,
  input  wire  [3:0] c0_i,
  output logic [3:0] q0_o,
  input  wire  [2:0] sel_i,
  input  wire  [7:0] a1_i,
  input  wire  [7:0] b1_i,
  input  wire  [7:0] c1_i,
  output logic [7:0] q1_o,
  output logic [7:0] q2_o,
  output logic [3:0] q4_o
);



  // ------------------------------------------------------
  //  Local Parameter
  // ------------------------------------------------------
  // my_enum
  localparam integer       my_enum_width_p   = 3;    // Width in Bits
  localparam logic   [2:0] my_enum_min_p     = 3'h0; // Minimal Value
  localparam logic   [2:0] my_enum_max_p     = 3'h7; // Maximal Value
  localparam logic   [2:0] my_enum_one_e     = 3'h0;
  localparam logic   [2:0] my_enum_two_e     = 3'h1;
  localparam logic   [2:0] my_enum_three_e   = 3'h2;
  localparam logic   [2:0] my_enum_default_p = 3'h0; // Default Value


  // ------------------------------------------------------
  //  Signals
  // ------------------------------------------------------
  logic [2:0] sel_s;
  logic [3:0] q3_s;


  // ------------------------------------------------------
  //  comment
  // ------------------------------------------------------
  always_comb begin : proc_main
    // defaults
    q0_o = 4'h8;
    q1_o = c1_i;
    q3_s = 4'h0;
    q4_o = 4'h0;

    case (sel_s) inside
      3'h1: begin
        q0_o = a0_i;
        q1_o = b1_i;
      end
      3'h2: begin
        q0_o = b0_i;
      end
      3'h4: begin
        q0_o = c0_i;
        q3_s = c0_i;
      end
      default: begin // 3'h0
        q1_o = a1_i;
      end
    endcase

    case (sel_i) inside
      my_enum_two_e: begin
        q4_o = b0_i;
      end
      3'h3: begin
        q4_o = a0_i;
      end
    endcase
  end


  // ------------------------------------------------------
  //  Multiplexer slim
  // ------------------------------------------------------
  always_comb begin : proc_slim
    // defaults
    q2_o = 8'h00;

    case (sel_s) inside
      3'h1: begin
        q2_o = a1_i;
      end
    endcase
  end


  // ------------------------------------------------------
  //  Multiplexer empty
  // ------------------------------------------------------
  always_comb begin : proc_empty
    // defaults

  end

endmodule // mux

`default_nettype wire
`end_keywords

// =============================================================================
//
//   @generated @fully-generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
