function readServerCaps() {
    const el = document.getElementById("server-caps");
    if (!el) return {};
    const raw = (el.textContent ?? "").trim();

    // Your server should replace __DEFAULTS_CAPS__ with valid JSON.
    // If it didn't, or JSON is invalid, fall back safely.
    if (!raw || raw === "__DEFAULTS_CAPS__") return {};

    try {
        return JSON.parse(raw);
    } catch {
        return {};
    }
}

const CAPS_WRAPPER = readServerCaps();
const CAP = CAPS_WRAPPER.capabilities ?? {};
let state = structuredClone(CAPS_WRAPPER.current_settings ?? {});

const $ = (s) => document.querySelector(s);

// show description when enabled, reason when disabled
function optRadio({name, value, title, description, enabled, reason, checked}) {
    const dis = !enabled;
    const tip = (dis && reason) ? ` title="${String(reason).replaceAll('"', '&quot;')}"` : "";
    const sub = dis ? (reason ?? "") : (description ?? "");
    return `
    <label class="opt ${dis ? "is-disabled" : ""}" ${tip}>
      <input type="radio" name="${name}" value="${value}" ${checked ? "checked" : ""} ${dis ? "disabled" : ""}/>
      <div class="k">
        <b>${title}</b>
        <span>${sub}</span>
      </div>
    </label>
  `;
}

function renderDevices() {
    $("#deviceOptions").innerHTML = (CAP.devices ?? []).map(d =>
        optRadio({
            name: "device",
            value: d,
            title: d,
            description: d === "cpu" ? "CPU (slow, best for small models)" : "Accelerator",
            enabled: true,
            reason: null,
            checked: state.device === d,
        })
    ).join("");
    $("#dPill").textContent = state.device ?? "—";
}

function renderAttention() {
    const trad = [];
    const paged = [];
    for (const a of (CAP.attention_methods ?? [])) {
        const html = optRadio({
            name: "attn",
            value: a.value,
            title: a.label ?? a.value,
            description: a.description,
            enabled: !!a.enabled,
            reason: a.reason,
            checked: state.attention_method === a.value,
        });
        (a.paged ? paged : trad).push(html);
    }
    $("#attnTraditional").innerHTML = trad.join("");
    $("#attnPaged").innerHTML = paged.join("");
    $("#aPill").textContent = (state.attention_method ?? "—").replaceAll("_", " ");
}

function quantFlat() {
    const out = [];
    for (const entry of (CAP.quantization_methods ?? [])) {
        const [prec, opts] = Object.entries(entry)[0] ?? [];
        if (!prec || !opts) continue;
        for (const o of opts) out.push({prec, ...o});
    }
    return out;
}

function renderQuantization() {
    const rows = quantFlat();
    const precisions = rows.map(r => r.prec).filter((v, i, a) => a.indexOf(v) === i);

    const descByPrec = new Map();
    for (const r of rows) if (!descByPrec.has(r.prec)) descByPrec.set(r.prec, r.description ?? "");

    $("#quantPrecision").innerHTML = precisions.map(p =>
        optRadio({
            name: "precision",
            value: p,
            title: p,
            description: descByPrec.get(p) ?? "",
            enabled: true,
            reason: null,
            checked: state.quantization_method?.precision === p,
        })
    ).join("");

    const needsBackend = (state.quantization_method?.precision === "8-bit" || state.quantization_method?.precision === "4-bit");
    const fs = $("#backendFieldset");
    fs.style.display = needsBackend ? "block" : "none";
    fs.setAttribute("aria-hidden", needsBackend ? "false" : "true");

    if (needsBackend) {
        const backendRows = rows.filter(r => r.prec === state.quantization_method.precision && r.backend);
        $("#quantBackend").innerHTML = backendRows.map(r =>
            optRadio({
                name: "backend",
                value: r.backend,
                title: r.backend,
                description: r.description,
                enabled: !!r.enabled,
                reason: r.reason,
                checked: state.quantization_method?.backend === r.backend,
            })
        ).join("");
    } else {
        $("#quantBackend").innerHTML = "";
    }

    const p = state.quantization_method?.precision ?? "—";
    const b = state.quantization_method?.backend;
    $("#qPill").textContent = (p === "8-bit" || p === "4-bit") ? `${p} · ${b ?? "—"}` : p;
}

function renderContext() {
    const arr = CAP.context_lengths ?? [];
    const slider = $("#ctxSelect");
    const idx = Math.max(0, arr.indexOf(state.context_length));
    slider.min = "0";
    slider.max = String(Math.max(0, arr.length - 1));
    slider.step = "1";
    slider.value = String(idx);

    const v = arr[idx] ?? 0;
    $("#ctxHuman").textContent = `${v.toLocaleString()} tokens`;
    $("#ctxPill").textContent = v ? `${Math.round(v / 1024)}k` : "—";
}

function renderAll() {
    renderDevices();
    renderAttention();
    renderQuantization();
    renderContext();
}

function bind() {
    $("#wrap").addEventListener("change", (e) => {
        const t = e.target;
        if (!(t instanceof HTMLInputElement)) return;

        if (t.name === "device") {
            state.device = t.value;
            renderDevices();
            renderAttention();
            renderQuantization();
        }

        if (t.name === "attn") {
            state.attention_method = t.value;
            $("#aPill").textContent = t.value.replaceAll("_", " ");
        }

        if (t.name === "precision") {
            state.quantization_method = state.quantization_method ?? {precision: t.value, backend: null};
            state.quantization_method.precision = t.value;

            if (t.value === "8-bit" || t.value === "4-bit") {
                const rows = quantFlat().filter(r => r.prec === t.value && r.backend && r.enabled);
                state.quantization_method.backend = rows[0]?.backend ?? null;
            } else {
                state.quantization_method.backend = null;
            }
            renderQuantization();
        }

        if (t.name === "backend") {
            state.quantization_method.backend = t.value;
            renderQuantization();
        }
    });

    $("#ctxSelect").addEventListener("input", () => {
        const arr = CAP.context_lengths ?? [];
        const v = arr[Number($("#ctxSelect").value)] ?? 0;
        $("#ctxHuman").textContent = `${v.toLocaleString()} tokens`;
        $("#ctxPill").textContent = v ? `${Math.round(v / 1024)}k` : "—";
    });

    $("#ctxSelect").addEventListener("change", () => {
        const arr = CAP.context_lengths ?? [];
        state.context_length = arr[Number($("#ctxSelect").value)] ?? state.context_length;
    });

    $("#exportBtn").addEventListener("click", async () => {
        const payload = {
            device: state.device,
            attention_method: state.attention_method,
            context_length: state.context_length,
            quantization_method: {
                backend: state.quantization_method?.backend ?? null,
                precision: state.quantization_method?.precision ?? "bfloat16",
            },
        };

        try {
            const r = await fetch("/settings/save", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload, null, 2),
            });
            const data = await r.json().catch(() => ({}));
            if (!r.ok) {
                $("#exportBtn").textContent = "Save failed: " + JSON.stringify(data.detail || r.statusText);
                return;
            }
            $("#exportBtn").textContent = "Saved";
        } catch (e) {
            $("#exportBtn").textContent = "Save failed: " + e.message;
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    bind();
    renderAll();
});
