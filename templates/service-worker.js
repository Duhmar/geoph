const CACHE_NAME = 'geoph-cache-v1';

// The essential files to save to the phone's hard drive
const urlsToCache = [
    '/',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap'
];

// Install the Service Worker and Cache the files
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log('Opened cache');
            return cache.addAll(urlsToCache);
        })
    );
});

// Intercept network requests and serve from Cache if Offline
self.addEventListener('fetch', event => {
    // Only cache GET requests
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request).then(response => {
                if (response) {
                    return response;
                }
                // If offline and file not cached, fallback to the home page
                if (event.request.headers.get('accept').includes('text/html')) {
                    return caches.match('/');
                }
            });
        })
    );
});