// Service Worker Minimal
self.addEventListener('install', (event) => {
  console.log('Cogitron Service Worker installé !');
});

self.addEventListener('fetch', (event) => {
  // Nécessaire pour que l'app soit considérée comme PWA
  event.respondWith(fetch(event.request));
});
