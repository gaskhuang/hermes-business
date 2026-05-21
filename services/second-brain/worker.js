// Cloudflare Worker — Second Brain Memory Layer
// Deploy: wrangler deploy

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const headers = {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, X-API-Key',
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers });
    }

    // API Key auth
    const apiKey = request.headers.get('X-API-Key');
    if (apiKey !== env.API_KEY) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401, headers
      });
    }

    // POST /remember — store a memory
    if (request.method === 'POST' && path === '/remember') {
      const body = await request.json();
      const { key, value, type = 'fact', ttl, tags = [] } = body;

      if (!key || !value) {
        return new Response(JSON.stringify({ error: 'key and value required' }), {
          status: 400, headers
        });
      }

      const memory = {
        key,
        value,
        type,
        tags,
        updated: new Date().toISOString(),
        created: (await env.MEMORY.get(key)
          ? JSON.parse(await env.MEMORY.get(key)).created
          : new Date().toISOString()),
      };

      const options = ttl ? { expirationTtl: ttl } : {};
      await env.MEMORY.put(key, JSON.stringify(memory), options);

      return new Response(JSON.stringify({ ok: true, key, type }), { headers });
    }

    // GET /recall?key=xxx — get specific memory
    if (request.method === 'GET' && path === '/recall') {
      const key = url.searchParams.get('key');
      if (!key) {
        return new Response(JSON.stringify({ error: 'key required' }), {
          status: 400, headers
        });
      }

      const raw = await env.MEMORY.get(key);
      if (!raw) {
        return new Response(JSON.stringify({ found: false, key }), { headers });
      }

      return new Response(JSON.stringify({ found: true, ...JSON.parse(raw) }), { headers });
    }

    // GET /list?type=pref&limit=50 — list memories
    if (request.method === 'GET' && path === '/list') {
      const type = url.searchParams.get('type');
      const limit = parseInt(url.searchParams.get('limit') || '100');
      const prefix = type ? `${type}:` : '';

      const list = await env.MEMORY.list({ prefix, limit });
      const memories = await Promise.all(
        list.keys.map(async ({ name }) => {
          const raw = await env.MEMORY.get(name);
          return raw ? JSON.parse(raw) : null;
        })
      );

      const filtered = memories.filter(Boolean);

      return new Response(JSON.stringify({
        count: filtered.length,
        type: type || 'all',
        memories: filtered.sort((a, b) =>
          new Date(b.updated) - new Date(a.updated)
        )
      }), { headers });
    }

    // DELETE /forget?key=xxx — delete a memory
    if (request.method === 'DELETE' && path === '/forget') {
      const key = url.searchParams.get('key');
      if (!key) {
        return new Response(JSON.stringify({ error: 'key required' }), {
          status: 400, headers
        });
      }

      await env.MEMORY.delete(key);
      return new Response(JSON.stringify({ ok: true, deleted: key }), { headers });
    }

    // GET /health — health check
    if (request.method === 'GET' && path === '/health') {
      return new Response(JSON.stringify({
        status: 'ok',
        service: 'second-brain',
        timestamp: new Date().toISOString()
      }), { headers });
    }

    return new Response(JSON.stringify({ error: 'Not found', path }), {
      status: 404, headers
    });
  }
};
