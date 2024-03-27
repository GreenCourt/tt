#include<bits/stdc++.h>
using namespace std;

int main() {
  int l = 1, r = 1000000 + 1;
  while(r-l > 1) {
    int m = l + (r-l)/2;
    cout << m << endl;
    string res; cin >> res;
    assert(!cin.eof());
    assert(res == "<" or res == ">=");
    if(res == "<") r = m;
    else l = m;
  }
  cout << "! " << l << endl;
}
