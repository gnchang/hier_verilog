module aes_128 (
    input wire clk,
    input wire reset,
    input wire enable,
    input wire mode,
    input wire [127:0] key,
    input wire [127:0] data_in,
    output reg [127:0] data_out,
    output reg done
);
    reg [3:0] round_count;
    wire [1407:0] expanded_keys;
    wire [127:0] encryption_data_out;
    wire [127:0] decryption_data_out;

    // Submodule instantiation for key expansion
    key_expansion key_exp(
        .key(key),
        .expanded_keys(expanded_keys)
    );

    // Submodule instantiation for encryption block
    encryption_block encrypt_blk(
        .data_in(data_in),
        .round_keys(expanded_keys),
        .clk(clk),
        .enable(enable & ~mode), // Enable only when mode is 0 (encryption)
        .reset(reset),
        .data_out(encryption_data_out)
    );

    // Submodule instantiation for decryption block
    decryption_block decrypt_blk(
        .data_in(data_in),
        .round_keys(expanded_keys),
        .clk(clk),
        .enable(enable & mode), // Enable only when mode is 1 (decryption)
        .reset(reset),
        .data_out(decryption_data_out)
    );

    // Control logic for processing rounds
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            round_count <= 0;
            data_out <= 128'b0;
            done <= 0;
        end else if (enable) begin
            if (round_count < 10) begin
                round_count <= round_count + 1;
            end else begin
                done <= 1'b1;
                round_count <= 0;
            end
        end
    end

    // Data output logic
    always @(posedge clk) begin
        if (done) begin
            if (mode == 1'b0) begin
                data_out <= encryption_data_out; // Encryption mode
            end else begin
                data_out <= decryption_data_out; // Decryption mode
            end
        end
    end

endmodule