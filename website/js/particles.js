/* ═══════════════════════════════════════
   Particle System — Connected Dots
   Minimalist floating particles with lines
   ═══════════════════════════════════════ */

(function () {
    const canvas = document.getElementById("particles");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let width, height;
    let particles = [];
    let mouse = { x: -1000, y: -1000 };
    let animId;

    const CONFIG = {
        count: 60,
        speed: 0.3,
        size: 1.5,
        connectDist: 140,
        mouseDist: 180,
        color: "196, 181, 253",    // pastel purple
        lineOpacity: 0.06,
        dotOpacity: 0.2,
        mouseLineOpacity: 0.12,
    };

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }

    function createParticle() {
        return {
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * CONFIG.speed,
            vy: (Math.random() - 0.5) * CONFIG.speed,
            size: Math.random() * CONFIG.size + 0.5,
        };
    }

    function init() {
        resize();
        particles = [];

        const count = Math.min(CONFIG.count, Math.floor((width * height) / 15000));
        for (let i = 0; i < count; i++) {
            particles.push(createParticle());
        }
    }

    function draw() {
        ctx.clearRect(0, 0, width, height);

        // Update + draw particles
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];

            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0) p.x = width;
            if (p.x > width) p.x = 0;
            if (p.y < 0) p.y = height;
            if (p.y > height) p.y = 0;

            // Draw dot
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${CONFIG.color}, ${CONFIG.dotOpacity})`;
            ctx.fill();

            // Connect to nearby particles
            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < CONFIG.connectDist) {
                    const opacity = (1 - dist / CONFIG.connectDist) * CONFIG.lineOpacity;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(${CONFIG.color}, ${opacity})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }

            // Connect to mouse
            const mdx = p.x - mouse.x;
            const mdy = p.y - mouse.y;
            const mDist = Math.sqrt(mdx * mdx + mdy * mdy);

            if (mDist < CONFIG.mouseDist) {
                const opacity = (1 - mDist / CONFIG.mouseDist) * CONFIG.mouseLineOpacity;
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(mouse.x, mouse.y);
                ctx.strokeStyle = `rgba(${CONFIG.color}, ${opacity})`;
                ctx.lineWidth = 0.6;
                ctx.stroke();
            }
        }

        animId = requestAnimationFrame(draw);
    }

    // Events
    window.addEventListener("resize", () => {
        cancelAnimationFrame(animId);
        init();
        draw();
    });

    window.addEventListener("mousemove", (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    window.addEventListener("mouseleave", () => {
        mouse.x = -1000;
        mouse.y = -1000;
    });

    // Reduce particles on mobile
    if (window.innerWidth < 768) {
        CONFIG.count = 25;
        CONFIG.connectDist = 100;
    }

    init();
    draw();
})();
