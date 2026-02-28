"""
PWA Configuration Module

This module provides functions to generate Progressive Web App (PWA) configuration files
including manifest.json and service worker JavaScript for offline capabilities.
"""

import json
import os
from pathlib import Path
from typing import Dict


def generate_manifest() -> Dict:
    """
    Generate PWA manifest.json content as a dictionary.
    
    Returns:
        dict: Complete manifest configuration with app metadata, icons, and display settings
    """
    manifest = {
        "name": "O-Zone Air Quality Monitor",
        "short_name": "O-Zone",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#1f77b4",
        "description": "Real-time air quality monitoring and health recommendations",
        "icons": [
            {
                "src": "/static/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "/static/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    }
    return manifest


def generate_service_worker() -> str:
    """
    Generate service worker JavaScript code for offline capabilities.
    
    Implements:
    - Cache-first strategy for static assets (CSS, JS, icons)
    - Network-first strategy for API calls (OpenAQ, Bedrock)
    - Offline fallback for when network is unavailable
    
    Returns:
        str: Complete service worker JavaScript code
    """
    service_worker_js = """
// O-Zone Service Worker
// Version: 1.0.0

const CACHE_NAME = 'ozone-cache-v1';
const STATIC_CACHE = 'ozone-static-v1';
const API_CACHE = 'ozone-api-v1';

// Static assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/manifest.json'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[Service Worker] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE && cacheName !== API_CACHE) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Cache-first strategy for static assets
  if (request.destination === 'image' || 
      request.destination === 'style' || 
      request.destination === 'script' ||
      url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(request).then((response) => {
          // Cache successful responses
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(STATIC_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        });
      })
    );
    return;
  }

  // Network-first strategy for API calls
  if (url.hostname.includes('api.openaq.org') || 
      url.hostname.includes('bedrock') ||
      url.hostname.includes('amazonaws.com')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache successful API responses
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(API_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Fallback to cache if network fails
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // Return offline fallback
            return new Response(
              JSON.stringify({ error: 'Offline - cached data unavailable' }),
              { 
                headers: { 'Content-Type': 'application/json' },
                status: 503
              }
            );
          });
        })
    );
    return;
  }

  // Default: network-first for everything else
  event.respondWith(
    fetch(request).catch(() => {
      return caches.match(request).then((cachedResponse) => {
        return cachedResponse || new Response('Offline', { status: 503 });
      });
    })
  );
});
""".strip()
    
    return service_worker_js


def setup_pwa_files() -> None:
    """
    Create manifest.json and sw.js files in the static/ directory.
    
    Creates the static directory if it doesn't exist, then writes:
    - manifest.json: PWA manifest configuration
    - sw.js: Service worker JavaScript for offline capabilities
    
    Raises:
        IOError: If unable to create files or directory
        PermissionError: If lacking permissions to write files
    """
    try:
        # Create static directory if it doesn't exist
        static_dir = Path('static')
        static_dir.mkdir(exist_ok=True)
        
        # Generate and write manifest.json
        manifest = generate_manifest()
        manifest_path = static_dir / 'manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        print(f"✓ Created {manifest_path}")
        
        # Generate and write service worker
        service_worker = generate_service_worker()
        sw_path = static_dir / 'sw.js'
        with open(sw_path, 'w', encoding='utf-8') as f:
            f.write(service_worker)
        print(f"✓ Created {sw_path}")
        
    except (IOError, PermissionError) as e:
        print(f"⚠️ PWA setup failed: {e}")
        raise


if __name__ == "__main__":
    # Test the PWA configuration generation
    print("Testing PWA configuration generation...\n")
    
    # Test manifest generation
    print("1. Testing manifest generation:")
    manifest = generate_manifest()
    print(f"   - Name: {manifest['name']}")
    print(f"   - Display: {manifest['display']}")
    print(f"   - Icons: {len(manifest['icons'])} icons")
    print(f"   ✓ Manifest generated successfully\n")
    
    # Test service worker generation
    print("2. Testing service worker generation:")
    sw = generate_service_worker()
    print(f"   - Length: {len(sw)} characters")
    print(f"   - Contains cache-first: {'cache-first' in sw.lower()}")
    print(f"   - Contains network-first: {'network-first' in sw.lower()}")
    print(f"   ✓ Service worker generated successfully\n")
    
    # Test file setup
    print("3. Testing PWA file setup:")
    setup_pwa_files()
    print(f"   ✓ PWA files created successfully")
