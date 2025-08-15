module encryption_block (
    input wire [127:0] data_in, 
    input wire [1407:0] round_keys, 
    input clk, 
    input enable, 
    input reset, 
    output reg [127:0] data_out
);
    reg [3:0] round_count;
    reg [127:0] state_reg;
    wire [127:0] round_key;
    wire [127:0] sub_bytes_wire;
    wire [127:0] shift_rows_wire;
    wire [127:0] mix_columns_wire;
    wire [127:0] add_round_key_wire;

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            round_count <= 4'd0;
            data_out <= 128'd0;
            state_reg <= 128'd0;
        end else if (enable) begin
            if (round_count == 4'd11) begin
                round_count <= 4'd0;
            end else begin
                round_count <= round_count + 4'd1;
                state_reg <= add_round_key_wire;
                if (round_count == 4'd10) begin
                    data_out <= add_round_key_wire;
                end
            end
        end
    end

    assign round_key = round_keys[1407 - (round_count) * 128 -: 128];

    sub_bytes u_sub_bytes (
        .state_in(state_reg),
        .state_out(sub_bytes_wire)
    );

    shift_rows u_shift_rows (
        .state_in(sub_bytes_wire),
        .state_out(shift_rows_wire)
    );

    mix_columns u_mix_columns (
        .state_in(shift_rows_wire),
        .state_out(mix_columns_wire)
    );

    assign add_round_key_wire = (round_count == 4'd0) ? (data_in ^ round_key) :
                                (round_count < 4'd10) ? (mix_columns_wire ^ round_key) :
                                (shift_rows_wire ^ round_key);

endmodule