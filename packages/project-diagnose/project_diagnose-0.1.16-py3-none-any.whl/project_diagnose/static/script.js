// ================= ТЕМА =================

function applyTheme() {
    const theme = localStorage.getItem("project_diagnose_theme") || "light";
    const root = document.documentElement;
    const toggle = document.getElementById("themeToggle");

    if (theme === "dark") {
        root.classList.add("dark");
        if (toggle) toggle.checked = true;
    } else {
        root.classList.remove("dark");
        if (toggle) toggle.checked = false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    applyTheme();

    const toggle = document.getElementById("themeToggle");

    if (toggle) {
        toggle.addEventListener("change", () => {
            const theme = toggle.checked ? "dark" : "light";
            localStorage.setItem("project_diagnose_theme", theme);
            applyTheme();
        });
    }
});


// ============ COLLAPSIBLE PANELS ============
document.querySelectorAll(".collapsible").forEach(h => {
    h.addEventListener("click", () => {
        const content = h.nextElementSibling;
        h.classList.toggle("active");
        content.classList.toggle("open");
    });
});

// ============ КНОПКА «РЕФАКТОРИНГ» ============
document.getElementById("refactorBtn").addEventListener("click", () => {
    alert("Рефакторинг не реализован.\n\nНо проект явно намекает.");
});

// ============ ПОИСК В ОТЧЁТЕ ============
const searchInput = document.getElementById("searchInput");
const reportBlock = document.getElementById("reportBlock");
const originalText = reportBlock.textContent;

searchInput.addEventListener("input", () => {
    const q = searchInput.value.trim();
    if (!q) {
        reportBlock.textContent = originalText;
        return;
    }
    const regex = new RegExp(q, "gi");
    reportBlock.innerHTML = originalText.replace(regex, m => `<span class="highlight">${m}</span>`);
});

// ============ Chart.js: строки по расширениям ============
if (window.PROJECT_METRICS && window.PROJECT_METRICS.ext_lines) {
    const ctx = document.getElementById("extChart");
    if (ctx && window.Chart) {
        const labels = Object.keys(window.PROJECT_METRICS.ext_lines);
        const data = Object.values(window.PROJECT_METRICS.ext_lines);

        new Chart(ctx, {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    label: "Строк кода по расширениям",
                    data
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: false
                    }
                },
                scales: {
                    x: { ticks: { color: getComputedStyle(document.body).color } },
                    y: { ticks: { color: getComputedStyle(document.body).color } }
                }
            }
        });
    }
}
