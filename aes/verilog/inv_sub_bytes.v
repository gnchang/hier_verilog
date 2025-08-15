module inv_sub_bytes (input wire [127:0] state, output wire [127:0] new_state);

    // Instantiate the inv_s_box submodules for each byte (16 bytes in total)
    inv_s_box inv_s_box_0 (.in_byte(state[127:120]), .out_byte(new_state[127:120]));
    inv_s_box inv_s_box_1 (.in_byte(state[119:112]), .out_byte(new_state[119:112]));
    inv_s_box inv_s_box_2 (.in_byte(state[111:104]), .out_byte(new_state[111:104]));
    inv_s_box inv_s_box_3 (.in_byte(state[103:96]), .out_byte(new_state[103:96]));
    
    inv_s_box inv_s_box_4 (.in_byte(state[95:88]), .out_byte(new_state[95:88]));
    inv_s_box inv_s_box_5 (.in_byte(state[87:80]), .out_byte(new_state[87:80]));
    inv_s_box inv_s_box_6 (.in_byte(state[79:72]), .out_byte(new_state[79:72]));
    inv_s_box inv_s_box_7 (.in_byte(state[71:64]), .out_byte(new_state[71:64]));
    
    inv_s_box inv_s_box_8 (.in_byte(state[63:56]), .out_byte(new_state[63:56]));
    inv_s_box inv_s_box_9 (.in_byte(state[55:48]), .out_byte(new_state[55:48]));
    inv_s_box inv_s_box_10 (.in_byte(state[47:40]), .out_byte(new_state[47:40]));
    inv_s_box inv_s_box_11 (.in_byte(state[39:32]), .out_byte(new_state[39:32]));
    
    inv_s_box inv_s_box_12 (.in_byte(state[31:24]), .out_byte(new_state[31:24]));
    inv_s_box inv_s_box_13 (.in_byte(state[23:16]), .out_byte(new_state[23:16]));
    inv_s_box inv_s_box_14 (.in_byte(state[15:8]), .out_byte(new_state[15:8]));
    inv_s_box inv_s_box_15 (.in_byte(state[7:0]), .out_byte(new_state[7:0]));

endmodule