async function bootSvelteStatus() {
  const target = document.getElementById("svelte-status");
  if (!target) return;
  try {
    const [{ compile }, { mount }] = await Promise.all([
      import("https://esm.sh/svelte@5/compiler"),
      import("https://esm.sh/svelte@5")
    ]);
    const source = `<span><strong style="color:#98ffbb">● online</strong> · Svelte Status · Jekyll Daten geladen</span>`;
    let code = compile(source, { generate: "client", dev: false }).js.code;
    code = code.replaceAll('"svelte/internal/', '"https://esm.sh/svelte@5/internal/');
    const moduleUrl = URL.createObjectURL(new Blob([code], { type: "text/javascript" }));
    try {
      const { default: Status } = await import(moduleUrl);
      target.textContent = "";
      mount(Status, { target });
    } finally {
      URL.revokeObjectURL(moduleUrl);
    }
  } catch (error) {
    target.textContent = "● online · Svelte Status (Fallback)";
    target.dataset.error = error instanceof Error ? error.message : String(error);
  }
}

bootSvelteStatus();
