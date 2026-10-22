// Interactive demo: Monte Carlo vs. M-DRM vs. FOSM for a textbook cantilever.
// Teaching example only — not the thesis model, data, or results.
(function () {
  var host = document.getElementById('uq-demo');
  if (!host) return;

  var L = 3; // m
  var MEAN = { P: 20e3, w: 5e3, E: 200e9, I: 8e-5 }; // N, N/m, Pa, m^4
  var VARS = ['P', 'w', 'E', 'I'];
  var cov = { P: 0.10, w: 0.10, E: 0.05, I: 0.05 };

  // 5-point Gauss–Hermite rule for a standard normal variable
  var GH_Z = [-2.856970, -1.355626, 0, 1.355626, 2.856970];
  var GH_W = [0.011257, 0.222076, 0.533333, 0.222076, 0.011257];

  function model(x) { // tip deflection in mm
    return 1000 * (x.P * Math.pow(L, 3) / (3 * x.E * x.I) + x.w * Math.pow(L, 4) / (8 * x.E * x.I));
  }
  function sd(v) { return MEAN[v] * cov[v]; }
  function withVar(v, val) { var x = Object.assign({}, MEAN); x[v] = val; return x; }

  function mdrm() {
    var g0 = model(MEAN), n = VARS.length, p1 = 1, p2 = 1;
    VARS.forEach(function (v) {
      var m1 = 0, m2 = 0;
      GH_Z.forEach(function (z, j) {
        var gi = model(withVar(v, MEAN[v] + sd(v) * z));
        m1 += GH_W[j] * gi; m2 += GH_W[j] * gi * gi;
      });
      p1 *= m1; p2 *= m2;
    });
    var M1 = Math.pow(g0, 1 - n) * p1, M2 = Math.pow(g0, 2 * (1 - n)) * p2;
    return { runs: VARS.length * (GH_Z.length - 1) + 1, mean: M1, std: Math.sqrt(Math.max(M2 - M1 * M1, 0)) };
  }

  function fosm() {
    var g0 = model(MEAN), v2 = 0;
    VARS.forEach(function (v) {
      var h = 0.01 * sd(v);
      var d = (model(withVar(v, MEAN[v] + h)) - model(withVar(v, MEAN[v] - h))) / (2 * h);
      v2 += Math.pow(d * sd(v), 2);
    });
    return { runs: 2 * VARS.length + 1, mean: g0, std: Math.sqrt(v2) };
  }

  function randn() { var u = 0, v = 0; while (u === 0) u = Math.random(); v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  function sampleOnce() {
    var x = {};
    VARS.forEach(function (v) { var s; do { s = MEAN[v] + sd(v) * randn(); } while (s <= 0); x[v] = s; });
    return model(x);
  }

  function lognormal(m, s) {
    var s2 = Math.log(1 + (s * s) / (m * m)), mu = Math.log(m) - s2 / 2;
    return {
      pdf: function (x) { return x <= 0 ? 0 : Math.exp(-Math.pow(Math.log(x) - mu, 2) / (2 * s2)) / (x * Math.sqrt(2 * Math.PI * s2)); },
      q: function (z) { return Math.exp(mu + z * Math.sqrt(s2)); }
    };
  }

  // ---------------------------------------------------------------- state
  var state = { samples: [], running: [], md: null, fo: null, range: null, bins: 36, timer: null };

  function recomputeAnalytic() {
    state.md = mdrm(); state.fo = fosm();
    var ln = lognormal(state.md.mean, state.md.std);
    state.range = [ln.q(-4), ln.q(4)];
  }

  // ---------------------------------------------------------------- chart helpers
  function niceTicks(lo, hi, count) {
    var span = hi - lo, step = Math.pow(10, Math.floor(Math.log10(span / count)));
    var err = (count * step) / span;
    if (err <= 0.15) step *= 10; else if (err <= 0.35) step *= 5; else if (err <= 0.75) step *= 2;
    var out = [], t = Math.ceil(lo / step) * step;
    for (; t <= hi + 1e-9; t += step) out.push(+t.toFixed(10));
    return out;
  }
  function fmt(x, d) { return x.toLocaleString(undefined, { minimumFractionDigits: d, maximumFractionDigits: d }); }
  var PAD = { l: 44, r: 16, t: 10, b: 30 };

  function frame(el) {
    var w = el.clientWidth || 600, h = el.clientHeight || 260;
    return { w: w, h: h, iw: w - PAD.l - PAD.r, ih: h - PAD.t - PAD.b };
  }

  function axes(f, xs, ys, xTicks, yTicks, xd, yd) {
    var s = '';
    yTicks.forEach(function (t) {
      var y = ys(t);
      s += '<line class="gridline" x1="' + PAD.l + '" x2="' + (f.w - PAD.r) + '" y1="' + y + '" y2="' + y + '"/>';
      s += '<text x="' + (PAD.l - 8) + '" y="' + (y + 4) + '" text-anchor="end">' + fmt(t, yd) + '</text>';
    });
    xTicks.forEach(function (t) {
      s += '<text x="' + xs(t) + '" y="' + (f.h - 10) + '" text-anchor="middle">' + fmt(t, xd) + '</text>';
    });
    s += '<line class="axis" x1="' + PAD.l + '" x2="' + (f.w - PAD.r) + '" y1="' + (f.h - PAD.b) + '" y2="' + (f.h - PAD.b) + '"/>';
    return s;
  }

  // ---------------------------------------------------------------- histogram
  var histEl = document.getElementById('uq-hist'), tip = document.getElementById('uq-tip');
  var histBins = [];

  function drawHist() {
    var f = frame(histEl), lo = state.range[0], hi = state.range[1], nb = state.bins, bw = (hi - lo) / nb;
    var counts = new Array(nb).fill(0), n = state.samples.length;
    state.samples.forEach(function (v) { var k = Math.floor((v - lo) / bw); if (k >= 0 && k < nb) counts[k]++; });
    var dens = counts.map(function (c) { return n ? c / (n * bw) : 0; });
    var ln = lognormal(state.md.mean, state.md.std), curve = [], peak = 0;
    for (var i = 0; i <= 160; i++) { var x = lo + (hi - lo) * i / 160, y = ln.pdf(x); curve.push([x, y]); peak = Math.max(peak, y); }
    var ymax = Math.max(peak, Math.max.apply(null, dens)) * 1.12;
    var xs = function (x) { return PAD.l + (x - lo) / (hi - lo) * f.iw; };
    var ys = function (y) { return PAD.t + f.ih - y / ymax * f.ih; };
    var yt = niceTicks(0, ymax, 4), yd = ymax < 0.1 ? 3 : 2;
    var s = '<svg viewBox="0 0 ' + f.w + ' ' + f.h + '" preserveAspectRatio="none">' + axes(f, xs, ys, niceTicks(lo, hi, 7), yt, 0, yd);
    histBins = [];
    dens.forEach(function (d, k) {
      if (!d) return;
      var x0 = xs(lo + k * bw), x1 = xs(lo + (k + 1) * bw), y = ys(d), base = ys(0);
      var hgt = Math.max(base - y, 0), r = Math.min(4, hgt, (x1 - x0) / 2);
      // rounded top, square base
      s += '<path class="bar" data-k="' + k + '" d="M' + x0 + ',' + base + 'V' + (y + r) + 'Q' + x0 + ',' + y + ' ' + (x0 + r) + ',' + y +
           'H' + (x1 - r) + 'Q' + x1 + ',' + y + ' ' + x1 + ',' + (y + r) + 'V' + base + 'Z"/>';
      histBins[k] = { lo: lo + k * bw, hi: lo + (k + 1) * bw, c: counts[k], x: (x0 + x1) / 2, y: y };
    });
    s += '<path class="curve" d="M' + curve.map(function (p) { return xs(p[0]).toFixed(1) + ',' + ys(p[1]).toFixed(1); }).join('L') + '"/>';
    s += '</svg>';
    histEl.innerHTML = s;
  }

  histEl.addEventListener('mousemove', function (e) {
    var t = e.target.closest ? e.target.closest('.bar') : null;
    histEl.querySelectorAll('.bar.active').forEach(function (b) { b.classList.remove('active'); });
    if (!t) { tip.hidden = true; return; }
    t.classList.add('active');
    var b = histBins[+t.dataset.k], box = histEl.getBoundingClientRect(), fig = histEl.parentNode.getBoundingClientRect();
    tip.textContent = fmt(b.lo, 2) + '–' + fmt(b.hi, 2) + ' mm · ' + b.c.toLocaleString() + ' samples';
    tip.style.left = (b.x * box.width / histEl.clientWidth + box.left - fig.left) + 'px';
    tip.style.top = (b.y + box.top - fig.top) + 'px';
    tip.hidden = false;
  });
  histEl.addEventListener('mouseleave', function () { tip.hidden = true; });

  // ---------------------------------------------------------------- convergence
  var convEl = document.getElementById('uq-conv');
  var convPts = [];

  function drawConv() {
    var f = frame(convEl), N = +document.getElementById('uq-n').value, ref = state.md.mean;
    var pts = state.running, step = Math.max(1, Math.floor(pts.length / 300));
    convPts = [];
    for (var i = Math.min(9, pts.length - 1); i < pts.length; i += step) convPts.push([i + 1, pts[i]]);
    if (pts.length) convPts.push([pts.length, pts[pts.length - 1]]);
    var vals = convPts.map(function (p) { return p[1]; }).concat([ref]);
    var spread = Math.max(state.md.std * 0.25, Math.max.apply(null, vals.map(function (v) { return Math.abs(v - ref); })));
    var lo = ref - spread * 1.15, hi = ref + spread * 1.15;
    var xs = function (x) { return PAD.l + (x - 1) / Math.max(N - 1, 1) * f.iw; };
    var ys = function (y) { return PAD.t + f.ih - (y - lo) / (hi - lo) * f.ih; };
    var s = '<svg viewBox="0 0 ' + f.w + ' ' + f.h + '" preserveAspectRatio="none">' + axes(f, xs, ys, niceTicks(1, N, 5), niceTicks(lo, hi, 4), 0, 2);
    s += '<line class="ref" x1="' + PAD.l + '" x2="' + (f.w - PAD.r) + '" y1="' + ys(ref) + '" y2="' + ys(ref) + '"/>';
    s += '<text class="label-line" x="' + (f.w - PAD.r) + '" y="' + (ys(ref) - 6) + '" text-anchor="end">M-DRM ' + fmt(ref, 2) + ' mm</text>';
    if (convPts.length > 1) s += '<path class="run" d="M' + convPts.map(function (p) { return xs(p[0]).toFixed(1) + ',' + ys(p[1]).toFixed(1); }).join('L') + '"/>';
    s += '<g class="hover" style="display:none"><line class="crosshair" y1="' + PAD.t + '" y2="' + (f.h - PAD.b) + '"/><circle class="dot" r="4"/></g></svg>';
    convEl.innerHTML = s;
    convEl._scale = { xs: xs, ys: ys, f: f, N: N };
  }

  convEl.addEventListener('mousemove', function (e) {
    var sc = convEl._scale, g = convEl.querySelector('.hover');
    if (!sc || convPts.length < 2 || !g) return;
    var box = convEl.getBoundingClientRect(), px = (e.clientX - box.left) * sc.f.w / box.width;
    var n = Math.round((px - PAD.l) / sc.f.iw * (sc.N - 1) + 1), best = convPts[0];
    convPts.forEach(function (p) { if (Math.abs(p[0] - n) < Math.abs(best[0] - n)) best = p; });
    var x = sc.xs(best[0]), y = sc.ys(best[1]);
    g.style.display = '';
    g.querySelector('line').setAttribute('x1', x); g.querySelector('line').setAttribute('x2', x);
    g.querySelector('circle').setAttribute('cx', x); g.querySelector('circle').setAttribute('cy', y);
    var fig = convEl.parentNode.getBoundingClientRect();
    tip.textContent = best[0].toLocaleString() + ' runs · mean ' + fmt(best[1], 3) + ' mm';
    // reuse the shared tooltip, positioned relative to the histogram figure's container
    var hostBox = tip.parentNode.getBoundingClientRect();
    tip.style.left = (x * box.width / sc.f.w + box.left - hostBox.left) + 'px';
    tip.style.top = (y * box.height / sc.f.h + box.top - hostBox.top) + 'px';
    tip.hidden = false;
  });
  convEl.addEventListener('mouseleave', function () { tip.hidden = true; var g = convEl.querySelector('.hover'); if (g) g.style.display = 'none'; });

  // ---------------------------------------------------------------- table
  function drawTable() {
    var n = state.samples.length, mean = 0, v = 0;
    state.samples.forEach(function (x) { mean += x; }); mean /= n || 1;
    state.samples.forEach(function (x) { v += (x - mean) * (x - mean); }); v /= Math.max(n - 1, 1);
    var rows = [
      ['Monte Carlo (reference)', n ? n.toLocaleString() : '—', n ? fmt(mean, 3) : '—', n ? fmt(Math.sqrt(v), 3) : '—'],
      ['M-DRM', state.md.runs, fmt(state.md.mean, 3), fmt(state.md.std, 3)],
      ['FOSM', state.fo.runs, fmt(state.fo.mean, 3), fmt(state.fo.std, 3)]
    ];
    document.querySelector('#uq-table tbody').innerHTML = rows.map(function (r) {
      return '<tr><th scope="row">' + r[0] + '</th><td>' + r[1] + '</td><td>' + r[2] + '</td><td>' + r[3] + '</td></tr>';
    }).join('');
  }

  function drawAll() { drawHist(); drawConv(); drawTable(); }

  // ---------------------------------------------------------------- run
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function run() {
    clearInterval(state.timer);
    state.samples = []; state.running = [];
    var N = +document.getElementById('uq-n').value, sum = 0, batch = reduced ? N : Math.ceil(N / 45);
    function step() {
      var end = Math.min(state.samples.length + batch, N);
      while (state.samples.length < end) { var y = sampleOnce(); state.samples.push(y); sum += y; state.running.push(sum / state.samples.length); }
      drawAll();
      if (state.samples.length >= N) clearInterval(state.timer);
    }
    step();
    if (state.samples.length < N) state.timer = setInterval(step, 30);
  }

  host.querySelectorAll('input[type=range]').forEach(function (inp) {
    inp.addEventListener('input', function () {
      cov[inp.dataset.var] = inp.value / 100;
      host.querySelector('output[data-for="' + inp.dataset.var + '"]').textContent = inp.value + '%';
      clearInterval(state.timer);
      state.samples = []; state.running = [];
      recomputeAnalytic(); drawAll();
    });
  });
  document.getElementById('uq-run').addEventListener('click', run);
  document.getElementById('uq-n').addEventListener('change', run);
  var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(drawAll, 120); });

  recomputeAnalytic();
  run();
})();
