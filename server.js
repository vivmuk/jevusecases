// Zero-dependency static server for the built site. No install step, no build step.
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const PORT = process.env.PORT || 3000;
const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.txt': 'text/plain; charset=utf-8',
  '.webp': 'image/webp',
};

const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  let file = path.join(ROOT, url === '/' ? 'index.html' : url);
  if (!file.startsWith(ROOT)) { res.writeHead(403).end('forbidden'); return; }
  fs.stat(file, (err, stat) => {
    if (err || stat.isDirectory()) {
      const fallback = path.join(ROOT, 'index.html');
      fs.readFile(fallback, (e2, buf) => {
        if (e2) { res.writeHead(404).end('not found'); return; }
        res.writeHead(200, { 'content-type': TYPES['.html'] }).end(buf);
      });
      return;
    }
    const ext = path.extname(file).toLowerCase();
    const cache = ext === '.png' ? 'public, max-age=604800' : 'public, max-age=300';
    fs.readFile(file, (e3, buf) => {
      if (e3) { res.writeHead(500).end('read error'); return; }
      res.writeHead(200, {
        'content-type': TYPES[ext] || 'application/octet-stream',
        'cache-control': cache,
        'x-content-type-options': 'nosniff',
      }).end(buf);
    });
  });
});

server.listen(PORT, () => console.log('jevusecases listening on ' + PORT));
