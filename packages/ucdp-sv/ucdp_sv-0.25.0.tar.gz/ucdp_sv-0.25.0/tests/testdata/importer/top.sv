module top #(
  parameter integer               param_p   = 10,
  parameter generic_p   = 'h17,
  parameter generic2_p   = 10'd17,
  parameter               has_rx=1,
  parameter               has_tx=1
) (
  // main_i
  input  wire                main_clk_i,
  input  wire                main_rst_an_i, // Async Reset (Low-Active)
  // intf_i: RX/TX
  output logic               intf_rx_o,
  input  wire                intf_tx_i,
  // bus_i
  input  wire  [1:0]         bus_trans_i,
  input  wire  [31:0]        bus_addr_i,
  input  wire                bus_write_i,
  input  wire  [31:0]        bus_wdata_i,
  output logic               bus_ready_o,
  output logic               bus_resp_o,
  output logic [31:0]        bus_rdata_o,
  input  wire                bus_other_i,
  input  wire  [param_p-1:0] data_i,
  output logic [param_p-1:0] cnt_o,
  `ifdef ASIC
  output logic [8:0]         brick_o,
  `endif // ASIC
  // key_i
  input                      key_valid_i,
  output logic               key_accept,
  input  wire  [8:0]         key_data,
  inout  wire  [3:0]         bidir
  `ifdef ASIC
  ,
  output logic [8:0]         value_o
  `endif // ASIC
);


endmodule // top
