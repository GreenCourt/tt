#include<bits/stdc++.h>
using namespace std;

int main() {
  auto stoi_exact = [&](const string &s)  {
    size_t idx;
    int val = stoi(s, &idx);
    assert(idx == s.size());
    return val;
  };

  int mn = 1, mx = 1000000;
  mt19937_64 rnd_ = mt19937_64(random_device()());
  int n = uniform_int_distribution<int>(mn, mx)(rnd_);

  cerr << "n:" << n << endl;
  for(int i=0; i<25; ++i) {
    string s; cin >> s;
    assert(!cin.eof());
    if(s=="!") {
      cin >> s;
      assert(!cin.eof());
      int ans = stoi_exact(s);
      assert(ans == n);
      exit(0);
    }
    int q = stoi_exact(s);
    assert(mn <= q and q <= mx);
    if(n < q) cout << "<" << endl;
    else cout << ">=" << endl;
  }
}
