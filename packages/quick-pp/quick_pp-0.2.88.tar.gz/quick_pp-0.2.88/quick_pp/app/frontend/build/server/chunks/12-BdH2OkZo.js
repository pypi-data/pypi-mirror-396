const load = ({ params }) => {
  const projectId = params.project_id ?? null;
  return {
    title: "Well Analysis",
    subtitle: projectId ? `ID: ${projectId}` : void 0
  };
};

var _page_ts = /*#__PURE__*/Object.freeze({
  __proto__: null,
  load: load
});

const index = 12;
let component_cache;
const component = async () => component_cache ??= (await import('./_page.svelte-BzStxyNV.js')).default;
const universal_id = "src/routes/wells/[project_id]/+page.ts";
const imports = ["_app/immutable/nodes/12.DcHpL93N.js","_app/immutable/chunks/B2f41zB7.js","_app/immutable/chunks/BNO5OzLn.js","_app/immutable/chunks/BJMC0GYJ.js","_app/immutable/chunks/P4kRMzeK.js","_app/immutable/chunks/PPVm8Dsz.js","_app/immutable/chunks/BhLg-KJu.js"];
const stylesheets = ["_app/immutable/assets/vendor.S5W4ZllZ.css","_app/immutable/assets/DepthFilterStatus.CMzVkwfb.css"];
const fonts = [];

export { component, fonts, imports, index, stylesheets, _page_ts as universal, universal_id };
//# sourceMappingURL=12-BdH2OkZo.js.map
