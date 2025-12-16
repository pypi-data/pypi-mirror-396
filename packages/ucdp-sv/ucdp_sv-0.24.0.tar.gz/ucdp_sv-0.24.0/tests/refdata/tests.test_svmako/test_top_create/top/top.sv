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
// Update via:  ucdp gen top.top
//
// Library:     top
// Module:      top
// Data Model:  TopMod
//              top/top.py
// Submodules:
//              clk_gate u_clk_gate
//              top_core u_core
//              sync u_sync
//              sync *
//              sub u_sub0
//
// =============================================================================

`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden

module top #(
  parameter integer               param_p   = 10,
  parameter integer               width_p   = $clog2(param_p + 1),
  parameter logic   [param_p-1:0] default_p = {param_p {1'b0}}
) (
  // main_i: Clock and Reset
  input  wire                main_clk_i,    // Clock
  input  wire                main_rst_an_i, // Async Reset (Low-Active)
  // intf_i: RX/TX
  output logic               intf_rx_o,     // ASYNC - RX
  input  wire                intf_tx_i,     // ASYNC
  // bus_i
  input  wire  [1:0]         bus_trans_i,   // clk: main_clk_i
  input  wire  [31:0]        bus_addr_i,    // clk: main_clk_i
  input  wire                bus_write_i,   // clk: main_clk_i
  input  wire  [31:0]        bus_wdata_i,   // clk: main_clk_i
  output logic               bus_ready_o,   // clk: main_clk_i
  output logic               bus_resp_o,    // clk: main_clk_i
  output logic [31:0]        bus_rdata_o,   // clk: main_clk_i
  `ifdef ASIC
  // -
  output logic [8:0]         brick_o,
  `endif // ASIC
  input  wire  [param_p-1:0] data_i,
  output logic [width_p-1:0] cnt_o,
  // key_i
  input  wire                key_valid_i,   // clk: main_clk_i
  output logic               key_accept_o,  // clk: main_clk_i
  input  wire  [8:0]         key_data_i,    // clk: main_clk_i
  // -
  inout  wire  [3:0]         bidir_io,
  input  wire                rail_i,
  output wire                rail_o,
  inout  wire                rail_io
  `ifdef ASIC
  ,
  output logic [8:0]         value_o
  `endif // ASIC
);



  // ------------------------------------------------------
  //  Local Parameter
  // ------------------------------------------------------
  localparam logic [param_p-1:0] const_c = default_p / 'd2;


  // ------------------------------------------------------
  //  Signals
  // ------------------------------------------------------
  // key_s
  logic               key_valid_s;
  logic               key_accept_s;
  logic [8:0]         key_data_s;
  // -
  logic [3:0]         bidir_s;
  logic               clk_s;                       // Clock
  logic [7:0]         array_s       [0:param_p-1];
  logic [8:0]         data_r;
  logic [param_p-1:0] data2_r;


  // ------------------------------------------------------
  //  glbl.clk_gate: u_clk_gate
  // ------------------------------------------------------
  clk_gate u_clk_gate (
    .clk_i(main_clk_i), // Clock
    .clk_o(clk_s     ), // Clock
    .ena_i(1'b0      )  // TODO - Enable
  );


  // ------------------------------------------------------
  //  top.top_core: u_core
  // ------------------------------------------------------
  top_core #(
    .param_p(10            ),
    .width_p($clog2(10 + 1))
  ) u_core (
    .main_clk_i   (clk_s             ), // Clock
    .main_rst_an_i(main_rst_an_i     ), // Async Reset (Low-Active)
    .p_i          ({10 {1'b0}}       ), // TODO
    .p_o          (                  ), // TODO
    .data_i       ({8 {1'b0}}        ), // TODO
    .data_o       (                  ), // TODO
    `ifdef ASIC
    .brick_o      (brick_o           ),
    `endif // ASIC
    .some_i       (3'h4              ),
    .bits_i       (data_i[3:2]       ),
    .key_valid_i  (key_valid_i       ), // clk: main_clk_i
    .key_accept_o (key_accept_o      ), // clk: main_clk_i
    .key_data_i   (key_data_i        ), // clk: main_clk_i
    .open_rail_i  (                  ), // RAIL - TODO
    .open_string_i(""                ), // TODO
    .open_array_i ('{4{6'h00}}       ), // TODO
    .open_matrix_i('{2{'{10{6'h00}}}}), // TODO
    .matrix_down_i('{2{'{10{6'h00}}}}), // TODO
    .open_rail_o  (                  ), // RAIL - TODO
    .open_string_o(                  ), // TODO
    .open_array_o (                  ), // TODO
    .open_matrix_o(                  ), // TODO
    .nosuffix0    (7'h00             ), // I - TODO
    .nosuffix1    (                  ), // O - TODO
    .array_i      (array_s           ),
    .array_open_i ('{8{8'h00}}       ), // TODO
    .intf_rx_o    (intf_rx_o         ), // RX
    .intf_tx_i    (intf_tx_i         )
  );


  // ------------------------------------------------------
  //  glbl.sync: u_sync
  // ------------------------------------------------------
  sync u_sync (
    .main_clk_i   (main_clk_i   ), // Clock
    .main_rst_an_i(main_rst_an_i), // Async Reset (Low-Active)
    .data_i       (1'b0         ), // TODO
    .data_o       (             )  // TODO
  );


  // ------------------------------------------------------
  //  top.sub: u_sub0
  // ------------------------------------------------------
  sub u_sub0 (
    .in_i     (4'h4            ), // info about in
    .open_i   (/* OPEN */      ), // info about open
    .open_o   (/* OPEN */      ), // info about open
    .note_i   (/* my note */   ), // info about note
    .note_o   (/* other note */), // info about note
    .default_i(4'h0            ), // DEFAULT - info about default
    .default_o(                ), // DEFAULT - info about default
    .unused_i (4'h0            ), // UNUSED
    .unused_o (                )  // UNUSED
  );


  // ------------------------------------------------------
  //  Flip-Flops
  // ------------------------------------------------------

  always_ff @(posedge main_clk_i or negedge main_rst_an_i) begin: proc_seq_0
    if (main_rst_an_i == 1'b0) begin
      data_r  <=  9'h000;
      data2_r <=  {param_p {1'b0}};
    end else begin
      data_r  <=  key_data_s;
      data2_r <=  data_i;
    end
  end

  // ------------------------------------------------------
  //  Assigns
  // ------------------------------------------------------
  `ifdef ASIC
  assign value_o      = key_data_s;
  `endif // ASIC
  assign key_valid_s  = key_valid_i;
  assign key_accept_o = key_accept_s;
  assign key_data_s   = key_data_i;

endmodule // top

`default_nettype wire
`end_keywords

// =============================================================================
//
//   @generated @fully-generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
