module inverse_mix_columns_tb;
reg [0:127] in;
reg [0:127] expected_output;
wire [0:127] out;	


inv_mix_columns m (in,out);


 initial begin
    $monitor("input= %h , output= %h , expected= %h", in, out, expected_output);
    in= 128'hbaa03de7a1f9b56ed5512cba5f414d23;
    expected_output = 128'h3e1c22c0b6fcbf768da85067f6170495 ;
    #10;
    if (out === expected_output)
        $display("✅ inv_mix_columns PASS");
        else
        $display("❌ inv_mix_columns FAIL");
    #10;
    //in=128'h_84e1dd69_1a41d76f_792d3897_83fbac70 ;
    //#10;
    //in=128'h_6353e08c_0960e104_cd70b751_bacad0e7;
    //#10;
end
endmodule