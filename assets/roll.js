/* Roll the DICE: five ingredients, one banned crutch, optional technique.
   Data: pantry.json (exposed as window.PANTRY by build.py). */
(function (root) {
  "use strict";

  var ELEMENTS = [
    { key: "salty", label: "Salt", group: "Taste" },
    { key: "sour", label: "Sour", group: "Taste" },
    { key: "sweet", label: "Sweet", group: "Taste" },
    { key: "bitter", label: "Bitter", group: "Taste" },
    { key: "umami", label: "Umami", group: "Taste" },
    { key: "heat", label: "Heat", group: "Physical" },
    { key: "rich", label: "Rich", group: "Texture" },
    { key: "crunch", label: "Crunch", group: "Texture" },
    { key: "fresh", label: "Fresh", group: "Aroma" },
    { key: "smoke", label: "Smoke", group: "Aroma" }
  ];
  var WORTH_FLAGGING = ["sour", "heat", "rich", "umami", "crunch", "fresh"];
  var ROLE_LABEL = {
    protein: "Main", base: "Base", veg: "Vegetable", creamy: "Creamy", acid: "Acid",
    heat: "Heat", umami: "Savory", crunch: "Crunch", fresh: "Fresh", spice: "Spice", sweet: "Sweet",
    boost: "Extra protein"
  };
  var LANE_LABEL = {
    mex: "Mexican", ind: "Indian", ita: "Italian", eas: "East Asian",
    ame: "American", med: "Mediterranean"
  };
  var ACCENT_WEIGHT = {
    creamy: 3, acid: 3, heat: 3, umami: 2, crunch: 2, fresh: 2, spice: 1.5, veg: 1.5, boost: 1.5, sweet: 1
  };
  var STOCK_FACTOR = [0, 0.45, 1, 1.4];

  function pickWeighted(items, weightOf, rng) {
    var total = 0, i;
    var weights = items.map(function (it) { var w = Math.max(0, weightOf(it)); total += w; return w; });
    if (!items.length || total <= 0) return null;
    var r = rng() * total;
    for (i = 0; i < items.length; i++) { r -= weights[i]; if (r <= 0) return items[i]; }
    return items[items.length - 1];
  }

  function ingredientWeight(ing, pantry, opts) {
    if (opts.houseOnly && ing.stock < 2) return 0;
    var score = 0, k;
    for (k in ing.brings) score += ing.brings[k] * (pantry.palate[k] || 0);
    var w = (1 + score / 10) * STOCK_FACTOR[ing.stock];
    return w;
  }

  function sharesLane(a, b) {
    return a.lanes.some(function (l) { return b.lanes.indexOf(l) !== -1; });
  }

  function commonLanes(set) {
    return set[0].lanes.filter(function (l) {
      return set.every(function (s) { return s.lanes.indexOf(l) !== -1; });
    });
  }

  function isConnected(set) {
    var seen = [0], queue = [0], i, cur;
    while (queue.length) {
      cur = queue.shift();
      for (i = 0; i < set.length; i++) {
        if (seen.indexOf(i) === -1 && sharesLane(set[cur], set[i])) { seen.push(i); queue.push(i); }
      }
    }
    return seen.length === set.length;
  }

  function anyPair(set) {
    var i, j;
    for (i = 0; i < set.length; i++) for (j = i + 1; j < set.length; j++) if (sharesLane(set[i], set[j])) return true;
    return false;
  }

  /* True when 4+ of the rolled ingredients already sit together in one recipe on the site. */
  function matchesExistingRecipe(set, recipes) {
    return recipes.some(function (r) {
      var text = (r.ingredients || []).join(" ").toLowerCase();
      var hits = set.filter(function (s) { return text.indexOf(s.key) !== -1; }).length;
      return hits >= 4;
    });
  }

  function fitsRisk(set, risk) {
    var common = commonLanes(set).length > 0;
    if (risk === "safe") return common;
    if (risk === "wild") return !common && anyPair(set) && !isConnected(set);
    return !common && isConnected(set);
  }

  /* held: array of 5, each null or an ingredient to keep in that slot. */
  function rollIngredients(pantry, recipes, opts, held, rng) {
    held = held || [null, null, null, null, null];
    var pool = pantry.ingredients;
    var best = null, attempt, set, usedRoles, usedNames, slot, role, choices, pick;

    function choose(roleList) {
      choices = pool.filter(function (p) {
        return roleList.indexOf(p.role) !== -1 && usedNames.indexOf(p.name) === -1;
      });
      return pickWeighted(choices, function (p) { return ingredientWeight(p, pantry, opts); }, rng);
    }

    for (attempt = 0; attempt < 800; attempt++) {
      set = held.slice();
      usedNames = set.filter(Boolean).map(function (s) { return s.name; });
      usedRoles = set.slice(1).filter(Boolean).map(function (s) { return s.role; });

      if (!set[0]) { set[0] = choose(["protein"]); if (set[0]) usedNames.push(set[0].name); }
      if (!set[1]) {
        set[1] = choose([usedRoles.indexOf("veg") === -1 && rng() < 0.4 ? "veg" : "base"]);
        if (set[1]) { usedNames.push(set[1].name); usedRoles.push(set[1].role); }
      }
      for (slot = 2; slot < 5; slot++) {
        if (set[slot]) continue;
        role = pickWeighted(Object.keys(ACCENT_WEIGHT).filter(function (r) {
          return usedRoles.indexOf(r) === -1;
        }), function (r) { return ACCENT_WEIGHT[r]; }, rng);
        pick = role ? choose([role]) : null;
        if (!pick) { set = null; break; }
        set[slot] = pick; usedNames.push(pick.name); usedRoles.push(role);
      }
      if (!set || set.some(function (s) { return !s; })) continue;
      if (!best) best = set;
      if (!fitsRisk(set, opts.risk)) continue;
      if (opts.risk !== "safe" && matchesExistingRecipe(set, recipes)) continue;
      return { dice: set, relaxed: false };
    }
    return best ? { dice: best, relaxed: true } : null;
  }

  /* avoid: ban texts rolled recently, so the same few don't come up back to back. */
  function rollBan(pantry, dice, rng, avoid) {
    var keys = dice.map(function (d) { return d.key; });
    var ok = pantry.bans.filter(function (b) {
      return !b.blocks.some(function (blk) { return keys.indexOf(blk) !== -1; });
    });
    var fresh = ok.filter(function (b) { return (avoid || []).indexOf(b.text) === -1; });
    var from = fresh.length ? fresh : (ok.length ? ok : pantry.bans);
    return pickWeighted(from, function () { return 1; }, rng).text;
  }

  function rollTechnique(pantry, rng, avoid) {
    var fresh = pantry.techniques.filter(function (t) { return (avoid || []).indexOf(t) === -1; });
    return pickWeighted(fresh.length ? fresh : pantry.techniques, function () { return 1; }, rng);
  }

  function profile(dice) {
    var totals = {}, lanes = {};
    ELEMENTS.forEach(function (e) { totals[e.key] = 0; });
    dice.forEach(function (d) {
      for (var k in d.brings) totals[k] += d.brings[k];
      d.lanes.forEach(function (l) { lanes[l] = (lanes[l] || 0) + 1; });
    });
    var missing = WORTH_FLAGGING.filter(function (k) { return totals[k] === 0; });
    var laneList = Object.keys(lanes).filter(function (l) { return lanes[l] >= 2; })
      .sort(function (a, b) { return lanes[b] - lanes[a]; });
    return { totals: totals, missing: missing, lanes: laneList };
  }

  var core = {
    ELEMENTS: ELEMENTS, ROLE_LABEL: ROLE_LABEL, LANE_LABEL: LANE_LABEL,
    rollIngredients: rollIngredients, rollBan: rollBan, rollTechnique: rollTechnique,
    profile: profile, fitsRisk: fitsRisk, commonLanes: commonLanes, isConnected: isConnected,
    matchesExistingRecipe: matchesExistingRecipe
  };
  root.DICE_ROLL = core;
  if (typeof document === "undefined") return;

  /* ------------------------------------------------------------------ page */
  var pantry = root.PANTRY, recipes = root.PERSONAL_RECIPES || [];
  var STORE_KEY = "dice-rolls-v1";
  var state = {
    risk: "stretch", houseOnly: false, technique: true,
    dice: [null, null, null, null, null], held: [false, false, false, false, false],
    ban: null, banHeld: false, tech: null, techHeld: false, relaxed: false, verdict: "",
    recentBans: [], recentTechs: [], rolling: false
  };
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };

  function loadLog() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY) || "[]"); } catch (e) { return []; }
  }
  function saveLog(list) {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(list)); return true; } catch (e) { return false; }
  }

  function remember(list, value) {
    list.push(value);
    while (list.length > 4) list.shift();
  }

  function roll() {
    if (state.rolling) return;
    var held = state.dice.map(function (d, i) { return state.held[i] ? d : null; });
    var result = rollIngredients(pantry, recipes, state, held, Math.random);
    if (!result) return;
    state.dice = result.dice;
    state.relaxed = result.relaxed;
    var newBan = !state.banHeld || !state.ban, newTech = !state.techHeld || !state.tech;
    if (newBan) { state.ban = rollBan(pantry, state.dice, Math.random, state.recentBans); remember(state.recentBans, state.ban); }
    if (newTech) { state.tech = rollTechnique(pantry, Math.random, state.recentTechs); remember(state.recentTechs, state.tech); }
    render();
    tumble(held, newBan, newTech);
  }

  /* Tumble every die that changed: names flicker past, then each die lands in turn.
     With reduced motion on, the names still cycle but the dice stay put. */
  function tumble(held, newBan, newTech) {
    var reduce = root.matchMedia && root.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var spin = reduce ? "rolling-still" : "rolling";
    var jobs = [];
    Array.prototype.forEach.call(document.querySelectorAll("#diceGrid .die"), function (el, i) {
      if (held[i]) return;
      var role = state.dice[i].role;
      jobs.push({ el: el, names: pantry.ingredients.filter(function (p) { return p.role === role; })
        .map(function (p) { return p.name; }) });
    });
    Array.prototype.forEach.call(document.querySelectorAll("#ruleGrid .die"), function (el) {
      var kind = el.getAttribute("data-kind");
      if (kind === "ban" && newBan) jobs.push({ el: el, names: pantry.bans.map(function (b) { return b.text; }) });
      if (kind === "tech" && newTech) jobs.push({ el: el, names: pantry.techniques });
    });
    if (!jobs.length) return;
    state.rolling = true;
    $("rollBtn").disabled = true;
    $("rollArea").classList.add("is-rolling");
    jobs.forEach(function (job, n) {
      var nameEl = job.el.querySelector(".die-name"), finalName = nameEl.textContent;
      job.el.classList.add(spin);
      job.el.style.animationDelay = (n * 40) + "ms";
      var timer = setInterval(function () {
        nameEl.textContent = job.names[Math.floor(Math.random() * job.names.length)];
      }, reduce ? 150 : 80);
      setTimeout(function () {
        clearInterval(timer);
        nameEl.textContent = finalName;
        job.el.classList.remove(spin);
        if (!reduce) {
          job.el.classList.add("landed");
          setTimeout(function () { job.el.classList.remove("landed"); }, 320);
        }
        if (n === jobs.length - 1) {
          state.rolling = false;
          $("rollBtn").disabled = false;
          $("rollArea").classList.remove("is-rolling");
        }
      }, 650 + n * 190);
    });
  }

  function dieButton(kind, index, label, name, held) {
    return '<button type="button" class="die' + (held ? " held" : "") + '" aria-pressed="' + held +
      '" data-kind="' + kind + '" data-index="' + index + '">' +
      '<span class="die-role">' + esc(label) + '</span>' +
      '<span class="die-name">' + esc(name) + '</span>' +
      '<span class="die-hold">' + (held ? "Held" : "Tap to hold") + '</span></button>';
  }

  function render() {
    var html = state.dice.map(function (d, i) {
      return dieButton("ing", i, ROLE_LABEL[d.role], d.name, state.held[i]);
    }).join("");
    $("diceGrid").innerHTML = html;

    var rules = dieButton("ban", 0, "Banned", state.ban, state.banHeld);
    if (state.technique) rules += dieButton("tech", 0, "Technique", state.tech, state.techHeld);
    $("ruleGrid").innerHTML = rules;

    var p = profile(state.dice);
    var group = "", bars = "";
    ELEMENTS.forEach(function (e) {
      if (e.group !== group) {
        if (group) bars += "</div>";
        group = e.group;
        bars += '<div class="bar-group"><p class="eyebrow">' + group + "</p>";
      }
      var n = Math.min(p.totals[e.key], 6);
      bars += '<div class="bar-row"><span class="bar-label">' + e.label + '</span>' +
        '<span class="bar-track" role="img" aria-label="' + e.label + " " + n + ' of 6">' +
        '<span class="bar-fill" style="width:' + Math.round(n / 6 * 100) + '%"></span></span></div>';
    });
    $("bars").innerHTML = bars + "</div>";

    var labelOf = function (k) {
      return ELEMENTS.filter(function (e) { return e.key === k; })[0].label.toLowerCase();
    };
    var notes = [];
    if (p.missing.length) {
      notes.push("Nothing in this roll brings " + p.missing.map(labelOf).join(" or ") +
        ". That part is yours to solve.");
    } else {
      notes.push("Every base is covered. The job is balance.");
    }
    if (p.totals.sweet >= 3) notes.push("There's real sweetness here. Keep it in check with acid or heat.");
    notes.push(p.lanes.length
      ? "Leans " + p.lanes.slice(0, 3).map(function (l) { return LANE_LABEL[l]; }).join(", ") + "."
      : "No two ingredients share a food lane.");
    if (state.relaxed) notes.push("Couldn't fit the risk setting with what's held, so this is the closest roll.");
    $("readNote").innerHTML = notes.map(function (n) { return "<p>" + esc(n) + "</p>"; }).join("");
    $("rollArea").hidden = false;
  }

  function rollText(entry) {
    var lines = [];
    lines.push("DICE roll" + (entry.date ? ", " + entry.date : ""));
    lines.push("Ingredients: " + entry.dice.join("; "));
    lines.push("Banned: " + entry.ban);
    if (entry.tech) lines.push("Technique: " + entry.tech);
    if (entry.name) lines.push("What I made: " + entry.name);
    if (entry.verdict) lines.push("Verdict: " + entry.verdict);
    if (entry.notes) lines.push("Notes: " + entry.notes);
    return lines.join("\n");
  }

  function renderLog() {
    var list = loadLog();
    $("logEmpty").hidden = list.length > 0;
    $("logList").innerHTML = list.map(function (e, i) {
      return '<li class="log-item sheet"><p class="eyebrow">' + esc(e.date) +
        (e.verdict ? " · " + esc(e.verdict) : "") + "</p>" +
        "<h3>" + esc(e.name || "Untitled roll") + "</h3>" +
        "<p>" + esc(e.dice.join(", ")) + "</p>" +
        '<p class="section-note">' + esc(e.ban) + (e.tech ? " · " + esc(e.tech) : "") + "</p>" +
        (e.notes ? "<p>" + esc(e.notes) + "</p>" : "") +
        '<p class="log-actions"><button type="button" class="btn small" data-copy="' + i +
        '">Copy as text</button> <button type="button" class="btn small" data-delete="' + i +
        '">Delete</button></p></li>';
    }).join("");
  }

  function copy(text, button) {
    var done = function (ok) {
      var old = button.textContent;
      button.textContent = ok ? "Copied" : "Couldn't copy";
      setTimeout(function () { button.textContent = old; }, 1600);
    };
    try { navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); }); }
    catch (e) { done(false); }
  }

  function setToggle(group, value) {
    Array.prototype.forEach.call(document.querySelectorAll('[data-' + group + ']'), function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-" + group) === value));
    });
  }

  document.addEventListener("click", function (ev) {
    var t = ev.target.closest("button");
    if (!t) return;
    if (t.id === "rollBtn") { roll(); return; }
    if (t.hasAttribute("data-risk")) { state.risk = t.getAttribute("data-risk"); setToggle("risk", state.risk); return; }
    if (t.id === "houseOnly" || t.id === "techToggle") {
      var on = t.getAttribute("aria-pressed") !== "true";
      t.setAttribute("aria-pressed", String(on));
      if (t.id === "houseOnly") state.houseOnly = on; else { state.technique = on; if (state.dice[0]) render(); }
      return;
    }
    if (t.classList.contains("die")) {
      if (state.rolling) return;
      var kind = t.getAttribute("data-kind"), i = +t.getAttribute("data-index");
      if (kind === "ing") state.held[i] = !state.held[i];
      else if (kind === "ban") state.banHeld = !state.banHeld;
      else state.techHeld = !state.techHeld;
      render();
      return;
    }
    if (t.hasAttribute("data-verdict")) {
      state.verdict = state.verdict === t.getAttribute("data-verdict") ? "" : t.getAttribute("data-verdict");
      setToggle("verdict", state.verdict);
      return;
    }
    if (t.id === "copyRoll") {
      copy(rollText({ dice: state.dice.map(function (d) { return d.name; }), ban: state.ban,
        tech: state.technique ? state.tech : "" }), t);
      return;
    }
    if (t.id === "saveRoll") {
      var list = loadLog();
      list.unshift({
        date: new Date().toISOString().slice(0, 10),
        dice: state.dice.map(function (d) { return d.name; }),
        ban: state.ban, tech: state.technique ? state.tech : "",
        name: $("dishName").value.trim(), verdict: state.verdict, notes: $("dishNotes").value.trim()
      });
      var ok = saveLog(list);
      $("saveStatus").textContent = ok ? "Saved to this browser." : "Couldn't save in this browser. Use Copy instead.";
      if (ok) { $("dishName").value = ""; $("dishNotes").value = ""; state.verdict = ""; setToggle("verdict", ""); }
      renderLog();
      return;
    }
    if (t.hasAttribute("data-copy")) { copy(rollText(loadLog()[+t.getAttribute("data-copy")]), t); return; }
    if (t.hasAttribute("data-delete")) {
      var l = loadLog(); l.splice(+t.getAttribute("data-delete"), 1); saveLog(l); renderLog();
    }
  });

  renderLog();
})(typeof window !== "undefined" ? window : globalThis);
