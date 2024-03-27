#include<bits/stdc++.h>
using namespace std;

int main() {
  mt19937_64 rnd_ = mt19937_64(random_device()());
  cout << uniform_int_distribution<int>(1, 100)(rnd_) << '\n';
}
