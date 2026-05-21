/* ═══════════════════════════════════════
   DiBot — Main JS
   Animations, Tabs, Terminal, FAQ, Scroll
   ═══════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {
    initReveal();
    initNavbar();
    initMobileMenu();
    initTerminalTyping();
    initTabs();
    initCounters();
    initCopyButtons();
    initFAQ();
    initDocsSidebar();
    initSidebarActiveTracking();
    initSmoothScroll();
});

/* ─── Scroll Reveal ───────────────────── */
function initReveal() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const delay = (entry.target.dataset.delay || 0) * 60;
                    setTimeout(() => entry.target.classList.add("visible"), delay);
                }
            });
        },
        { threshold: 0.08, rootMargin: "0px 0px -30px 0px" }
    );

    document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));
}

/* ─── Navbar ──────────────────────────── */
function initNavbar() {
    const nav = document.getElementById("nav");
    if (!nav) return;

    window.addEventListener("scroll", () => {
        nav.classList.toggle("scrolled", window.scrollY > 40);
    });
}

/* ─── Mobile Menu ─────────────────────── */
function initMobileMenu() {
    const btn = document.getElementById("hamburger");
    const drawer = document.getElementById("mobileDrawer");
    if (!btn || !drawer) return;

    btn.addEventListener("click", () => {
        btn.classList.toggle("open");
        drawer.classList.toggle("open");
    });

    drawer.querySelectorAll(".drawer-link").forEach((link) => {
        link.addEventListener("click", () => {
            btn.classList.remove("open");
            drawer.classList.remove("open");
        });
    });
}

/* ─── Terminal Typing ─────────────────── */
function initTerminalTyping() {
    const termBody = document.querySelector(".term-body");
    if (!termBody) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    runTerminal();
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.3 }
    );

    observer.observe(termBody);
}

function runTerminal() {
    const lines = document.querySelectorAll(".term-line");
    lines.forEach((line, i) => {
        setTimeout(() => {
            line.classList.add("visible");
            const typed = line.querySelector(".typed");
            if (typed && typed.dataset.text) {
                typewriter(typed, typed.dataset.text, 25);
            }
        }, i * 500);
    });
}

function typewriter(el, text, speed) {
    el.textContent = "";
    let i = 0;
    (function type() {
        if (i < text.length) {
            el.textContent += text.charAt(i++);
            setTimeout(type, speed);
        }
    })();
}

/* ─── Tabs ────────────────────────────── */
function initTabs() {
    document.querySelectorAll(".tab-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.tab;

            btn.closest(".tabs") &&
                btn.closest(".section").querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");

            btn.closest(".section").querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
            const panel = document.getElementById(target);
            if (panel) panel.classList.add("active");
        });
    });
}

/* ─── Counter Animation ──────────────── */
function initCounters() {
    const nums = document.querySelectorAll(".stat-num");

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateNum(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.5 }
    );

    nums.forEach((n) => observer.observe(n));
}

function animateNum(el) {
    const target = parseInt(el.dataset.count);
    const duration = 1200;
    const start = performance.now();

    (function update(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(eased * target);
        if (progress < 1) requestAnimationFrame(update);
    })(start);
}

/* ─── Copy Buttons ────────────────────── */
function initCopyButtons() {
    // Hero terminal copy
    const heroCopy = document.getElementById("heroCopy");
    if (heroCopy) {
        heroCopy.addEventListener("click", () => {
            const cmds = [
                "git clone https://github.com/Compromisee/DiBot.git",
                "cd DiBot && pip install -r requirements.txt",
                "cp .env.example .env",
                "python bot.py",
            ].join("\n");
            copyToClipboard(heroCopy, cmds);
        });
    }

    // Doc copy buttons
    document.querySelectorAll(".copy-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            copyToClipboard(btn, btn.dataset.copy);
        });
    });
}

function copyToClipboard(btn, text) {
    navigator.clipboard.writeText(text).then(() => {
        const icon = btn.querySelector(".material-symbols-outlined");
        if (icon) {
            const orig = icon.textContent;
            icon.textContent = "check";
            icon.style.color = "var(--pastel-green)";
            setTimeout(() => {
                icon.textContent = orig;
                icon.style.color = "";
            }, 1500);
        }
    });
}

/* ─── FAQ Accordion ───────────────────── */
function initFAQ() {
    document.querySelectorAll(".faq-question").forEach((btn) => {
        btn.addEventListener("click", () => {
            const id = btn.dataset.faq;
            const answer = document.getElementById(id);
            if (!answer) return;

            const isOpen = btn.classList.contains("open");

            // Close all
            document.querySelectorAll(".faq-question").forEach((b) => b.classList.remove("open"));
            document.querySelectorAll(".faq-answer").forEach((a) => a.classList.remove("open"));

            if (!isOpen) {
                btn.classList.add("open");
                answer.classList.add("open");
            }
        });
    });
}

/* ─── Docs Sidebar ────────────────────── */
function initDocsSidebar() {
    const toggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("docsSidebar");
    if (!toggle || !sidebar) return;

    toggle.addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });

    // Close on link click (mobile)
    sidebar.querySelectorAll(".sidebar-link").forEach((link) => {
        link.addEventListener("click", () => {
            if (window.innerWidth <= 1024) {
                sidebar.classList.remove("open");
            }
        });
    });
}

/* ─── Sidebar Active Tracking ─────────── */
function initSidebarActiveTracking() {
    const links = document.querySelectorAll(".sidebar-link");
    if (!links.length) return;

    const articles = document.querySelectorAll(".doc-article");
    if (!articles.length) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    links.forEach((link) => {
                        link.classList.toggle(
                            "active",
                            link.getAttribute("href") === "#" + id
                        );
                    });
                }
            });
        },
        { threshold: 0.1, rootMargin: "-80px 0px -60% 0px" }
    );

    articles.forEach((article) => observer.observe(article));
}

/* ─── Smooth Scroll ───────────────────── */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((a) => {
        a.addEventListener("click", (e) => {
            e.preventDefault();
            const target = document.querySelector(a.getAttribute("href"));
            if (target) {
                target.scrollIntoView({ behavior: "smooth" });
            }
        });
    });
}
