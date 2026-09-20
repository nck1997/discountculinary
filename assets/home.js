// Photo-wall filtering. The cards are already in the HTML (good for search
// engines and for no-JS); this only hides the ones that don't match.
(function () {
  var cards = Array.prototype.slice.call(document.querySelectorAll("#wall .card"));
  var search = document.getElementById("search");
  var proteinRange = document.getElementById("proteinRange");
  var calorieRange = document.getElementById("calorieRange");
  var proteinValue = document.getElementById("proteinValue");
  var calorieValue = document.getElementById("calorieValue");
  var count = document.getElementById("resultsCount");
  var clear = document.getElementById("clearFilters");
  var empty = document.getElementById("empty");
  var filters = document.getElementById("filters");
  var tagButtons = Array.prototype.slice.call(document.querySelectorAll("[data-tag]"));
  var maxCalories = Number(calorieRange.max);
  var activeTags = new Set();

  // On phones the filter sheet starts folded so the photos come first.
  if (window.matchMedia("(max-width: 860px)").matches) {
    filters.open = false;
  }

  function apply() {
    var q = search.value.trim().toLowerCase();
    var minProtein = Number(proteinRange.value);
    var maxKcal = Number(calorieRange.value);
    var shown = 0;

    cards.forEach(function (card) {
      var tags = card.dataset.tags.split("|");
      var ok =
        (!q || card.dataset.search.indexOf(q) !== -1) &&
        Number(card.dataset.protein) >= minProtein &&
        Number(card.dataset.kcal) <= maxKcal &&
        Array.from(activeTags).every(function (t) { return tags.indexOf(t) !== -1; });
      card.hidden = !ok;
      if (ok) shown += 1;
    });

    proteinValue.textContent = minProtein;
    calorieValue.textContent = maxKcal;
    count.textContent = shown + (shown === 1 ? " recipe" : " recipes");
    empty.hidden = shown !== 0;
    clear.hidden = !(q || minProtein > 0 || maxKcal < maxCalories || activeTags.size);
  }

  tagButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var tag = btn.dataset.tag;
      if (activeTags.has(tag)) activeTags.delete(tag); else activeTags.add(tag);
      btn.setAttribute("aria-pressed", String(activeTags.has(tag)));
      apply();
    });
  });

  clear.addEventListener("click", function () {
    search.value = "";
    proteinRange.value = 0;
    calorieRange.value = maxCalories;
    activeTags.clear();
    tagButtons.forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
    apply();
  });

  [search, proteinRange, calorieRange].forEach(function (el) {
    el.addEventListener("input", apply);
  });

  apply();
})();
