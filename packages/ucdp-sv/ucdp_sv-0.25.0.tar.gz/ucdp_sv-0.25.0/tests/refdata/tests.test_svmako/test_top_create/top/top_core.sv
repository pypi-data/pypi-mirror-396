// GENERATE INPLACE BEGIN head() ===============================================
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
// Update via:  ucdp gen top.top
//
// Library:     top
// Module:      top_core
// Data Model:  TopCoreMod
//              top/top.py
//
// =============================================================================

`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden

module top_core #(
  parameter integer            param_p = 10,
  parameter integer            width_p = 8,
  parameter logic signed [7:0] other_p = 8'shFD
) (
  // main_i: Clock and Reset
  input  wire                 main_clk_i,                        // Clock
  input  wire                 main_rst_an_i,                     // Async Reset (Low-Active)
  // -
  input  wire   [param_p-1:0] p_i,
  output logic  [param_p-1:0] p_o,
  input  bit    [width_p-1:0] data_i,
  output logic  [width_p-1:0] data_o,
  `ifdef ASIC
  output logic  [8:0]         brick_o,
  `endif // ASIC
  input  wire   [2:0]         some_i,
  input  wire   [1:0]         bits_i,
  // key_i
  input  wire                 key_valid_i,                       // clk: main_clk_i
  output logic                key_accept_o,                      // clk: main_clk_i
  input  wire   [8:0]         key_data_i,                        // clk: main_clk_i
  // -
  input  wire                 open_rail_i,
  input  string               open_string_i,
  input  wire   [5:0]         open_array_i   [3:0],
  input  wire   [5:0]         open_matrix_i  [0:1][0:param_p-1],
  input  wire   [5:0]         matrix_down_i  [0:1][param_p-1:0],
  output wire                 open_rail_o,
  output string               open_string_o,
  output logic  [5:0]         open_array_o   [0:3],
  output logic  [5:0][0:3]    open_matrix_o  [0:1],
  input  wire   [6:0]         nosuffix0,
  output logic  [6:0]         nosuffix1,
  input  wire   [7:0]         array_i        [0:param_p-1],
  input  wire   [7:0]         array_open_i   [0:7],
  // intf_i: RX/TX
  output logic                intf_rx_o,                         // RX
  input  wire                 intf_tx_i
);



  // ------------------------------------------------------
  //  Signals
  // ------------------------------------------------------
  logic   [width_p-1:0] one_s;
  bit     [width_p-1:0] two_s;
  integer               integer_s;
  int                   int_s;
  real                  float_s;
  real                  double_s;

// GENERATE INPLACE END head ===================================================

// Add your hand-written code here - remove this line afterwards

// GENERATE INPLACE BEGIN tail() ===============================================
endmodule // top_core

`default_nettype wire
`end_keywords
// GENERATE INPLACE END tail ===================================================
