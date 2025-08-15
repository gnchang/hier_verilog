module inverseShiftRows_tb;

reg [127:0] in;
reg [127:0] expected_output;  // 기대 출력값
wire [127:0] out;	


inv_shift_rows m (in,out);


initial begin
	$monitor("input= %H , output= %h",in,out);
	in = 128'h7ad5fda789ef4e272bca100b3d9ff59f;
    expected_output = 128'h7a9f102789d5f50b2beffd9f3dca4ea7;
    #10;
    if (out === expected_output)
        $display("✅ inv_shift_rows PASS");
        else
        $display("❌ inv_shift_rows FAIL");
end
endmodule