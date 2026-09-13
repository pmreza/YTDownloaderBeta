document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d', { alpha: false });
    
    let width = 0;
    let height = 0;
    
    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
    }
    
    window.addEventListener('resize', resize);
    resize();
    
    // Particle Configuration
    const numParticles = 200;
    const colors = ['rgba(252,165,165,0.7)', 'rgba(147,197,253,0.7)', 'rgba(253,224,71,0.7)', 'rgba(253,186,116,0.7)', 'rgba(226,232,240,0.7)', 'rgba(165,180,252,0.7)', 'rgba(103,232,249,0.7)'];
    const particles = [];
    
    for (let i = 0; i < numParticles; i++) {
        // Distribute particles across distance bands
        const band = Math.random();
        let rOffset = 0;
        if (band < 0.3) rOffset = Math.random() * 60;
        else if (band < 0.7) rOffset = 60 + Math.random() * 140;
        else rOffset = 200 + Math.random() * 300;
        
        particles.push({
            angle: Math.random() * Math.PI * 2,
            rOffset: rOffset,
            speed: (Math.random() * 0.0015 + 0.0002) * (Math.random() > 0.5 ? 1 : -1),
            color: colors[Math.floor(Math.random() * colors.length)],
            length: Math.random() * 0.15 + 0.02,
            yOffset: (Math.random() - 0.5) * 40, // spread the ring vertically a bit
            width: Math.random() * 4 + 2
        });
    }
    
    const tilt = 0.35; // perspective tilt of the ring (1 is top-down, 0 is side-on)
    const globalRotation = Math.PI / 6; // 30 degrees rotation of the whole system
    
    function drawPlanet(x, y, radius) {
        ctx.save();
        ctx.translate(x, y);
        
        // 1. Subtle Outer Glow (Atmosphere)
        const atmosphere = ctx.createRadialGradient(0, 0, radius * 0.9, 0, 0, radius * 1.3);
        atmosphere.addColorStop(0, 'rgba(56, 189, 248, 0.15)'); // Soft cyan glow
        atmosphere.addColorStop(1, 'rgba(33, 30, 59, 0)');
        
        ctx.beginPath();
        ctx.arc(0, 0, radius * 1.3, 0, Math.PI * 2);
        ctx.fillStyle = atmosphere;
        ctx.fill();
        
        // 2. The Planet Base (3D Sphere Gradient)
        // Light source from top-left
        const planetGrad = ctx.createRadialGradient(-radius * 0.3, -radius * 0.3, radius * 0.1, 0, 0, radius);
        planetGrad.addColorStop(0, '#94a3b8'); // Bright highlight
        planetGrad.addColorStop(0.5, '#475569'); // Mid-tone
        planetGrad.addColorStop(1, '#0f172a'); // Deep shadow
        
        ctx.beginPath();
        ctx.arc(0, 0, radius, 0, Math.PI * 2);
        ctx.fillStyle = planetGrad;
        ctx.fill();
        
        // 3. Inner Shadow for extra depth (darker on bottom-right edge)
        const innerShadow = ctx.createRadialGradient(radius * 0.2, radius * 0.2, radius * 0.4, 0, 0, radius);
        innerShadow.addColorStop(0, 'rgba(0,0,0,0)');
        innerShadow.addColorStop(1, 'rgba(0,0,0,0.7)');
        
        ctx.beginPath();
        ctx.arc(0, 0, radius, 0, Math.PI * 2);
        ctx.fillStyle = innerShadow;
        ctx.fill();
        
        ctx.restore();
    }
    
    let time = 0;
    
    function draw() {
        time += 0.006; // Smooth, slow rotation speed
        
        // Match the background color from style.css or use a deep space purplish color
        ctx.fillStyle = '#211e3b';
        ctx.fillRect(0, 0, width, height);
        
        const centerX = width / 2;
        const centerY = height / 2;
        const planetRadius = Math.max(120, Math.min(width, height) * 0.18);
        
        const behind = [];
        const front = [];
        
        particles.forEach(p => {
            p.angle += p.speed;
            
            // Determine if particle is behind or in front of planet
            // In our simple projection, sin(angle) < 0 is the back half of the ellipse
            if (Math.sin(p.angle) < 0) {
                behind.push(p);
            } else {
                front.push(p);
            }
        });
        
        function renderParticles(arr) {
            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(globalRotation);
            
            arr.forEach(p => {
                const r = planetRadius + 30 + p.rOffset;
                
                const x1 = Math.cos(p.angle) * r;
                const y1 = Math.sin(p.angle) * r * tilt + p.yOffset;
                
                const x2 = Math.cos(p.angle - p.length) * r;
                const y2 = Math.sin(p.angle - p.length) * r * tilt + p.yOffset;
                
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.strokeStyle = p.color;
                ctx.lineWidth = p.width;
                ctx.lineCap = 'round';
                ctx.stroke();
            });
            
            ctx.restore();
        }
        
        // Render order: behind particles -> planet -> front particles
        renderParticles(behind);
        drawPlanet(centerX, centerY, planetRadius);
        renderParticles(front);
        
        requestAnimationFrame(draw);
    }
    
    draw();
});
