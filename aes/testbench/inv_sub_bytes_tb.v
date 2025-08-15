module inverse_sub_bytes_tb;
reg [127:0] in;
reg [127:0] expected_output;  // 기대 출력값
wire [127:0]out;

inv_sub_bytes isb(in,out);

initial begin
    $monitor("input= %h , output= %h , expected= %h", in, out, expected_output);
    in=128'h7a9f102789d5f50b2beffd9f3dca4ea7;
    expected_output = 128'hbd6e7c3df2b5779e0b61216e8b10b689;
    #10;
    if (out === expected_output)
        $display("✅ inverse_sub_bytes PASS");
        else
        $display("❌ inverse_sub_bytes FAIL");

$finish;
end

endmodule