int foo(arg) {
 if(arg<2) return arg;
 else return foo(arg-2)+foo(arg-1);
}

foo(10);
halt;

