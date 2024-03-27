#include<bits/stdc++.h>
using namespace std;

int main() {
  mt19937_64 rnd_ = mt19937_64(random_device()());
  int a = uniform_int_distribution<int>(2800, 4999)(rnd_);
  cout << a << '\n';
  int n = uniform_int_distribution<int>(1, 10)(rnd_);
  for(int i=0; i<n; ++i) cout << uniform_int_distribution<char>('a', 'z')(rnd_);
  cout << '\n';
}
