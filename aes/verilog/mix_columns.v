module mix_columns (input wire [127:0] state_in, output wire [127:0] state_out);

    // Function to perform multiplication in GF(2^8)
    function [7:0] xtime;
        input [7:0] byte;
        begin
            xtime = {byte[6:0], 1'b0} ^ (8'h1b & {8{byte[7]}});
        end
    endfunction

    // Function to perform multiplication by 3 in GF(2^8) which is equivalent to xtime(byte) ^ byte
    function [7:0] mul_by_3;
        input [7:0] byte;
        begin
            mul_by_3 = xtime(byte) ^ byte;
        end
    endfunction

    // Function to mix one column and returns the mixed column
    function [31:0] mix_single_column;
        input [31:0] column;
        reg [7:0] b0, b1, b2, b3;
        reg [7:0] mb0, mb1, mb2, mb3;
        begin
            b0 = column[31:24];
            b1 = column[23:16];
            b2 = column[15:8];
            b3 = column[7:0];
            
            mb0 = xtime(b0) ^ mul_by_3(b1) ^ b2 ^ b3;
            mb1 = b0 ^ xtime(b1) ^ mul_by_3(b2) ^ b3;
            mb2 = b0 ^ b1 ^ xtime(b2) ^ mul_by_3(b3);
            mb3 = mul_by_3(b0) ^ b1 ^ b2 ^ xtime(b3);
            
            mix_single_column = {mb0, mb1, mb2, mb3};
        end
    endfunction

    assign state_out[127:96] = mix_single_column(state_in[127:96]);
    assign state_out[95:64]  = mix_single_column(state_in[95:64]);
    assign state_out[63:32]  = mix_single_column(state_in[63:32]);
    assign state_out[31:0]   = mix_single_column(state_in[31:0]);

endmodule