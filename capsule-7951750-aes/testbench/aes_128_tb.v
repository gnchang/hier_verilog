module AES_tb;
    reg clk = 1'b0;
    reg reset = 1'b0;
    reg enable = 1'b1;
    reg mode = 1'b0; // 0: 암호화, 1: 복호화
    reg [127:0] key = 128'h000102030405060708090a0b0c0d0e0f;
    reg [127:0] data = 128'h00112233445566778899aabbccddeeff;
    wire [127:0] data_out;
    wire done;

    wire [127:0] expected_output1 = 128'h69c4e0d86a7b0430d8cdb78070b4c55a;
    wire [127:0] expected_output2 = 128'h00112233445566778899aabbccddeeff;

    aes_128 aes128 (
        .clk(clk),
        .reset(reset),
        .enable(enable),
        .mode(mode),
        .key(key),
        .data_in(data),
        .data_out(data_out),
        .done(done)
    );

    integer count = 0;
    initial begin
        forever #10 clk = ~clk;
    end

    initial begin
        $display("AES 128-bit Encryption and Decryption Test");
        $display("================================");
        $display("Starting 128-bit AES Encryption");
        reset = 1;
        #20 reset = 0;

        // Encryption Phase
        mode = 0; // 암호화 모드
        enable = 1;
        #400;
        $display("Encryption Complete. Cipher Text: %h", data_out);
        if (data_out == expected_output1) begin
			$display("✅ TEST PASS: Encryption output matches expected value.");
		end else begin
			$display("❌ TEST FAIL: Encryption output does NOT match expected value.");
			$display("Expected: %h", expected_output1);
			$display("Got:      %h", data_out);
		end


         // Decryption Phase
        $display("\n================================");
        $display("Starting 128-bit AES Decryption");
        reset = 1;
        #20; 
        reset = 0;
        data = 128'h69c4e0d86a7b0430d8cdb78070b4c55a;
        key = 128'h000102030405060708090a0b0c0d0e0f;
        #20;
        enable = 1;
        mode = 1; // 복호화 모드
        #400;
        $display("Decryption Complete. Recovered Plain Text: %h", data_out);
        #400;
        if (data_out == expected_output2) begin
			$display("✅ TEST PASS: Decryption output matches expected value.");
		end else begin
			$display("❌ TEST FAIL: Decryption output does NOT match expected value.");
			$display("Expected: %h", expected_output2);
			$display("Got:      %h", data_out);
		end
        $finish;
    end
endmodule