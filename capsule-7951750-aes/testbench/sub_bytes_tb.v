module subBytes_tb;
reg [127:0] in;
wire [127:0]out;
reg [127:0] expected_output;

sub_bytes sb(in,out);

initial begin
    $monitor("input= %h , output= %h , expected= %h", in, out, expected_output);

    in=128'h193de3bea0f4e22b9ac68d2ae9f84808;
    expected_output= 128'hd42711aee0bf98f1b8b45de51e415230;
    #10;
        if (out === expected_output)
            $display("✅ sub_bytes PASS");
            else
            $display("❌ sub_bytes FAIL");


    #10;
    in=128'ha49c7ff2689f352b6b5bea43026a5049;
    expected_output= 128'h49ded28945db96f17f39871a7702533b;
    #10;
        if (out === expected_output)
            $display("✅ sub_bytes PASS");
            else
            $display("❌ sub_bytes FAIL");



    #10;
    in=128'haa8f5f0361dde3ef82d24ad26832469a;
    expected_output= 128'hac73cf7befc111df13b5d6b545235ab8;
    #10;
        if (out === expected_output)
            $display("✅ sub_bytes PASS");
            else
            $display("❌ sub_bytes FAIL");
    #10;
    $finish;
end
endmodule