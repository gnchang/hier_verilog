module AESEncrypt_tb;

	wire [127:0] data = 128'h00112233445566778899aabbccddeeff;
	//wire [4 * 32 - 1:0] key = 128'h000102030405060708090a0b0c0d0e0f;
	wire [((10 + 1) * 128) - 1:0] allKeys = 1408'h000102030405060708090a0b0c0d0e0fd6aa74fdd2af72fadaa678f1d6ab76feb692cf0b643dbdf1be9bc5006830b3feb6ff744ed2c2c9bf6c590cbf0469bf4147f7f7bc95353e03f96c32bcfd058dfd3caaa3e8a99f9deb50f3af57adf622aa5e390f7df7a69296a7553dc10aa31f6b14f9701ae35fe28c440adf4d4ea9c02647438735a41c65b9e016baf4aebf7ad2549932d1f08557681093ed9cbe2c974e13111d7fe3944a17f307a78b4d2b30c5;
	wire [127:0] out;

	reg clk = 1'b0;
    reg reset = 1'b0;
    reg enable = 1'b0;

    wire [127:0] expected_output = 128'h69c4e0d86a7b0430d8cdb78070b4c55a;

	//key_expansion ke(key, allKeys);
	encryption_block aes(data, allKeys, clk, enable, reset, out); // enable, reset
	
	initial begin
		clk = 1'b1;
		forever #10 clk = ~clk;
	end

	initial begin

		#15 reset = 1;
        #20 reset = 0;
		#20 enable = 1;

		#300;

		if (out == expected_output) begin
			$display("✅ TEST PASSED: Encryption output matches expected value.");
		end else begin
			$display("❌ TEST FAILED: Encryption output does NOT match expected value.");
			$display("Expected: %h", expected_output);
			$display("Got:      %h", out);
		end
		$finish;
	end

endmodule