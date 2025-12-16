a=foo(5);
halt;
int foo(int arg) {
 if(arg < 1) return(arg);
 return arg + foo(arg-1);
}

