.assembly extern mscorlib {}
.assembly output {}
.module output.exe
.class private auto ansi beforefieldinit ConsoleApp1.Program extends [mscorlib]System.Object
{
.method private hidebysig static void  Main(string[] args) cil managed
{
.entrypoint
.maxstack  100
.locals init ([0] int64 T0)
.locals init ([1] int64 T1)
.locals init ([2] int64 T2)
.locals init ([3] int64 c)
.locals init ([4] int64 forst)
.locals init ([5] int64 ouput)
.locals init ([6] int64 output)
nop
///////////////////////// IL CODE
ldc.i8 1
stloc i
ldc.i8 4
stloc T0
Label1:
ldloc c
ldc.i8 1
add
stloc T1
ldloc T1
stloc c
ldloc i
ldc.i8 1
ADD
stloc i
ldloc T0
ldloc i
ceq
stloc T1
brtrue Label2
br Label1
Label2:
ldc.i8 2
stloc ouput

///////////////////////// IL CODE
ldloca.s   output
call       instance string [mscorlib]System.Int64::ToString()
call       void [mscorlib]System.Console::WriteLine(string)
nop
ret
} // end of method Program::Main
.method public hidebysig specialname rtspecialname instance void  .ctor() cil managed
{
.maxstack  8
ldarg.0
call       instance void [mscorlib]System.Object::.ctor()
nop
ret
} // end of method Program::.ctor
} // end of class
