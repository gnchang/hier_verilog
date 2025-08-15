module mix_columns_tb;
reg [0:127] in;
reg [127:0] expected_output;  // 기대 출력값
wire [0:127] out;	
mix_columns m (in, out);



 initial begin
    $monitor("input= %h , output= %h , expected= %h", in, out, expected_output);

    in= 128'hd4bf5d30e0b452ae_b84111f11e2798e5 ;
    expected_output = 128'h046681e5e0cb199a48f8d37a2806264c ;
    #10;
    if (out === expected_output)
        $display("✅ mix_columns PASS");
        else
        $display("❌ mix_columns FAIL");

    in=128'h84e1dd691a41d76f_792d389783fbac70 ;
    expected_output = 128'h9f487f794f955f662afc86abd7f1ab29;
    #10;
    if (out === expected_output)
      $display("✅ mix_columns PASS");
    else
      $display("❌ mix_columns FAIL");

    in=128'h6353e08c0960e104cd70b751bacad0e7;
    expected_output=128'h5f72641557f5bc92f7be3b291db9f91a;
    #10;
    if (out === expected_output)
      $display("✅ mix_columns PASS");
    else
      $display("❌ mix_columns FAIL");

end
endmodule