import { defineComponent as _, inject as g, ref as u, createElementBlock as s, openBlock as i, withDirectives as f, createCommentVNode as h, createElementVNode as k, vModelText as y, Fragment as w, renderList as A, toDisplayString as p } from "vue";
import { airport_information as x } from "rs1090-wasm";
const C = { class: "airport-search" }, I = {
  key: 0,
  class: "search-results"
}, S = ["onClick"], T = /* @__PURE__ */ _({
  __name: "AirportSearchWidget",
  setup(r) {
    const a = g("tangramApi");
    if (!a)
      throw new Error("assert: tangram api not provided");
    const t = u(""), o = u([]), n = u(null), d = () => {
      n.value && clearTimeout(n.value), t.value.length >= 3 ? n.value = window.setTimeout(() => {
        m();
      }, 300) : o.value = [];
    }, m = () => {
      o.value = x(t.value);
    }, v = (c) => {
      a.map.getMapInstance().flyTo({
        center: [c.lon, c.lat],
        zoom: 13,
        speed: 1.2
      }), t.value = "", o.value = [];
    };
    return (c, l) => (i(), s("div", C, [
      f(k("input", {
        "onUpdate:modelValue": l[0] || (l[0] = (e) => t.value = e),
        type: "text",
        placeholder: "Search for airports...",
        onClick: l[1] || (l[1] = (e) => e.target.select()),
        onInput: d
      }, null, 544), [
        [y, t.value]
      ]),
      o.value.length ? (i(), s("ul", I, [
        (i(!0), s(w, null, A(o.value, (e) => (i(), s("li", {
          key: e.icao,
          onClick: (V) => v(e)
        }, p(e.name) + " (" + p(e.iata) + " | " + p(e.icao) + ") ", 9, S))), 128))
      ])) : h("", !0)
    ]));
  }
}), E = (r, a) => {
  const t = r.__vccOpts || r;
  for (const [o, n] of a)
    t[o] = n;
  return t;
}, M = /* @__PURE__ */ E(T, [["__scopeId", "data-v-ddbda8e0"]]);
function D(r) {
  r.ui.registerWidget("airport-search-widget", "MapOverlay", M);
}
export {
  D as install
};
//# sourceMappingURL=index.js.map
