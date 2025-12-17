module matrix #(
  parameter addrwidth, datawidth_p = 32,
  parameter tranwidth_p = 2

) (
  input  wire                main_clk_i,
  input  wire                main_rst_an_i, // Async Reset (Low-Active)
`ifdef TRAN
  output logic               intf_rx_o,
  input  wire                intf_tx_i,
`endif
  input  wire  [tranwidth_p-1:0] bus_a_trans_i,
  input  wire  [addrwidth-1:0] bus_a_addr_i,
  input  wire                bus_a_write_i,
  input  wire  [datawidth_p-1:0] bus_a_wdata_i,
  output logic               bus_a_ready_o,
  output logic               bus_a_resp_o,
  output logic [datawidth_p-1:0] bus_a_rdata_o,

  input  wire  [tranwidth_p-1:0] bus_b_trans_i,
  input  wire  [addrwidth-1:0] bus_b_addr_i,
  input  wire                bus_b_write_i,
  input  wire  [datawidth_p-1:0] bus_b_wdata_i,
  output logic               bus_b_ready_o,
  output logic               bus_b_resp_o,
  output logic [datawidth_p-1:0] bus_b_rdata_o,

  output wire  [tranwidth_p-1:0] bus_c_trans_o,
  output wire  [addrwidth-1:0] bus_c_addr_o,
  output wire                bus_c_write_o,
  output wire  [datawidth_p-1:0] bus_c_wdata_o,
  input  logic               bus_c_ready_i,
  input  logic               bus_c_resp_i,
  input  logic [datawidth_p-1:0] bus_c_rdata_i,

  input  wire  [tranwidth_p-1:0] bus_m0_trans,
  input  wire  [addrwidth-1:0] bus_m0_addr,
  input  wire                bus_m0_write,
  input  wire  [datawidth_p-1:0] bus_m0_wdata,
  output logic               bus_m0_ready,
  output logic               bus_m0_resp,
  output logic [datawidth_p-1:0] bus_m0_rdata,

  output wire  [tranwidth_p-1:0] bus_s0_trans,
  output wire  [addrwidth-1:0] bus_s0_addr,
  output reg                 bus_s0_write,
  output wire  [datawidth_p-1:0] bus_s0_wdata,
  input  logic               bus_s0_ready,
  input  logic               bus_s0_resp,
  input  logic [datawidth_p-1:0] bus_s0_rdata
);


endmodule // matrix
