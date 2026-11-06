// static server with Range support (video needs it); python's http.server hangs the new engines
const http=require('http'),fs=require('fs'),path=require('path');
const root=process.argv[2],port=+process.argv[3]||4173;
const T={'.html':'text/html','.css':'text/css','.js':'text/javascript','.webp':'image/webp','.jpg':'image/jpeg','.mp4':'video/mp4','.svg':'image/svg+xml','.woff2':'font/woff2','.txt':'text/plain'};
http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);if(p.endsWith('/'))p+='index.html';const f=path.join(root,p);
 fs.stat(f,(e,s)=>{if(e||!s.isFile()){r.writeHead(404);return r.end('nf')}
  const h={'Content-Type':T[path.extname(f)]||'application/octet-stream','Accept-Ranges':'bytes'};
  const m=/bytes=(\d+)-(\d*)/.exec(q.headers.range||'');
  if(m){const a=+m[1],b=m[2]?+m[2]:s.size-1;r.writeHead(206,{...h,'Content-Range':`bytes ${a}-${b}/${s.size}`,'Content-Length':b-a+1});fs.createReadStream(f,{start:a,end:b}).pipe(r)}
  else{r.writeHead(200,{...h,'Content-Length':s.size});fs.createReadStream(f).pipe(r)}})
}).listen(port,()=>console.log('up',port));
