import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';

var AMBER = 0xf59e0b;
var AMBER_DIM = 0x78350f;
var INK_DIM = 0x6b7280;

var CITIES = [
  ['London', 51.5074, -0.1278],
  ['Paris', 48.8566, 2.3522],
  ['Berlin', 52.52, 13.405],
  ['Madrid', 40.4168, -3.7038],
  ['Rome', 41.9028, 12.4964],
  ['Amsterdam', 52.3676, 4.9041],
  ['Brussels', 50.8503, 4.3517],
  ['Vienna', 48.2082, 16.3738],
  ['Warsaw', 52.2297, 21.0122],
  ['Copenhagen', 55.6761, 12.5683],
  ['Stockholm', 59.3293, 18.0686],
  ['Helsinki', 60.1699, 24.9384],
  ['Oslo', 59.9139, 10.7522],
  ['Dublin', 53.3498, -6.2603],
  ['Tallinn', 59.437, 24.7536],
  ['Riga', 56.9496, 24.1052],
  ['Vilnius', 54.6872, 25.2797],
  ['Prague', 50.0755, 14.4378],
  ['Lisbon', 38.7223, -9.1393],
  ['Athens', 37.9838, 23.7275],
];

var ARCS = [
  [0, 1], [0, 5], [0, 13], [0, 2], [0, 9],
  [1, 2], [1, 3], [1, 4],
  [2, 7], [2, 8], [2, 17],
  [5, 6], [5, 11],
  [9, 10], [9, 12], [10, 11], [10, 14],
  [11, 15], [15, 16], [16, 8],
  [4, 7], [7, 8], [17, 8],
  [14, 9], [14, 15],
];

function latLonToVec3(lat, lon, r) {
  r = r || 1;
  var phi = (90 - lat) * Math.PI / 180;
  var theta = (lon + 180) * Math.PI / 180;
  return new THREE.Vector3(
    -r * Math.sin(phi) * Math.cos(theta),
    r * Math.cos(phi),
    r * Math.sin(phi) * Math.sin(theta)
  );
}

function arc(a, b, lift, segments) {
  lift = lift || 0.25;
  segments = segments || 48;
  var start = a.clone();
  var end = b.clone();
  var mid = start.clone().add(end).multiplyScalar(0.5).normalize().multiplyScalar(1 + lift);
  var pts = [];
  for (var i = 0; i <= segments; i++) {
    var t = i / segments;
    var p = start.clone().multiplyScalar((1 - t) * (1 - t))
      .add(mid.clone().multiplyScalar(2 * (1 - t) * t))
      .add(end.clone().multiplyScalar(t * t));
    pts.push(p);
  }
  return pts;
}

function init() {
  var container = document.getElementById('three-hero');
  if (!container) return;

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var width = container.clientWidth;
  var height = container.clientHeight;

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
  camera.position.set(0, 0.7, 3.6);
  camera.lookAt(0, 0, 0);

  var renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
  renderer.setSize(width, height);
  renderer.setClearColor(0x000000, 0);
  container.appendChild(renderer.domElement);

  var globe = new THREE.Group();
  scene.add(globe);

  var sphereGeom = new THREE.SphereGeometry(1, 40, 28);
  var wireMat = new THREE.LineBasicMaterial({ color: INK_DIM, transparent: true, opacity: 0.25 });
  var edges = new THREE.EdgesGeometry(sphereGeom);
  globe.add(new THREE.LineSegments(edges, wireMat));

  var fillMat = new THREE.MeshBasicMaterial({ color: 0x0f172a, transparent: true, opacity: 0.85 });
  globe.add(new THREE.Mesh(sphereGeom, fillMat));

  var cityPositions = CITIES.map(function (c) { return latLonToVec3(c[1], c[2], 1.005); });
  var dotGeom = new THREE.BufferGeometry().setFromPoints(cityPositions);
  var dotMat = new THREE.PointsMaterial({ color: AMBER, size: 0.035, transparent: true, opacity: 0.9 });
  globe.add(new THREE.Points(dotGeom, dotMat));

  var haloMat = new THREE.PointsMaterial({ color: AMBER, size: 0.09, transparent: true, opacity: 0.15 });
  var halos = new THREE.Points(dotGeom, haloMat);
  globe.add(halos);

  var arcObjects = [];
  ARCS.forEach(function (pair) {
    var pts = arc(cityPositions[pair[0]], cityPositions[pair[1]]);
    var geom = new THREE.BufferGeometry().setFromPoints(pts);
    var mat = new THREE.LineBasicMaterial({ color: AMBER_DIM, transparent: true, opacity: 0.5 });
    var line = new THREE.Line(geom, mat);
    globe.add(line);
    arcObjects.push({ line: line, pts: pts, phase: Math.random() * Math.PI * 2 });
  });

  var pulseMat = new THREE.PointsMaterial({ color: AMBER, size: 0.05, transparent: true, opacity: 0.95 });
  var pulsePositions = new Float32Array(arcObjects.length * 3);
  var pulseGeom = new THREE.BufferGeometry();
  pulseGeom.setAttribute('position', new THREE.BufferAttribute(pulsePositions, 3));
  globe.add(new THREE.Points(pulseGeom, pulseMat));

  globe.rotation.x = 0.45;
  globe.rotation.y = -0.6;

  var clock = new THREE.Clock();
  var targetFps = reduced ? 12 : 30;
  var minFrameTime = 1 / targetFps;
  var lastRender = 0;

  function animate() {
    requestAnimationFrame(animate);
    var t = clock.getElapsedTime();
    if (t - lastRender < minFrameTime) return;
    lastRender = t;

    if (!reduced) {
      globe.rotation.y += 0.0014;
    }

    haloMat.opacity = 0.12 + 0.06 * Math.sin(t * 1.2);

    arcObjects.forEach(function (a, idx) {
      var prog = ((t * 0.12) + a.phase) % 1;
      var segIdx = Math.floor(prog * (a.pts.length - 1));
      var p = a.pts[segIdx];
      pulsePositions[idx * 3] = p.x;
      pulsePositions[idx * 3 + 1] = p.y;
      pulsePositions[idx * 3 + 2] = p.z;
    });
    pulseGeom.attributes.position.needsUpdate = true;

    renderer.render(scene, camera);
  }

  animate();

  window.addEventListener('resize', function () {
    var w = container.clientWidth;
    var h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
