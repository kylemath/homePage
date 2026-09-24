(function () {
    var KEY = "theme";

    function systemTheme() {
        return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
    }

    function savedTheme() {
        try {
            var value = localStorage.getItem(KEY);
            return value === "light" || value === "dark" ? value : null;
        } catch (err) {
            return null;
        }
    }

    function apply(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        var button = document.querySelector(".theme-toggle");
        if (!button) return;
        var next = theme === "light" ? "dark" : "light";
        button.setAttribute("aria-pressed", theme === "light" ? "true" : "false");
        button.setAttribute("aria-label", "Switch to " + next + " mode");
        button.textContent = next === "light" ? "Light" : "Dark";
    }

    function persist(theme) {
        try { localStorage.setItem(KEY, theme); } catch (err) {}
        apply(theme);
    }

    var button = document.createElement("button");
    button.type = "button";
    button.className = "theme-toggle";
    button.addEventListener("click", function () {
        persist(document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light");
    });
    document.body.appendChild(button);
    apply(document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark");

    var media = window.matchMedia("(prefers-color-scheme: light)");
    function onSystemChange() {
        if (!savedTheme()) apply(systemTheme());
    }
    if (media.addEventListener) media.addEventListener("change", onSystemChange);
    else if (media.addListener) media.addListener(onSystemChange);
})();
