/* ═══════════════════════════════════════════
   DiBot — Main JavaScript
   Animations, Terminal, Tabs, Scroll Effects
   ═══════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {
    initScrollAnimations();
    initNavbar();
    initMobileMenu();
    initCursorGlow();
    initFeatureCardGlow();
    initTerminal();
    initTabs();
    initCounters();
    initTerminalCopy();
    initSmoothScroll();
});

/* ─── Scroll Animations ───────────────── */
function initScrollAnimations() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const delay = entry.target.dataset.delay || 0;
                    setTimeout(() => {
                        entry.target.classList.add("visible");
                    }, delay * 80);
                }
            });
        },
        { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );

    document.querySelectorAll(".animate-on-scroll").forEach((el) => {
        observer.observe(el);
    });
}

/* ─── Navbar Scroll ───────────────────── */
function initNavbar() {
    const nav = document.getElementById("nav");
    let lastScroll = 0;

    window.addEventListener("scroll", () => {
        const currentScroll = window.scrollY;

        if (currentScroll > 50) {
            nav.classList.add("scrolled");
        } else {
            nav.classList.remove("scrolled");
        }

        lastScroll = currentScroll;
    });
}

/* ─── Mobile Menu ─────────────────────── */
function initMobileMenu() {
    const toggle = document.getElementById("navToggle");
    const menu = document.getElementById("mobileMenu");

    if (!toggle || !menu) return;

    toggle.addEventListener("click", () => {
        toggle.classList.toggle("active");
        menu.classList.toggle("open");
    });

    menu.querySelectorAll(".mobile-link").forEach((link) => {
        link.addEventListener("click", () => {
            toggle.classList.remove("active");
            menu.classList.remove("open");
        });
    });
}

/* ─── Cursor Glow ─────────────────────── */
function initCursorGlow() {
    const glow = document.getElementById("cursorGlow");
    if (!glow || window.innerWidth < 768) return;

    let mouseX = 0, mouseY = 0;
    let glowX = 0, glowY = 0;

    document.addEventListener("mousemove", (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        glow.style.opacity = "1";
    });

    document.addEventListener("mouseleave", () => {
        glow.style.opacity = "0";
    });

    function animateGlow() {
        glowX += (mouseX - glowX) * 0.08;
        glowY += (mouseY - glowY) * 0.08;
        glow.style.left = glowX + "px";
        glow.style.top = glowY + "px";
        requestAnimationFrame(animateGlow);
    }

    animateGlow();
}

/* ─── Feature Card Glow (Mouse Follow) ── */
function initFeatureCardGlow() {
    const grid = document.querySelector(".features-grid");
    if (!grid) return;

    grid.addEventListener("mousemove", (e) => {
        grid.querySelectorAll(".feature-card").forEach((card) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty("--mouse-x", x + "px");
            card.style.setProperty("--mouse-y", y + "px");
        });
    });
}

/* ─── Terminal Typing Animation ────────── */
function initTerminal() {
    const terminalBody = document.getElementById("terminalBody");
    if (!terminalBody) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    startTerminalAnimation();
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.3 }
    );

    observer.observe(terminalBody);
}

function startTerminalAnimation() {
    const lines = document.querySelectorAll(".terminal-line");

    lines.forEach((line, index) => {
        const delay = index * 600;

        setTimeout(() => {
            line.style.animationDelay = "0s";
            line.style.animation = "terminalFadeIn 0.3s forwards";

            // Typing effect for command lines
            const cmdSpan = line.querySelector(".terminal-cmd");
            if (cmdSpan && cmdSpan.dataset.text) {
                typeText(cmdSpan, cmdSpan.dataset.text, 30);
            }
        }, delay);
    });
}

function typeText(element, text, speed) {
    let index = 0;
    element.textContent = "";

    function type() {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            index++;
            setTimeout(type, speed);
        }
    }

    type();
}

/* ─── Tabs ────────────────────────────── */
function initTabs() {
    const tabs = document.querySelectorAll(".tab");
    const panels = document.querySelectorAll(".commands-panel");

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            const target = tab.dataset.tab;

            tabs.forEach((t) => t.classList.remove("active"));
            panels.forEach((p) => p.classList.remove("active"));

            tab.classList.add("active");
            const panel = document.getElementById("panel-" + target);
            if (panel) panel.classList.add("active");
        });
    });
}

/* ─── Counter Animation ──────────────── */
function initCounters() {
    const counters = document.querySelectorAll(".stat-number");

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.5 }
    );

    counters.forEach((counter) => observer.observe(counter));
}

function animateCounter(element) {
    const target = parseInt(element.dataset.count);
    const duration = 1500;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(eased * target);

        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

/* ─── Terminal Copy ──────────────────── */
function initTerminalCopy() {
    const copyBtn = document.getElementById("terminalCopy");
    if (!copyBtn) return;

    copyBtn.addEventListener("click", () => {
        const commands = [
            "git clone https://github.com/Compromisee/DiBot.git",
            "cd DiBot && pip install -r requirements.txt",
            "cp .env.example .env && nano .env",
            "python bot.py",
        ].join("\n");

        navigator.clipboard.writeText(commands).then(() => {
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>`;
            copyBtn.style.color = "var(--green)";

            setTimeout(() => {
                copyBtn.innerHTML = originalHTML;
                copyBtn.style.color = "";
            }, 2000);
        });
    });
}

/* ─── Smooth Scroll ──────────────────── */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", (e) => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute("href"));
            if (target) {
                target.scrollIntoView({ behavior: "smooth" });
            }
        });
    });
}