const hoverLabel = document.getElementById("hover-label");
const container = document.getElementById("creative-dna-container");

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
container.appendChild(renderer.domElement);

camera.position.z = 150;

// --- Data with Example Creators ---
const nodesData = [
  { 
    label: "🎵 Music", 
    x: -50, y: 30, z: 0,
    creators: ["Beethoven", "David Bowie", "Daft Punk"]
  },
  { 
    label: "🎨 Art", 
    x: 40, y: 60, z: 20,
    creators: ["Leonardo da Vinci", "Yayoi Kusama", "Jean-Michel Basquiat"]
  },
  { 
    label: "✍️ Poetry", 
    x: -70, y: -40, z: -10,
    creators: ["Maya Angelou", "William Shakespeare", "Edgar Allan Poe"]
  },
  { 
    label: "👗 Fashion", 
    x: 70, y: -20, z: 30,
    creators: ["Coco Chanel", "Alexander McQueen", "Vivienne Westwood"]
  },
  { 
    label: "💡 Design", 
    x: 0, y: 0, z: -40,
    creators: ["Dieter Rams", "Paula Scher", "Saul Bass"]
  }
];

// --- Lighting for a more dynamic look ---
const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
scene.add(ambientLight);

const pointLight = new THREE.PointLight(0x00ffff, 1, 500);
pointLight.position.set(50, 50, 50);
scene.add(pointLight);

// --- Updated Materials and Geometry ---
const nodeGeometry = new THREE.SphereGeometry(8, 32, 32);
const nodeMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x00ffff, // Bright cyan color
    emissive: 0x00ffff, // Emissive property makes it glow
    emissiveIntensity: 0.3,
    metalness: 0.1,
    roughness: 0.4
});

const nodes = [];
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

nodesData.forEach(data => {
  const mesh = new THREE.Mesh(nodeGeometry.clone(), nodeMaterial.clone());
  mesh.position.set(data.x, data.y, data.z);
  // Store all data, including creators, in the mesh's userData
  mesh.userData = data; 
  scene.add(mesh);
  nodes.push(mesh);
});

function connectNodes() {
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const material = new THREE.LineBasicMaterial({ 
          color: 0x00ffff,
          transparent: true,
          opacity: 0.2
      });
      const points = [];
      points.push(nodes[i].position);
      points.push(nodes[j].position);
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(geometry, material);
      scene.add(line);
    }
  }
}

connectNodes();

function animate() {
  requestAnimationFrame(animate);
  scene.rotation.y += 0.002;
  scene.rotation.x += 0.0005;
  renderer.render(scene, camera);
}

function onMouseMove(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);

  const intersects = raycaster.intersectObjects(nodes);

  if (intersects.length > 0) {
    document.body.style.cursor = 'pointer';
    const obj = intersects[0].object;
    
    nodes.forEach(node => node.scale.set(1, 1, 1));
    obj.scale.set(1.5, 1.5, 1.5);
    
    const data = obj.userData;
    // --- Updated Hover Label Logic ---
    hoverLabel.innerHTML = `<strong>${data.label}</strong>${data.creators.join('<br>')}`;
    hoverLabel.style.left = `${event.clientX + 15}px`;
    hoverLabel.style.top = `${event.clientY + 15}px`;
    hoverLabel.style.display = "block";

  } else {
    document.body.style.cursor = 'default';
    hoverLabel.style.display = "none";
    nodes.forEach(node => node.scale.set(1, 1, 1));
  }
}

window.addEventListener("mousemove", onMouseMove);
animate();