"""Builds docs/artifact/index.html: the same page as index.html, prepared for
publishing as a claude.ai Artifact (no document skeleton, and PDF downloads
routed through the viewer's `downloads` capability, since plain <a download>
links are inert inside the artifact sandbox). Run after build_site.py.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = open(ROOT / "index.html").read()
out = ROOT / "docs" / "artifact"
out.mkdir(exist_ok=True)

# strip the skeleton: keep everything that was inside <head> (minus charset/viewport) and <body>
head = re.search(r"<head>(.*?)</head>", src, re.S).group(1)
body = re.search(r"<body>(.*?)</body>", src, re.S).group(1)
head = re.sub(r'<meta charset="utf-8">\s*', "", head)
head = re.sub(r'<meta name="viewport"[^>]*>\s*', "", head)
head = head.replace('<link rel="icon" type="image/png" href="images/logo-mark.png">\n', "")

DL = """
<script>
(function(){
  // Inside the claude.ai artifact viewer, downloads go through the viewer's save prompt.
  var p = (window.claude && window.claude.use) ? window.claude.use('downloads') : Promise.resolve(null);
  p.then(function(dl){
    if(!dl) return;
    document.querySelectorAll('a[download]').forEach(function(a){
      a.addEventListener('click', function(e){
        e.preventDefault();
        var name = a.getAttribute('download') || a.getAttribute('href').split('/').pop();
        var label = a.querySelector('.act');
        if(label) label.textContent = 'Preparing…';
        fetch(a.getAttribute('href')).then(function(r){ if(!r.ok) throw new Error('fetch'); return r.blob(); })
          .then(function(b){ return dl.save({filename: name, data: b}); })
          .then(function(){ if(label) label.textContent = 'Saved ✓'; })
          .catch(function(err){ if(label) label.textContent = (err && err.code === 'declined') ? 'Download ↓' : 'Unavailable here'; })
          .finally(function(){ setTimeout(function(){ if(label) label.textContent = 'Download ↓'; }, 2500); });
      });
    });
  });
})();
</script>
"""
page = head.strip() + "\n" + body.strip() + "\n" + DL
open(out / "index.html", "w").write(page)
print("wrote", out / "index.html", len(page), "bytes")
