module add_round_key (
    input wire [127:0] state,
    input wire [127:0] round_key,
    output wire [127:0] state_out
);

assign state_out = state ^ round_key;

endmodule