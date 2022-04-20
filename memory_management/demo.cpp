#include "malloc.h"
#include <stdint.h>
#define EXPORT __attribute__((visibility("default")))

class MyClass {
private:
  int hidden;

public:
  MyClass(int hide) : hidden(hide) {}
  ~MyClass() {}
  int my_method() { return hidden * 2; }
};

EXPORT void *operator new(unsigned long count) { return malloc(count); }
EXPORT void operator delete(void *v) { return free(v); }

extern "C" {

EXPORT MyClass *_MyClass__constructor(int h) { return new MyClass(h); }
EXPORT void _MyClass__destructor(MyClass *m) { delete m; }
EXPORT int _MyClass__my_method(MyClass *m) { return m->my_method(); }

}
