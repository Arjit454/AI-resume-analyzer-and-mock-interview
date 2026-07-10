// ---- custom cursor ----
const cursorDot = document.getElementById("cursorDot");
const cursorRing = document.getElementById("cursorRing");

let mouseX = 0, mouseY = 0;
let ringX = 0, ringY = 0;

window.addEventListener("mousemove", (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
  if (cursorDot) {
    cursorDot.style.left = mouseX + "px";
    cursorDot.style.top = mouseY + "px";
  }
});

function animateRing() {
  ringX += (mouseX - ringX) * 0.15;
  ringY += (mouseY - ringY) * 0.15;
  if (cursorRing) {
    cursorRing.style.left = ringX + "px";
    cursorRing.style.top = ringY + "px";
  }
  requestAnimationFrame(animateRing);
}
animateRing();

document.querySelectorAll("a, button, .faq-item summary").forEach((el) => {
  el.addEventListener("mouseenter", () => {
    if (cursorRing) {
      cursorRing.style.width = "50px";
      cursorRing.style.height = "50px";
      cursorRing.style.opacity = "0.9";
    }
  });
  el.addEventListener("mouseleave", () => {
    if (cursorRing) {
      cursorRing.style.width = "34px";
      cursorRing.style.height = "34px";
      cursorRing.style.opacity = "0.6";
    }
  });
});

// ---- theme toggle (dark / light) ----
const themeToggle = document.getElementById("themeToggle");
const htmlEl = document.documentElement;

const savedTheme = localStorage.getItem("careerstack-theme");
if (savedTheme) {
  htmlEl.setAttribute("data-theme", savedTheme);
}

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const current = htmlEl.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    htmlEl.setAttribute("data-theme", next);
    localStorage.setItem("careerstack-theme", next);

    if (document.body.dataset.authenticated === "true") {
      fetch("/profile/theme", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ theme: next }),
      }).catch(() => {});
    }
  });
}

// ---- mobile nav burger ----
const navBurger = document.getElementById("navBurger");
const navLinks = document.querySelector(".nav-links");
const navActions = document.querySelector(".nav-actions");

if (navBurger) {
  navBurger.addEventListener("click", () => {
    navBurger.classList.toggle("active");
    navLinks.style.display = navLinks.style.display === "flex" ? "none" : "flex";
    navActions.style.display = navActions.style.display === "flex" ? "none" : "flex";
  });
}

// ---- parallax blobs on scroll ----
const parallaxEls = document.querySelectorAll("[data-speed]");

window.addEventListener("scroll", () => {
  const scrollY = window.scrollY;
  parallaxEls.forEach((el) => {
    const speed = parseFloat(el.dataset.speed);
    el.style.transform = `translateY(${scrollY * speed}px)`;
  });
});

// ---- 3D tilt on the hero stamp card ----
const tiltCard = document.getElementById("tiltCard");

if (tiltCard) {
  tiltCard.addEventListener("mousemove", (e) => {
    const rect = tiltCard.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const rotateX = ((y / rect.height) - 0.5) * -14;
    const rotateY = ((x / rect.width) - 0.5) * 14;

    tiltCard.style.transform = `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
  });

  tiltCard.addEventListener("mouseleave", () => {
    tiltCard.style.transform = "perspective(1200px) rotateX(0deg) rotateY(0deg) scale(1)";
  });
}

// tilt for feature cards, a bit subtler
document.querySelectorAll(".tilt-card").forEach((card) => {
  card.addEventListener("mousemove", (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const rotateX = ((y / rect.height) - 0.5) * -6;
    const rotateY = ((x / rect.width) - 0.5) * 6;
    card.style.transform = `translateY(-6px) perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
  });
  card.addEventListener("mouseleave", () => {
    card.style.transform = "";
  });
});

// ---- scroll reveal + stat count-up + score ring, all via IntersectionObserver ----
const revealTargets = document.querySelectorAll(
  ".feature-card, .step, .testimonial-card, .faq-item, .section-head"
);
revealTargets.forEach((el) => el.classList.add("reveal"));

const statNumbers = document.querySelectorAll(".stat-number");
const scoreRing = document.querySelector(".score-ring");

function countUp(el) {
  const target = parseFloat(el.dataset.target);
  const isDecimal = target % 1 !== 0;
  const duration = 1400;
  const start = performance.now();

  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = target * eased;
    el.textContent = isDecimal ? value.toFixed(1) : Math.floor(value).toLocaleString();
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in-view");
      }
    });
  },
  { threshold: 0.2 }
);

revealTargets.forEach((el) => observer.observe(el));

const statsObserver = new IntersectionObserver(
  (entries, obs) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        statNumbers.forEach(countUp);
        obs.disconnect();
      }
    });
  },
  { threshold: 0.4 }
);
const statsSection = document.getElementById("stats");
if (statsSection) statsObserver.observe(statsSection);

if (scoreRing) {
  const ringObserver = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          scoreRing.classList.add("in-view");
          obs.disconnect();
        }
      });
    },
    { threshold: 0.5 }
  );
  ringObserver.observe(scoreRing);
}

// ---- password show/hide toggle on auth forms ----
document.querySelectorAll(".toggle-visibility").forEach((btn) => {
  btn.addEventListener("click", () => {
    const targetInput = document.getElementById(btn.dataset.target);
    if (!targetInput) return;
    const isHidden = targetInput.type === "password";
    targetInput.type = isHidden ? "text" : "password";
    btn.textContent = isHidden ? "Hide" : "Show";
  });
});
