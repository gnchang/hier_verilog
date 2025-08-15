module shift_rows_tb;

reg [127:0] in;
wire [127:0] out;	
reg [127:0] expected_output;
shift_rows m (in, out);




 initial begin
    $monitor("input= %h , output= %h , expected= %h", in, out, expected_output);

	in = 128'hd42711aee0bf98f1b8b45de51e415230;
	expected_output = 128'hd4bf5d30e0b452aeb84111f11e2798e5;
    #10;
    if (out === expected_output)
        $display("✅ shift_rows PASS");
        else
        $display("❌ shift_rows FAIL");
	#10;

	in = 128'h49ded28945db96f17f39871a7702533b;
	expected_output = 128'h49db873b453953897f02d2f177de961a ;
    #10;
    if (out === expected_output)
        $display("✅ shift_rows PASS");
        else
        $display("❌ shift_rows FAIL");
	#10;

	in = 128'hac73cf7befc111df13b5d6b545235ab8;
	expected_output = 128'hacc1d6b8efb55a7b1323cfdf457311b5 ;
    #10;
    if (out === expected_output)
        $display("✅ shift_rows PASS");
        else
        $display("❌ shift_rows FAIL");
end
endmodule