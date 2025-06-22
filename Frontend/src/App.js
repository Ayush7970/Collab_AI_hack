import React, { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';

// --- Reusable Style Objects ---
const styles = {
    app: { fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif", background: 'linear-gradient(135deg, #f3e7ff, #e3eeff)', color: '#333', width: '100vw', height: '100vh', overflow: 'hidden' },
    view: { width: '100%', height: '100%', position: 'absolute', top: 0, left: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', textAlign: 'center', opacity: 0, transition: 'opacity 0.5s ease-in-out', pointerEvents: 'none' },
    viewActive: { opacity: 1, pointerEvents: 'auto' },
    canvas: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 1, cursor: 'pointer' },
    textContent: { position: 'relative', zIndex: 2, color: '#443c68', textShadow: '0px 1px 3px rgba(255, 255, 255, 0.5)', pointerEvents: 'none' },
    h1: { fontSize: 'clamp(2.5rem, 6vw, 4rem)', margin: '0 0 0.5rem 0' },
    tagline: { fontSize: 'clamp(1rem, 2.5vw, 1.25rem)', opacity: 0.8, maxWidth: '500px', margin: '0 auto' },
    modalOverlay: { position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0, 0, 0, 0.4)', backdropFilter: 'blur(5px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 },
    modalBubble: { background: '#fff', padding: '25px 35px', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0,0,0,0.2)', width: '90%', maxWidth: '500px', maxHeight: '90vh', overflowY: 'auto', position: 'relative', textAlign: 'left' },
    modalClose: { position: 'absolute', top: '15px', right: '15px', fontSize: '24px', color: '#aaa', cursor: 'pointer', border: 'none', background: 'none' },
    formGroup: { marginBottom: '15px' },
    formLabel: { display: 'block', marginBottom: '5px', fontWeight: 500 },
    formInput: { width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '8px', boxSizing: 'border-box', fontFamily: 'inherit' },
    primaryButton: { background: 'linear-gradient(135deg, #6a11cb, #2575fc)', color: 'white', border: 'none', padding: '12px 20px', borderRadius: '8px', cursor: 'pointer', fontSize: '16px', width: '100%', marginTop: '10px', transition: 'transform 0.2s, box-shadow 0.2s' },
    contentContainer: { width: '100%', maxHeight: '70vh' },
    // --- PROFILE PAGE STYLES ---
    profilePageContainer: { width: '100%', height: '100%', display: 'flex', flexDirection: 'row', alignItems: 'flex-start', padding: '20px', boxSizing: 'border-box', overflowY: 'auto', background: 'linear-gradient(135deg, #f3e7ff, #e3eeff)' },
    sidePanel: { flex: '0 0 250px', marginRight: '40px', textAlign: 'left' },
    mainContent: { flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' },
    profileHeader: { display: 'flex', alignItems: 'center', width: '100%', maxWidth: '900px', marginBottom: '20px' },
    profilePic: { width: '150px', height: '150px', borderRadius: '50%', objectFit: 'cover', marginRight: '40px', border: '3px solid white', boxShadow: '0 4px 10px rgba(0,0,0,0.1)', flexShrink: 0 },
    profileInfo: { textAlign: 'left', flexGrow: 1 },
    profileName: { fontSize: '2rem', fontWeight: 'bold', margin: 0 },
    profileBio: { fontSize: '1rem', margin: '10px 0', whiteSpace: 'pre-wrap' },
    portfolioLink: { display: 'block', color: '#6a11cb', textDecoration: 'none', marginBottom: '5px' },
    statsContainer: { display: 'flex', gap: '30px', marginTop: '10px' },
    statItem: { textAlign: 'center' },
    statNumber: { fontSize: '1.2rem', fontWeight: 'bold' },
    statLabel: { fontSize: '0.9rem', color: '#555' },
    contentGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '15px', width: '100%', maxWidth: '900px', padding: '20px 0' },
    contentThumbnail: { width: '100%', height: '250px', objectFit: 'cover', borderRadius: '10px', cursor: 'pointer', transition: 'transform 0.2s', '&:hover': { transform: 'scale(1.05)' } },
    reUploadButton: { position: 'fixed', bottom: '30px', right: '30px', width: '60px', height: '60px', borderRadius: '50%', background: 'linear-gradient(135deg, #6a11cb, #2575fc)', color: 'white', fontSize: '30px', border: 'none', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', boxShadow: '0 4px 12px rgba(0,0,0,0.3)', zIndex: 1001 },
    collaboratorCard: { background: 'white', padding: '20px', borderRadius: '10px', boxShadow: '0 4px 10px rgba(0,0,0,0.1)', width: '300px' }
};

// --- Landing Page 3D Scene Component ---
const LandingScene = ({ onNodeClick }) => {
    const mountRef = useRef(null);
    const hoverLabelRef = useRef(null);

    useEffect(() => {
        const mountNode = mountRef.current;
        if (!mountNode) return;
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 220;
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        mountNode.appendChild(renderer.domElement);

        const nodesData = [
            { label: "🎵 Music", creators: ["Mozart", "Bowie", "Björk"], position: new THREE.Vector3(-120, 70, -40) },
            { label: "🎨 Art", creators: ["Frida Kahlo", "da Vinci", "Warhol"], position: new THREE.Vector3(100, 120, 10) },
            { label: "✍️ Poetry", creators: ["Maya Angelou", "Shakespeare", "Rumi"], position: new THREE.Vector3(-140, -90, -60) },
            { label: "👗 Fashion", creators: ["Coco Chanel", "McQueen", "Miyake"], position: new THREE.Vector3(150, -60, 50) },
            { label: "💡 Design", creators: ["Dieter Rams", "Zaha Hadid", "Saul Bass"], position: new THREE.Vector3(10, -20, -100) },
            { label: "🎬 Film", creators: ["Kubrick", "DuVernay", "Miyazaki"], position: new THREE.Vector3(120, 30, 120) },
            { label: "💻 Code", creators: ["Torvalds", "Hopper", "Nakamoto"], position: new THREE.Vector3(-110, 10, 110) }
        ];

        const nodes = [];
        nodesData.forEach(data => {
            const geometry = new THREE.SphereGeometry(15, 32, 32);
            const material = new THREE.MeshBasicMaterial({ color: new THREE.Color(Math.random(), Math.random(), Math.random()).getHex() });
            const node = new THREE.Mesh(geometry, material);
            node.position.copy(data.position);
            node.userData = data;
            nodes.push(node);
            scene.add(node);
        });

        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        let hoveredNode = null;

        const onMouseMove = (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            if(hoverLabelRef.current) {
                hoverLabelRef.current.style.left = `${event.clientX + 15}px`;
                hoverLabelRef.current.style.top = `${event.clientY + 15}px`;
            }
        };
        window.addEventListener('mousemove', onMouseMove);

        const handleClick = () => { if (hoveredNode) onNodeClick(); }
        mountNode.addEventListener('click', handleClick);

        let animationFrameId;
        const animate = () => {
            animationFrameId = requestAnimationFrame(animate);
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(nodes);

            if(intersects.length > 0) {
                hoveredNode = intersects[0].object;
                if(hoverLabelRef.current) {
                    hoverLabelRef.current.style.display = 'block';
                    hoverLabelRef.current.innerHTML = `<strong>${hoveredNode.userData.label}</strong><br/>${hoveredNode.userData.creators.join('<br/>')}`;
                }
            } else {
                hoveredNode = null;
                if(hoverLabelRef.current) hoverLabelRef.current.style.display = 'none';
            }

            nodes.forEach(node => { node.scale.lerp(node === hoveredNode ? new THREE.Vector3(1.5,1.5,1.5) : new THREE.Vector3(1,1,1), 0.1); });
            scene.rotation.y += 0.001;
            scene.rotation.x += 0.0005;
            renderer.render(scene, camera);
        };
        animate();

        return () => {
            cancelAnimationFrame(animationFrameId);
            window.removeEventListener('mousemove', onMouseMove);
            if(mountNode) mountNode.removeEventListener('click', handleClick);
            if (mountNode && renderer.domElement) {
                try { mountNode.removeChild(renderer.domElement); } catch (e) {}
            }
        };
    }, [onNodeClick]);

    return (
        <>
            <div ref={mountRef} style={styles.canvas} />
            <div ref={hoverLabelRef} style={{...styles.modalBubble, display: 'none', position: 'absolute', zIndex: 3, pointerEvents: 'none'}}></div>
        </>
    );
};

// --- NEW Profile Page Component ---
const ProfilePage = ({ profileData, onContentClick, onCollaborateClick, onReUploadClick }) => {
    const { name, bio, uploads = {}, portfolioLinks = [] } = profileData;
    const contentToDisplay = Object.keys(uploads).filter(key => key !== 'profilePic').map(key => ({ type: key, data: uploads[key] }));
    const contentCount = contentToDisplay.length;

    return (
        <div style={styles.profilePageContainer}>
            <div style={styles.sidePanel}>
                <h3>Similar Artists</h3>
                {/* Placeholder for similar artists list */}
                <p style={{fontSize:'0.8rem', color:'#777'}}>Coming soon...</p>
            </div>
            <div style={styles.mainContent}>
                <header style={styles.profileHeader}>
                    <img src={uploads.profilePic || 'https://placehold.co/150x150/e3eeff/443c68?text=?'} alt="Profile" style={styles.profilePic} />
                    <div style={styles.profileInfo}>
                        <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                           <h2 style={styles.profileName}>{name || 'Username'}</h2>
                           <button style={{ ...styles.primaryButton, width: 'auto', marginTop: 0 }} onClick={onCollaborateClick}>Find Collaborators 🚀</button>
                        </div>
                        <div style={styles.statsContainer}>
                            <div style={styles.statItem}><div style={styles.statNumber}>{contentCount}</div><div style={styles.statLabel}>Content</div></div>
                            <div style={styles.statItem}><div style={styles.statNumber}>0</div><div style={styles.statLabel}>Active Collabs</div></div>
                            <div style={styles.statItem}><div style={styles.statNumber}>0</div><div style={styles.statLabel}>Past Collabs</div></div>
                        </div>
                    </div>
                </header>
                <div style={{...styles.profileInfo, width: '100%', maxWidth: '900px', marginBottom: '20px'}}>
                    <p style={styles.profileBio}>{bio || 'No bio yet.'}</p>
                    {portfolioLinks.length > 0 && <h4>Portfolio:</h4>}
                    {portfolioLinks.map((link, index) => <a key={index} href={link} target="_blank" rel="noopener noreferrer" style={styles.portfolioLink}>{link}</a>)}
                </div>
                <hr style={{ width: '100%', maxWidth: '900px', border: 'none', borderTop: '1px solid #ddd' }} />
                <main style={styles.contentGrid}>
                    {contentToDisplay.length === 0 ? (<p>No content uploaded yet. Click the '+' button to add some!</p>) : (
                        contentToDisplay.map(({ type, data }) => (
                            <div key={type} onClick={() => onContentClick(type, data)}>
                                {type === 'image' && <img src={data} alt="upload" style={styles.contentThumbnail} />}
                                {type === 'video' && <video src={data} style={styles.contentThumbnail} />}
                                {type === 'audio' && <div style={{ ...styles.contentThumbnail, background: '#eee', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '4rem' }}>🎵</div>}
                                {type === 'text' && <div style={{ ...styles.contentThumbnail, background: '#eee', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '4rem' }}>📝</div>}
                            </div>
                        ))
                    )}
                </main>
            </div>
            <button style={styles.reUploadButton} onClick={onReUploadClick}>+</button>
        </div>
    );
};


// --- Modal Components ---
const ProfileModal = ({ onSubmit, onClose }) => {
    const [formData, setFormData] = useState({ portfolioLinks: ['', '', '', ''], isCollaborating: true, uploads: {} });
    
    const handleFormChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
    };
    
    const handlePortfolioChange = (index, value) => {
        const newLinks = [...formData.portfolioLinks];
        newLinks[index] = value;
        setFormData(prev => ({ ...prev, portfolioLinks: newLinks }));
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                setFormData(prev => ({
                    ...prev,
                    uploads: { ...prev.uploads, profilePic: event.target.result }
                }));
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSubmit = () => {
        const finalData = { ...formData, portfolioLinks: formData.portfolioLinks.filter(link => link) };
        onSubmit(finalData);
    };

    return (
        <div style={styles.modalOverlay}>
            <div style={styles.modalBubble}>
                <button style={styles.modalClose} onClick={onClose}>&times;</button>
                <h2>Create Your Profile</h2>
                <div style={styles.formGroup}>
                    <label style={{...styles.formLabel, cursor:'pointer', color:'#6a11cb', textDecoration:'underline'}} htmlFor="pfp-upload">Upload Profile Picture</label>
                    <input id="pfp-upload" type="file" accept="image/*" onChange={handleFileChange} style={{display:'none'}} />
                </div>
                <div style={styles.formGroup}><label style={styles.formLabel}>Name</label><input style={styles.formInput} name="name" onChange={handleFormChange}/></div>
                <div style={styles.formGroup}><label style={styles.formLabel}>Age</label><input type="number" style={styles.formInput} name="age" onChange={handleFormChange}/></div>
                <div style={styles.formGroup}><label style={styles.formLabel}>Gender Identity (Optional)</label><input style={styles.formInput} name="gender" onChange={handleFormChange}/></div>
                <div style={styles.formGroup}><label style={styles.formLabel}>Bio</label><textarea style={styles.formInput} name="bio" placeholder="Tell us about your creative journey..." onChange={handleFormChange}/></div>
                <div style={styles.formGroup}>
                    <label style={styles.formLabel}>Portfolio Links</label>
                    {formData.portfolioLinks.map((link, index) => (
                        <input key={index} style={{...styles.formInput, marginBottom:'8px'}} placeholder={index === 0 ? "e.g., SoundCloud, YouTube, Behance" : `Link ${index + 1}`} value={link} onChange={(e) => handlePortfolioChange(index, e.target.value)} />
                    ))}
                </div>
                <div style={styles.formGroup}>
                    <label><input type="checkbox" name="isCollaborating" checked={formData.isCollaborating} onChange={handleFormChange}/> Open to Collaborate?</label>
                </div>
                <button style={styles.primaryButton} onClick={handleSubmit}>Create Profile</button>
            </div>
        </div>
    );
};

const CollaborationModal = ({ onSubmit, onClose, isLoading }) => {
    const [description, setDescription] = useState('');
    return (
        <div style={styles.modalOverlay}>
            <div style={styles.modalBubble}>
                <button style={styles.modalClose} onClick={onClose}>&times;</button>
                <h2>Find a Collaborator</h2>
                <textarea style={{...styles.formInput, height: '120px'}} placeholder="Describe your ideal collaborator..." value={description} onChange={e => setDescription(e.target.value)} />
                <button style={styles.primaryButton} onClick={() => onSubmit(description)} disabled={isLoading}>{isLoading ? 'Searching...' : 'Launch Agents'}</button>
            </div>
        </div>
    );
};

const CollaboratorResultsPage = ({ results, onSelect }) => {
    return (
         <div>
            <h1 style={styles.h1}>Top 3 Matches</h1>
            <div style={{display: 'flex', gap: '20px'}}>
                {results.map(profile => (
                    <div key={profile.user_id} style={styles.collaboratorCard}>
                        <h3>{profile.name}</h3>
                        <p>{profile.bio}</p>
                        <button style={styles.primaryButton} onClick={() => onSelect(profile.user_id)}>Connect</button>
                    </div>
                ))}
            </div>
        </div>
    );
};


// --- Main App Component ---
function App() {
    const [view, setView] = useState('landing');
    const [modals, setModals] = useState({ profile: false, upload: false, collaborate: false, content: false });
    const [currentProfile, setCurrentProfile] = useState(null);
    const [collaborators, setCollaborators] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const openModal = (modal) => setModals(prev => ({...prev, [modal]: true}));
    const closeModal = (modal) => setModals(prev => ({...prev, [modal]: false}));

    const handleCreateProfile = async (profileDetails) => {
        const payload = {
            user_id: `user_${Date.now()}`,
            name: profileDetails.name || '',
            bio: profileDetails.bio || '',
            interests: profileDetails.interests || [],
            skills: profileDetails.skills || [],
            uploads: profileDetails.uploads || {},
            portfolioLinks: profileDetails.portfolioLinks || [],
            isCollaborating: profileDetails.isCollaborating,
        };
        
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:5001/create_profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`Backend Error: ${response.statusText}`);
            
            const result = await response.json();
            if(result.success) {
                setCurrentProfile(payload);
                closeModal('profile');
                setView('profile');
            } else {
                alert(`Error creating profile: ${result.message}`);
            }
        } catch (err) {
            console.error("Failed to create profile:", err);
            alert(`Failed to create profile. Is the Flask server and agent running? Error: ${err.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFindCollaborators = async (description) => {
    setIsLoading(true);
    try {
        const response = await fetch('http://localhost:5001/submit_collab_query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: description })
        });

        const result = await response.json();
        if (result.success) {
            alert("Query submitted to backend successfully.");
        } else {
            alert(`Backend responded with error: ${result.message}`);
        }
        closeModal('collaborate');
    } catch (err) {
        console.error("Error sending collaborator query:", err);
        alert(`Error sending query: ${err.message}`);
    } finally {
        setIsLoading(false);
    }
};
    
    return (
        <div style={styles.app}>
            <div style={{ ...styles.view, ...(view === 'landing' && styles.viewActive) }}>
                <LandingScene onNodeClick={() => openModal('profile')} />
                <div style={styles.textContent}><h1 style={styles.h1}>artseé</h1><p style={styles.tagline}>Join the community.</p></div>
            </div>

            <div style={{ ...styles.view, ...(view === 'profile' && styles.viewActive) }}>
                {currentProfile && <ProfilePage profileData={currentProfile} onCollaborateClick={() => openModal('collaborate')} />}
            </div>
            
            <div style={{...styles.view, ...(view === 'collaborators' && styles.viewActive)}}>
                <CollaboratorResultsPage results={collaborators} onSelect={(id) => alert(`Connecting with ${id}`)} />
            </div>

            {modals.profile && <ProfileModal onSubmit={handleCreateProfile} onClose={() => closeModal('profile')} />}
            {modals.collaborate && <CollaborationModal onSubmit={handleFindCollaborators} onClose={() => closeModal('collaborate')} isLoading={isLoading} />}
        </div>
    );
}

export default App;