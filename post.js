javascript:(
  function(){
    try {
      var f = function(q) {
        var r = [];
        var x = document.evaluate(q, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (var i = 0; i < x.snapshotLength; i++) r.push(x.snapshotItem(i).innerText);
        return r;
      };
      var I = [], O = [];
      switch (document.domain) {
        case 'atcoder.jp':
          I = f("//div/section/h3[starts-with(text(),'Sample Input')]/following-sibling::pre[1]");
          O = f("//div/section/h3[starts-with(text(),'Sample Output')]/following-sibling::pre[1]");
          break;
        case 'codeforces.com':
          I = f("//div/div[text()='Input']/following-sibling::pre[1]");
          O = f("//div/div[text()='Output']/following-sibling::pre[1]");
          break;
        default:
          throw "unsupported domain";
      }
      if((I.length == 0) || (I.length != O.length)) throw "failed to parse.";
      var token = "";
      fetch('http://127.0.0.1:17624/?'+token,{method:'POST',mode:"no-cors",body:JSON.stringify({"url":location.href,"I":I,"O":O})});
      console.log(I.map((x,i) => "____ in" + String(i+1) + " ____\n" + x + "\n____ out" + String(i+1) + " ____\n" + O[i]).join("\n"));
    }
    catch (e) {
      alert(e);
    }
  }
)();
