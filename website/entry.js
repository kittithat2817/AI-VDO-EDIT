const guideSections = new Set([
  'main', 'commands', 'start', 'choose', 'brief', 'media', 'plan',
  'style', 'edit', 'qc', 'revise', 'reuse', 'trouble', 'files', 'promotion'
]);
const section = window.location.hash.slice(1);
if (guideSections.has(section)) {
  window.location.replace(`experiment.html#${section}`);
}
