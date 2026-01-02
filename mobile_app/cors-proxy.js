/**
 * Simple CORS proxy for development
 * This proxies requests from the Flutter web app to the Odoo backend
 * and adds CORS headers to allow cross-origin requests
 */

const http = require('http');
const httpProxy = require('http-proxy');

// Create a proxy server
const proxy = httpProxy.createProxyServer({
  target: 'http://localhost:8069',
  changeOrigin: true,
  ws: true, // Enable WebSocket proxying
});

// Handle proxy errors
proxy.on('error', (err, req, res) => {
  console.error('Proxy error:', err);
  if (res.writeHead) {
    res.writeHead(500, {
      'Content-Type': 'text/plain',
      'Access-Control-Allow-Origin': '*',
    });
    res.end('Proxy error: ' + err.message);
  }
});

// Add CORS headers to all responses
proxy.on('proxyRes', (proxyRes, req, res) => {
  proxyRes.headers['Access-Control-Allow-Origin'] = '*';
  proxyRes.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS';
  proxyRes.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With';
  proxyRes.headers['Access-Control-Allow-Credentials'] = 'true';
});

// Create HTTP server
const server = http.createServer((req, res) => {
  // Handle preflight OPTIONS requests
  if (req.method === 'OPTIONS') {
    res.writeHead(200, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
      'Access-Control-Max-Age': '86400',
    });
    res.end();
    return;
  }

  // Log the request
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);

  // Proxy the request
  proxy.web(req, res);
});

// Handle WebSocket upgrade
server.on('upgrade', (req, socket, head) => {
  console.log(`${new Date().toISOString()} - WebSocket upgrade ${req.url}`);
  proxy.ws(req, socket, head);
});

// Start the server
const PORT = 8070;
server.listen(PORT, () => {
  console.log('='.repeat(60));
  console.log('CORS Proxy Server Started');
  console.log('='.repeat(60));
  console.log(`Proxy listening on: http://localhost:${PORT}`);
  console.log(`Proxying to: http://localhost:8069`);
  console.log('');
  console.log('Update your Flutter app to use: http://localhost:8070');
  console.log('='.repeat(60));
});

