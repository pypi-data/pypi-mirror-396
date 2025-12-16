import { defineComponent as l, inject as _, reactive as g, onMounted as f, onUnmounted as v, computed as u, createElementBlock as S, openBlock as h, createElementVNode as c, toDisplayString as d } from "vue";
const w = { class: "system-widget" }, y = { id: "info_time" }, b = { id: "uptime" }, T = /* @__PURE__ */ l({
  __name: "SystemWidget",
  setup(s) {
    const o = _("tangramApi");
    if (!o)
      throw new Error("assert: tangram api not provided");
    const e = g({
      hovered: !1,
      uptime: "",
      info_utc: (/* @__PURE__ */ new Date()).getTime()
    });
    let i = null;
    f(async () => {
      try {
        i = await o.realtime.subscribe(
          "system:update-node",
          (t) => {
            t.el === "uptime" && (e.uptime = t.value), t.el === "info_utc" && (e.info_utc = t.value);
          }
        );
      } catch (t) {
        console.error("failed to subscribe to system:update-node", t);
      }
    }), v(() => {
      i?.dispose();
    });
    const r = u(() => {
      const t = new Date(e.info_utc), n = t.getUTCHours().toString().padStart(2, "0"), a = t.getUTCMinutes().toString().padStart(2, "0"), p = t.getUTCSeconds().toString().padStart(2, "0");
      return `${n}:${a}:${p} Z`;
    }), m = u(() => new Date(e.info_utc).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: !1,
      timeZoneName: "shortOffset"
    }));
    return (t, n) => (h(), S("div", w, [
      c("div", {
        class: "clock",
        onMouseover: n[0] || (n[0] = (a) => e.hovered = !0),
        onMouseleave: n[1] || (n[1] = (a) => e.hovered = !1)
      }, [
        c("span", y, d(e.hovered ? m.value : r.value), 1)
      ], 32),
      c("span", b, d(e.uptime), 1)
    ]));
  }
}), $ = (s, o) => {
  const e = s.__vccOpts || s;
  for (const [i, r] of o)
    e[i] = r;
  return e;
}, k = /* @__PURE__ */ $(T, [["__scopeId", "data-v-6e31ee8b"]]);
function D(s, o) {
  s.ui.registerWidget("system-widget", "TopBar", k, {
    priority: o?.topbar_order
  });
}
export {
  D as install
};
//# sourceMappingURL=index.js.map
