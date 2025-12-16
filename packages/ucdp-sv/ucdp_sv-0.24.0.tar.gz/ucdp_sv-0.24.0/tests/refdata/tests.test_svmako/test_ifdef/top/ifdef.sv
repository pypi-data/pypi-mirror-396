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
// Update via:  ucdp gen top.ifdef
//
// Library:     top
// Module:      ifdef
// Data Model:  IfdefMod
//              top/ifdef.py
// Submodules:
//              sub0 u_sub0
//              sub1 u_sub1
//              sub2 u_sub2
//              sub3 u_sub3
//
// =============================================================================

`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden

module ifdef (
  input wire [7:0] a_i,
  `ifdef A
  input wire [7:0] b_i,
  `endif // A
  input wire [7:0] j_i
);



  // ------------------------------------------------------
  //  top.sub0: u_sub0
  // ------------------------------------------------------
  sub0 u_sub0 (
    .a_i(a_i  ),
    `ifdef A
    .b_i(b_i  ),
    `endif // A
    `ifdef B
    .c_i(8'h00), // TODO
    `endif // B
    `ifndef B
    .d_i(8'h00), // TODO
    `endif // !B
    `ifdef C
    .e_i(8'h00), // TODO
      `ifdef D
    .f_i(8'h00), // TODO
      `endif // D
    `endif // C
    `ifdef D
    .g_i(8'h00), // TODO
      `ifdef E
    .h_i(8'h00), // TODO
      `endif // E
    .i_i(8'h00), // TODO
    `endif // D
    .j_i(8'h00)  // TODO
  );


  // ------------------------------------------------------
  //  top.sub1: u_sub1
  // ------------------------------------------------------
  sub1 u_sub1 (
    `ifdef B
    .k_i(8'h00) // TODO
    `endif // B
    `ifdef D
      `ifdef E
    ,
    .l_i(8'h00) // TODO
      `endif // E
    `endif // D
    `ifdef E
    ,
    .m_i(8'h00) // TODO
    `endif // E
  );


  // ------------------------------------------------------
  //  top.sub2: u_sub2
  // ------------------------------------------------------
  sub2 u_sub2 (
    .q_i   (8'h00), // TODO
    `ifdef B
      `ifdef X
    .r_rx_o(     ), // TODO
        `ifdef Y
    .r_tx_i(1'b0 ), // TODO
        `endif // Y
      `endif // X
    `endif // B
    `ifdef D
      `ifdef E
    .s_i   (8'h00), // TODO
      `endif // E
    `endif // D
    .t_i   (8'h00)  // TODO
  );


  // ------------------------------------------------------
  //  top.sub3: u_sub3
  // ------------------------------------------------------
  sub3 u_sub3 (
    .q_i(`MYDEFAULT), // TODO
    .t_i(8'h00     )  // TODO
  );

endmodule // ifdef

`default_nettype wire
`end_keywords

// =============================================================================
//
//   @generated @fully-generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
