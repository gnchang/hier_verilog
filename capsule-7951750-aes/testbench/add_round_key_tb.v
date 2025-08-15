module add_round_key_tb;

reg [127:0] in;
reg [127:0] key;
wire [127:0] out;	
reg [127:0] expected_output;

add_round_key m (in, key, out);


initial begin
	$monitor("input= %H, output= %h, key = %h", in, out, key);
	in = 128'h046681e5e0cb199a48f8d37a2806264c;
	key = 128'ha0fafe1788542cb123a339392a6c7605;
    expected_output = 128'ha49c7ff2689f352b6b5bea43026a5049;

    #10;
    if (out === expected_output)
        $display("✅ add_round_key PASS");
        else
        $display("❌ add_round_key FAIL");
end
endmodule