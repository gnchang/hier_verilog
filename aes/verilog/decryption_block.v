module decryption_block (
    input wire [127:0] data_in,
    input wire [1407:0] round_keys,
    input clk,
    input enable,
    input reset,
    output reg [127:0] data_out
);

    reg [3:0] round_count;
    wire [127:0] inv_shift_rows_wires;
    wire [127:0] inv_sub_bytes_wires;
    wire [127:0] add_round_key_wires;
    wire [127:0] inv_mix_columns_wires;
    reg [127:0] current_state;

    // Submodule instantiations
    inv_shift_rows u_inv_shift_rows (
        .state(current_state),
        .new_state(inv_shift_rows_wires)
    );

    inv_sub_bytes u_inv_sub_bytes (
        .state(inv_shift_rows_wires),
        .new_state(inv_sub_bytes_wires)
    );

    add_round_key u_add_round_key (
        .state((round_count == 0) ? data_in : inv_sub_bytes_wires),
        .round_key(round_keys[round_count * 128 +: 128]),
        .state_out(add_round_key_wires)
    );

    inv_mix_columns u_inv_mix_columns (
        .state(add_round_key_wires),
        .new_state(inv_mix_columns_wires)
    );

    // Main decryption control logic
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            round_count <= 4'd0;
            data_out <= 128'd0;
            current_state <= 128'd0;
        end else if (enable) begin
            if (round_count == 4'd0) begin
                // Initial round
                current_state <= add_round_key_wires;
            end else if (round_count == 4'd10) begin
                // Final round
                data_out <= add_round_key_wires;
            end else if (round_count < 4'd10) begin
                // Intermediate rounds
                current_state <= inv_mix_columns_wires;
            end

            // Increment round counter for next operation
            round_count <= round_count + 4'd1;
        end
    end

endmodule