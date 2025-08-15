module sub_bytes (input wire [127:0] state_in, output wire [127:0] state_out);

  // Instantiate the s_box module for each byte of the input state
  s_box s_box0 (.in_byte(state_in[127:120]), .c(state_out[127:120]));
  s_box s_box1 (.in_byte(state_in[119:112]), .c(state_out[119:112]));
  s_box s_box2 (.in_byte(state_in[111:104]), .c(state_out[111:104]));
  s_box s_box3 (.in_byte(state_in[103:96]), .c(state_out[103:96]));
  s_box s_box4 (.in_byte(state_in[95:88]), .c(state_out[95:88]));
  s_box s_box5 (.in_byte(state_in[87:80]), .c(state_out[87:80]));
  s_box s_box6 (.in_byte(state_in[79:72]), .c(state_out[79:72]));
  s_box s_box7 (.in_byte(state_in[71:64]), .c(state_out[71:64]));
  s_box s_box8 (.in_byte(state_in[63:56]), .c(state_out[63:56]));
  s_box s_box9 (.in_byte(state_in[55:48]), .c(state_out[55:48]));
  s_box s_box10 (.in_byte(state_in[47:40]), .c(state_out[47:40]));
  s_box s_box11 (.in_byte(state_in[39:32]), .c(state_out[39:32]));
  s_box s_box12 (.in_byte(state_in[31:24]), .c(state_out[31:24]));
  s_box s_box13 (.in_byte(state_in[23:16]), .c(state_out[23:16]));
  s_box s_box14 (.in_byte(state_in[15:8]), .c(state_out[15:8]));
  s_box s_box15 (.in_byte(state_in[7:0]), .c(state_out[7:0]));

endmodule