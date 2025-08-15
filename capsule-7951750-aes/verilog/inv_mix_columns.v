module inv_mix_columns (input wire [127:0] state, output wire [127:0] new_state);

  function [31:0] inv_mix_single_column;
    input [31:0] column;
    reg [7:0] s0, s1, s2, s3;
    reg [7:0] result0, result1, result2, result3;
    begin
      s0 = column[31:24];
      s1 = column[23:16];
      s2 = column[15:8];
      s3 = column[7:0];
      
      result0 = gf_mul(8'h0E, s0) ^ gf_mul(8'h0B, s1) ^ gf_mul(8'h0D, s2) ^ gf_mul(8'h09, s3);
      result1 = gf_mul(8'h09, s0) ^ gf_mul(8'h0E, s1) ^ gf_mul(8'h0B, s2) ^ gf_mul(8'h0D, s3);
      result2 = gf_mul(8'h0D, s0) ^ gf_mul(8'h09, s1) ^ gf_mul(8'h0E, s2) ^ gf_mul(8'h0B, s3);
      result3 = gf_mul(8'h0B, s0) ^ gf_mul(8'h0D, s1) ^ gf_mul(8'h09, s2) ^ gf_mul(8'h0E, s3);
      
      inv_mix_single_column = {result0, result1, result2, result3};
    end
  endfunction

  function [7:0] gf_mul;
    input [7:0] a, b;
    reg [7:0] result;
    reg [7:0] temp_a;
    reg [3:0] i;
    begin
      result = 8'b0;
      temp_a = a;
      for (i = 0; i < 8; i = i + 1) begin
        if (b[i]) begin
          result = result ^ temp_a;
        end
        if (temp_a[7]) begin
          temp_a = (temp_a << 1) ^ 8'h1B;
        end else begin
          temp_a = temp_a << 1;
        end
      end
      gf_mul = result;
    end
  endfunction

  assign new_state[127:96] = inv_mix_single_column(state[127:96]);
  assign new_state[95:64] = inv_mix_single_column(state[95:64]);
  assign new_state[63:32] = inv_mix_single_column(state[63:32]);
  assign new_state[31:0] = inv_mix_single_column(state[31:0]);

endmodule