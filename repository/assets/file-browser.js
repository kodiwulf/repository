(function () {
  const h = React.createElement;
  const files = Array.isArray(window.KODIWULF_FILES) ? window.KODIWULF_FILES : [];

  function directEntries(path) {
    const prefix = path ? path + "/" : "";
    const folders = new Set();
    const rows = [];
    files.forEach((file) => {
      if (!file.path.startsWith(prefix)) return;
      const rest = file.path.slice(prefix.length);
      const slash = rest.indexOf("/");
      if (slash >= 0) folders.add(rest.slice(0, slash));
      else rows.push(file);
    });
    return {
      folders: Array.from(folders).sort(),
      files: rows.sort((a, b) => a.name.localeCompare(b.name)),
    };
  }

  function App() {
    const [path, setPath] = React.useState("");
    const [glitch, setGlitch] = React.useState(false);
    const current = directEntries(path);

    function browse(next) {
      setGlitch(true);
      if (window.anime && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
        anime({
          targets: "#zip-list .entry",
          translateX: [0, 6, 0, -3, 0],
          opacity: [1, 0.5, 1],
          delay: anime.stagger(18),
          duration: 260,
          easing: "steps(4)",
        });
      }
      setTimeout(() => {
        setPath(next);
        setGlitch(false);
      }, 120);
    }

    const parts = path ? path.split("/") : [];
    const crumbs = [
      h("button", { className: "crumb", onClick: () => browse(""), "aria-current": path === "", key: "root" }, "root"),
    ];
    parts.forEach((part, index) => {
      crumbs.push(h("span", { className: "prompt", key: "slash-" + index }, "/"));
      crumbs.push(h("button", {
        className: "crumb",
        onClick: () => browse(parts.slice(0, index + 1).join("/")),
        "aria-current": index === parts.length - 1,
        key: "crumb-" + index,
      }, part));
    });

    const entries = [];
    if (path) {
      entries.push(h("button", { className: "entry", onClick: () => browse(parts.slice(0, -1).join("/")), key: "up" },
        h("span", { className: "glyph" }, "[..]"), h("span", { className: "name" }, "parent directory"), h("span", { className: "meta" }, "DIR")));
    }
    current.folders.forEach((folder) => entries.push(h("button", {
      className: "entry", onClick: () => browse(path ? path + "/" + folder : folder), key: "dir-" + folder,
    }, h("span", { className: "glyph" }, "[+]"), h("span", { className: "name" }, folder + "/"), h("span", { className: "meta" }, "DIR"))));
    current.files.forEach((file) => entries.push(h("a", { className: "entry", href: file.url, key: "file-" + file.path },
      h("span", { className: "glyph" }, "ZIP"), h("span", { className: "name" }, file.name), h("span", { className: "meta" }, file.category || "archive"))));

    return h("main", { className: "shell" },
      h("header", { className: "masthead" }, h("div", null, h("p", { className: "eyebrow" }, "kodiwulf // archive node"), h("h1", { className: "title" }, "ZIP file browser")), h("div", { className: "status" }, files.length + " packages indexed")),
      h("div", { className: "matrix-line" }),
      h("section", { className: "browser" + (glitch ? " glitching" : ""), "aria-label": "ZIP file browser" },
        h("div", { className: "toolbar" }, h("nav", { className: "breadcrumbs", "aria-label": "Path" }, crumbs), h("span", { className: "count" }, (current.folders.length + current.files.length) + " entries")),
        h("div", { id: "zip-list", className: "listing" }, entries.length ? entries : h("div", { className: "empty" }, "no ZIP files in this node"))));
  }

  ReactDOM.createRoot(document.getElementById("file-browser-root")).render(h(App));
})();
