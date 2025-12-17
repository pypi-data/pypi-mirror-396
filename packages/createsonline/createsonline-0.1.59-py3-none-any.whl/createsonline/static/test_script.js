console.log('CREATESONLINE v0.1.23 - monochrome build ready');

const features = [
  'Automatic static file serving from /static',
  'Zero-config route discovery with overrides',
  'Smart MIME type detection and caching',
  'Guardrails against path traversal',
  'Upgrade-safe templates and assets'
];

setTimeout(() => {
  console.group('CREATESONLINE runtime');
  features.forEach(feature => console.log('-', feature));
  console.groupEnd();
}, 100);
