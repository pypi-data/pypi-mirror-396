const load = async ({ params }) => {
  const projectId = params.project_id ?? null;
  const wellId = params.well_id ? decodeURIComponent(params.well_id) : null;
  return { projectId, wellId };
};

var _layout_ts = /*#__PURE__*/Object.freeze({
  __proto__: null,
  load: load
});

const index = 3;
let component_cache;
const component = async () => component_cache ??= (await import('./_layout.svelte--zKlFQdX.js')).default;
const universal_id = "src/routes/wells/+layout.ts";
const imports = ["_app/immutable/nodes/3.oWGl5g_W.js","_app/immutable/chunks/B2f41zB7.js","_app/immutable/chunks/BNO5OzLn.js","_app/immutable/chunks/BJMC0GYJ.js","_app/immutable/chunks/CVeJoFBp.js","_app/immutable/chunks/BjKtTXPK.js","_app/immutable/chunks/BhLg-KJu.js"];
const stylesheets = ["_app/immutable/assets/vendor.S5W4ZllZ.css"];
const fonts = [];

export { component, fonts, imports, index, stylesheets, _layout_ts as universal, universal_id };
//# sourceMappingURL=3-Dzk2cSVN.js.map
