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
// Update via:  ucdp gen glbl.sync
//
// Library:     glbl
// Module:      sync
// Data Model:  SyncMod
//              glbl/sync.py
//
// =============================================================================

`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden

module sync (
  // main_i: Clock and Reset
  input  wire  main_clk_i,    // Clock
  input  wire  main_rst_an_i, // Async Reset (Low-Active)
  // -
  input  wire  data_i,
  output logic data_o
);



  // ------------------------------------------------------
  //  Local Parameter
  // ------------------------------------------------------
  // edge
  localparam integer       edge_width_p   = 2;    // Width in Bits
  localparam logic   [1:0] edge_min_p     = 2'h0; // Minimal Value
  localparam logic   [1:0] edge_max_p     = 2'h3; // Maximal Value
  localparam logic   [1:0] edge_no_e      = 2'h0;
  localparam logic   [1:0] edge_pos_e     = 2'h1;
  localparam logic   [1:0] edge_neg_e     = 2'h2;
  localparam logic   [1:0] edge_default_p = 2'h0; // Default Value

// GENERATE INPLACE END head ===================================================



// GENERATE INPLACE BEGIN tail() ===============================================
endmodule // sync

`default_nettype wire
`end_keywords
// GENERATE INPLACE END tail ===================================================
