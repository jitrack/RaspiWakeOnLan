// Service Worker for NAS Control PWA
const CACHE_NAME = 'nas-control-v2';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/api.js',
  '/static/js/state.js',
  '/static/js/modal.js',
  '/static/js/status.js',
  '/static/js/actions.js',
  '/static/js/schedule.js',
  '/static/js/app.js',
  '/static/favicon.ico',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/manifest.json',
];

// Install – cache static resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
      .catch((err) => console.log('SW cache error:', err))
  );
  self.skipWaiting();
});

// Activate – clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(
        names
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    )
  );
  self.clients.claim();
});

// Fetch – cache-first for static, network-first for API
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;

      return fetch(event.request.clone()).then((response) => {
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }

        if (event.request.url.includes('/static/')) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }

        return response;
      });
    })
  );
});
