(function () {
  var data = window.PLOTLY_DATA;
  if (!data || typeof Plotly === 'undefined') return;

  var config = { displayModeBar: false, responsive: true };

  function render(key) {
    var block = data[key];
    if (!block) return;
    var primary = document.getElementById('chart-' + key + '-primary');
    var secondary = document.getElementById('chart-' + key + '-secondary');
    if (primary && !primary.dataset.rendered) {
      Plotly.newPlot(primary, block.primary.data, block.primary.layout, config);
      primary.dataset.rendered = '1';
    }
    if (secondary && !secondary.dataset.rendered) {
      Plotly.newPlot(secondary, block.secondary.data, block.secondary.layout, config);
      secondary.dataset.rendered = '1';
    }
  }

  function setActive(key) {
    document.querySelectorAll('[data-signal-panel]').forEach(function (el) {
      var visible = el.dataset.signalPanel === key;
      el.classList.toggle('hidden', !visible);
    });
    document.querySelectorAll('[data-signal-tab]').forEach(function (el) {
      var active = el.dataset.signalTab === key;
      el.classList.toggle('signal-tab-active', active);
    });
    render(key);
    var block = data[key];
    if (block) {
      var p = document.getElementById('chart-' + key + '-primary');
      var s = document.getElementById('chart-' + key + '-secondary');
      if (p) Plotly.Plots.resize(p);
      if (s) Plotly.Plots.resize(s);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-signal-tab]').forEach(function (el) {
      el.addEventListener('click', function () { setActive(el.dataset.signalTab); });
    });
    var initial = document.querySelector('[data-signal-tab]');
    if (initial) setActive(initial.dataset.signalTab);
  });
})();

(function () {
  var el = document.getElementById('signal-teaser');
  if (!el || typeof Plotly === 'undefined' || !window.PLOTLY_TEASER) return;
  Plotly.newPlot(el, window.PLOTLY_TEASER.data, window.PLOTLY_TEASER.layout, { displayModeBar: false, responsive: true });
})();
