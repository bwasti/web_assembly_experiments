int b_fn(int x);

int a_fn(int x) {
  x = b_fn(x);
  return x + 13;
}
