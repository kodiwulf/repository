import React from "https://esm.sh/react@19";
import { createRoot } from "https://esm.sh/react-dom@19/client";

const files = Array.isArray(window.KODIWULF_FILES) ? window.KODIWULF_FILES : [];
const treeData = window.KODIWULF_TREE || { roots: [], total_zips: files.length };
const h = React.createElement;

function childrenAt(path) {
  const prefix = path ? `${path}/` : "";
  const folders = new Set();
  const localFiles = [];
  files.forEach((file) => {
    if (!file.path.startsWith(prefix)) return;
    const rest = file.path.slice(prefix.length);
    const slash = rest.indexOf("/");
    if (slash === -1) localFiles.push(file);
    else folders.add(rest.slice(0, slash));
  });
  return { folders: [...folders].sort(), files: localFiles.sort((a, b) => a.name.localeCompare(b.name)) };
}

function ZipBrowser() {
  const [path, setPath] = React.useState("");
  const current = childrenAt(path);
  const parts = path ? path.split("/") : [];
  const go = (next) => {
    setPath(next);
    window.anime?.({ targets: "#react-browser .zip-entry", opacity: [0, 1], translateX: [-10, 0], delay: window.anime.stagger(18), duration: 260, easing: "easeOutQuad" });
  };
  const crumbs = [h("button", { className: "crumb", onClick: () => go(""), key: "root" }, "root")];
  parts.forEach((part, index) => {
    crumbs.push(h("span", { key: `sep-${index}` }, "/"));
    crumbs.push(h("button", { className: "crumb", onClick: () => go(parts.slice(0, index + 1).join("/")), key: part }, part));
  });
  const rows = [];
  if (path) rows.push(h("li", { className: "zip-entry", key: "up" }, h("span", { className: "type" }, "DIR"), h("button", { className: "zip-folder", onClick: () => go(parts.slice(0, -1).join("/")) }, "../"), h("span", { className: "zip-meta" }, "parent")));
  current.folders.forEach((folder) => rows.push(h("li", { className: "zip-entry", key: folder }, h("span", { className: "type" }, "DIR"), h("button", { className: "zip-folder zip-name", onClick: () => go(path ? `${path}/${folder}` : folder) }, `${folder}/`), h("span", { className: "zip-meta" }, "folder"))));
  current.files.forEach((file) => rows.push(h("li", { className: "zip-entry", key: file.path }, h("span", { className: "type" }, "ZIP"), h("a", { className: "zip-name", href: file.url }, file.name), h("span", { className: "zip-meta" }, file.category))));
  return h(React.Fragment, null,
    h("div", { className: "react-toolbar" }, h("nav", { className: "breadcrumbs", "aria-label": "ZIP-Pfad" }, crumbs), h("span", { className: "pill" }, `${current.folders.length + current.files.length} Einträge`)),
    h("ul", { className: "zip-list" }, rows.length ? rows : h("li", { className: "empty" }, "Keine ZIP-Dateien in diesem Ordner"))
  );
}

function boot() {
  const summary = document.getElementById("react-summary");
  if (summary) createRoot(summary).render(h("span", null, `${files.length} ZIP-Dateien`));
  const browser = document.getElementById("react-browser");
  if (browser) createRoot(browser).render(h(ZipBrowser));

  if (window.Vue && document.getElementById("vue-filter")) {
    window.Vue.createApp({
      data: () => ({ query: "" }),
      methods: {
        applyFilter() {
          const needle = this.query.trim().toLowerCase();
          document.querySelectorAll(".folder-row").forEach((row) => { row.hidden = needle && !row.dataset.folder.includes(needle); });
        },
        clearFilter() { this.query = ""; this.$nextTick(this.applyFilter); }
      }
    }).mount("#vue-filter");
  }

  if (window.d3 && document.getElementById("d3-chart")) {
    const data = treeData.roots || [];
    const width = Math.max(620, data.length * 96);
    const height = 160;
    const max = Math.max(1, ...data.map((d) => d.zip_count));
    const svg = window.d3.select("#d3-chart").append("svg").attr("viewBox", `0 0 ${width} ${height}`);
    const x = window.d3.scaleBand().domain(data.map((d) => d.name)).range([16, width - 16]).padding(.28);
    const y = window.d3.scaleLinear().domain([0, max]).range([118, 16]);
    svg.selectAll("rect").data(data).join("rect").attr("class", "bar").attr("x", (d) => x(d.name)).attr("y", (d) => y(d.zip_count)).attr("width", x.bandwidth()).attr("height", (d) => 118 - y(d.zip_count)).attr("rx", 5);
    svg.selectAll(".label").data(data).join("text").attr("class", "label").attr("x", (d) => x(d.name) + x.bandwidth() / 2).attr("y", 140).attr("text-anchor", "middle").text((d) => d.name);
    svg.selectAll(".value").data(data).join("text").attr("class", "value").attr("x", (d) => x(d.name) + x.bandwidth() / 2).attr("y", (d) => y(d.zip_count) - 5).attr("text-anchor", "middle").text((d) => d.zip_count);
  }

  window.jQuery?.(() => {
    window.jQuery(".folder-row").on("mouseenter mouseleave", function () { window.jQuery(this).toggleClass("is-hovered"); });
    window.jQuery(document).on("keydown", (event) => { if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") { event.preventDefault(); window.jQuery("#folder-search").trigger("focus"); } });
  });
  window.anime?.({ targets: ".animate-target", opacity: [0, 1], translateY: [18, 0], delay: window.anime.stagger(90), duration: 620, easing: "easeOutCubic" });
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
else boot();
