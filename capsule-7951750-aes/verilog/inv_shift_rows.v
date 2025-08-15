module inv_shift_rows (input wire [127:0] state, output wire [127:0] new_state);

    // Decompose the state into bytes for each row
    wire [7:0] row_0_0 = state[127:120];
    wire [7:0] row_0_1 = state[95:88];
    wire [7:0] row_0_2 = state[63:56];
    wire [7:0] row_0_3 = state[31:24];
    
    wire [7:0] row_1_0 = state[119:112];
    wire [7:0] row_1_1 = state[87:80];
    wire [7:0] row_1_2 = state[55:48];
    wire [7:0] row_1_3 = state[23:16];
    
    wire [7:0] row_2_0 = state[111:104];
    wire [7:0] row_2_1 = state[79:72];
    wire [7:0] row_2_2 = state[47:40];
    wire [7:0] row_2_3 = state[15:8];
    
    wire [7:0] row_3_0 = state[103:96];
    wire [7:0] row_3_1 = state[71:64];
    wire [7:0] row_3_2 = state[39:32];
    wire [7:0] row_3_3 = state[7:0];

    // Inverse shift the rows
    // Row 0: no shift
    assign new_state[127:120] = row_0_0;
    assign new_state[95:88]   = row_0_1;
    assign new_state[63:56]   = row_0_2;
    assign new_state[31:24]   = row_0_3;

    // Row 1: shift right by 1
    assign new_state[119:112] = row_1_3;
    assign new_state[87:80]   = row_1_0;
    assign new_state[55:48]   = row_1_1;
    assign new_state[23:16]   = row_1_2;

    // Row 2: shift right by 2
    assign new_state[111:104] = row_2_2;
    assign new_state[79:72]   = row_2_3;
    assign new_state[47:40]   = row_2_0;
    assign new_state[15:8]    = row_2_1;

    // Row 3: shift right by 3
    assign new_state[103:96]  = row_3_1;
    assign new_state[71:64]   = row_3_2;
    assign new_state[39:32]   = row_3_3;
    assign new_state[7:0]     = row_3_0;

endmodule