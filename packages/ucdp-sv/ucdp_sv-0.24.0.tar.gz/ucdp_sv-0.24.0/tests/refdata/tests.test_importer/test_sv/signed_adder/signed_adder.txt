Param(IntegerType(default=8), 'DATA_WIDTH')
Port(SintType(Param(IntegerType(default=8), 'DATA_WIDTH')), 'A', direction=IN)
Port(SintType(Param(IntegerType(default=8), 'DATA_WIDTH')), 'B', direction=IN)
Port(SintType(Op(Param(IntegerType(default=8), 'DATA_WIDTH'), '+', ConstExpr(IntegerType(default=1)))), 'X', direction=OUT)
