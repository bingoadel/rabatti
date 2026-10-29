(function () {
  const form = document.getElementById("discount-search");
  const button = document.getElementById("find-products");
  const hint = document.getElementById("search-hint");
  if (!form || !button) {
    return;
  }

  const placeInput = document.getElementById("wo");
  const marketInput = document.getElementById("markt");
  const chosenList = document.getElementById("chosen-products");
  const addButton = document.getElementById("add-product");
  let data = { orte: [], kategorien: [] };
  let rowSerial = chosenList ? chosenList.querySelectorAll(".product-line").length : 0;

  function fold(value) {
    return value
      .toLocaleLowerCase("de")
      .replaceAll("ä", "ae")
      .replaceAll("ö", "oe")
      .replaceAll("ü", "ue")
      .replaceAll("ß", "ss");
  }

  function exact(value, options) {
    const folded = fold(value.trim());
    if (!folded) {
      return "";
    }
    return options.find(function (option) {
      return fold(option) === folded;
    }) || "";
  }

  function categoryNames() {
    return data.kategorien.map(function (category) {
      return category.name;
    });
  }

  function categoryCount(name) {
    const entry = data.kategorien.find(function (category) {
      return category.name === name;
    });
    if (!entry) {
      return 0;
    }
    if (entry.anzahl != null) {
      return entry.anzahl;
    }
    return entry.unterkategorien.reduce(function (sum, sub) {
      return sum + sub.produkte.length;
    }, 0);
  }

  function subcategoryCount(name, categoryName) {
    let count = 0;
    data.kategorien.forEach(function (category) {
      if (categoryName && category.name !== categoryName) {
        return;
      }
      category.unterkategorien.forEach(function (sub) {
        if (sub.name === name) {
          count += sub.anzahl != null ? sub.anzahl : sub.produkte.length;
        }
      });
    });
    return count;
  }

  function categoryEntry(name) {
    const found = exact(name, categoryNames());
    return data.kategorien.find(function (category) {
      return category.name === found;
    }) || null;
  }

  function subNames(categoryName) {
    const category = categoryName ? categoryEntry(categoryName) : null;
    const source = category ? [category] : data.kategorien;
    const names = [];
    source.forEach(function (entry) {
      entry.unterkategorien.forEach(function (sub) {
        if (!names.includes(sub.name)) {
          names.push(sub.name);
        }
      });
    });
    return names;
  }

  function productRecord(name) {
    const folded = fold(name.trim());
    if (!folded) {
      return null;
    }
    const kinds = data.produktarten || [];
    const found = kinds.find(function (kind) {
      return fold(kind) === folded;
    });
    if (!found) {
      return null;
    }
    const demand = (data.bedarf || {})[found] || { einheit: "Stück", schritt: 1, minimum: 1, vorgabe: 1 };
    return { name: found, demand: demand };
  }

  function productNames() {
    return data.produktarten || [];
  }

  function validProductRows() {
    const seen = new Set();
    const rows = [];
    if (!chosenList) {
      return rows;
    }
    chosenList.querySelectorAll(".product-line").forEach(function (row) {
      const input = row.querySelector(".product-field");
      const record = input ? productRecord(input.value) : null;
      if (!record) {
        return;
      }
      const key = fold(record.name);
      if (seen.has(key)) {
        return;
      }
      seen.add(key);
      rows.push(row);
    });
    return rows;
  }

  function removeButton() {
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "remove-product";
    remove.title = "entfernen";
    remove.setAttribute("aria-label", "entfernen");
    remove.innerHTML = '<svg class="trash-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 7h15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M9 7V5.6c0-.9.7-1.6 1.6-1.6h2.8c.9 0 1.6.7 1.6 1.6V7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M6.8 7.2 8 19.2h8l1.2-12" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M10 11v5.2M14 11v5.2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
    return remove;
  }

  function fillAmount(stepper, record) {
    const demand = record.demand;
    stepper.className = "amount-stepper";
    stepper.dataset.kind = record.name;
    stepper.replaceChildren();
    const minus = document.createElement("button");
    minus.type = "button";
    minus.className = "amount-step amount-minus";
    minus.setAttribute("aria-label", "Menge für " + record.name + " verringern");
    minus.textContent = "−";
    const field = document.createElement("input");
    field.type = "text";
    field.inputMode = "decimal";
    field.name = "mengen";
    field.value = formatAmount(demand.vorgabe);
    field.dataset.step = demand.schritt;
    field.dataset.min = demand.minimum;
    field.dataset.default = demand.vorgabe;
    field.setAttribute("aria-label", "Menge für " + record.name);
    const plus = document.createElement("button");
    plus.type = "button";
    plus.className = "amount-step amount-plus";
    plus.setAttribute("aria-label", "Menge für " + record.name + " erhöhen");
    plus.textContent = "+";
    const unit = document.createElement("span");
    unit.className = "amount-unit";
    unit.textContent = demand.einheit;
    stepper.append(minus, field, plus, unit);
  }

  function syncRow(row) {
    const input = row.querySelector(".product-field");
    const record = productRecord(input.value);
    const duplicate = record && validProductRows().some(function (other) {
      return other !== row && fold(other.querySelector(".product-field").value) === fold(record.name);
    });
    const stepper = row.querySelector(".amount-stepper");
    if (!record || duplicate) {
      if (stepper) {
        stepper.remove();
      }
      return;
    }
    if (input.value !== record.name) {
      input.value = record.name;
    }
    if (stepper && stepper.dataset.kind === record.name && stepper.querySelector('input[name="mengen"]')) {
      return;
    }
    const next = stepper || document.createElement("span");
    fillAmount(next, record);
    const remove = row.querySelector(".remove-product");
    if (!stepper) {
      row.insertBefore(next, remove);
    }
  }

  function bindProductRow(row) {
    const input = row.querySelector(".product-field");
    const list = row.querySelector(".suggestions");
    if (!input || !list || input.dataset.bound === "1") {
      return;
    }
    input.dataset.bound = "1";
    bindList(input, list, productNames, null, { maxResults: 40, minQuery: 1 });
    input.addEventListener("value-picked", function () {
      syncRow(row);
      refreshForm();
    });
    input.addEventListener("input", function () {
      syncRow(row);
    });
    input.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
      }
    });
  }

  function addProductRow() {
    if (!chosenList) {
      return;
    }
    rowSerial += 1;
    const row = document.createElement("li");
    row.className = "product-line";
    const entry = document.createElement("div");
    entry.className = "suggest product-entry";
    const input = document.createElement("input");
    input.className = "product-field";
    input.type = "text";
    input.name = "produkte";
    input.placeholder = "Produktart, zum Beispiel Magerquark";
    input.autocomplete = "off";
    input.setAttribute("role", "combobox");
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("aria-expanded", "false");
    input.setAttribute("aria-controls", "produkt-list-" + rowSerial);
    const list = document.createElement("ul");
    list.id = "produkt-list-" + rowSerial;
    list.className = "suggestions";
    list.hidden = true;
    list.setAttribute("role", "listbox");
    entry.append(input, list);
    row.append(entry, removeButton());
    chosenList.append(row);
    bindProductRow(row);
    input.focus();
    refreshForm();
  }

  function formatAmount(value) {
    const number = Number(value);
    if (!Number.isFinite(number)) {
      return "";
    }
    if (Math.abs(number - Math.round(number)) < 1e-9) {
      return String(Math.round(number));
    }
    return String(Math.round(number * 100) / 100).replace(".", ",");
  }

  function readAmount(input) {
    const number = Number(String(input.value).trim().replace(",", "."));
    return Number.isFinite(number) ? number : NaN;
  }

  function stepAmount(input, direction) {
    const step = Number(input.dataset.step) || 1;
    const minimum = Number(input.dataset.min);
    const fallback = Number(input.dataset.default);
    let current = readAmount(input);
    if (!Number.isFinite(current)) {
      current = Number.isFinite(fallback) ? fallback : minimum;
    }
    let next = current + direction * step;
    if (Number.isFinite(minimum) && next < minimum) {
      next = minimum;
    }
    input.value = formatAmount(next);
  }

  function placeName(label) {
    if (/^\d{5} /.test(label)) {
      return label.slice(6);
    }
    const comma = label.indexOf(", ");
    return comma === -1 ? label : label.slice(0, comma);
  }

  function placeHits(options, query, limit) {
    const text = query.trim();
    const folded = fold(text);
    const digits = /^\d+$/.test(text);
    const starts = [];
    const contains = [];
    for (let index = 0; index < options.length; index += 1) {
      const option = options[index];
      const name = placeName(option);
      if (digits) {
        if (option.startsWith(text)) {
          starts.push(option);
        }
        continue;
      }
      const foldedName = fold(name);
      if (foldedName.startsWith(folded)) {
        starts.push(option);
      } else if (contains.length < limit && foldedName.includes(folded)) {
        contains.push(option);
      }
    }
    starts.sort(function (left, right) {
      return placeName(left).localeCompare(placeName(right), "de") || left.localeCompare(right, "de");
    });
    return starts.concat(contains).slice(0, limit);
  }

  function placeAccepted(value) {
    const text = value.trim();
    const folded = fold(text);
    if (!folded) {
      return "";
    }
    if (data.orte.some(function (option) { return fold(option) === folded; })) {
      return text;
    }
    if (/^\d{5}$/.test(text) && data.orte.some(function (option) { return option.startsWith(text + " "); })) {
      return text;
    }
    if (data.orte.some(function (option) { return fold(placeName(option)) === folded; })) {
      return text;
    }
    return "";
  }

  function matches(options, query, limit) {
    const folded = fold(query.trim());
    const hits = options.filter(function (option) {
      return !folded || fold(option).includes(folded);
    });
    hits.sort(function (left, right) {
      const leftStart = folded && fold(left).startsWith(folded) ? 0 : 1;
      const rightStart = folded && fold(right).startsWith(folded) ? 0 : 1;
      if (leftStart !== rightStart) {
        return leftStart - rightStart;
      }
      return left.localeCompare(right, "de");
    });
    return limit ? hits.slice(0, limit) : hits;
  }

  function hideList(list, input) {
    list.hidden = true;
    list.replaceChildren();
    input.setAttribute("aria-expanded", "false");
  }

  function bindList(input, list, optionsFor, labelFor, limits) {
    let shown = [];
    let active = -1;
    const maxResults = limits && limits.maxResults;
    const minQuery = limits && limits.minQuery ? limits.minQuery : 0;

    function hide() {
      hideList(list, input);
      shown = [];
      active = -1;
    }

    function setActive(index) {
      const buttons = list.querySelectorAll("button");
      buttons.forEach(function (button, position) {
        button.classList.toggle("is-active", position === index);
      });
      active = index;
      if (buttons[index]) {
        buttons[index].scrollIntoView({ block: "nearest" });
      }
    }

    function render() {
      document.querySelectorAll(".suggestions").forEach(function (other) {
        if (other !== list) {
          other.hidden = true;
          other.replaceChildren();
        }
      });
      shown = limits && limits.byPlace
        ? placeHits(optionsFor(), input.value, maxResults || 40)
        : matches(optionsFor(), input.value, maxResults);
      list.replaceChildren();
      if (input.value.trim().length < minQuery || !shown.length) {
        hide();
        return;
      }
      shown.forEach(function (name, index) {
        const item = document.createElement("li");
        item.setAttribute("role", "option");
        const choice = document.createElement("button");
        choice.type = "button";
        const label = labelFor ? labelFor(name) : { text: name };
        choice.append(document.createTextNode(label.text));
        if (label.count != null) {
          const mark = document.createElement("span");
          mark.className = "kind";
          mark.textContent = "(" + label.count + ")";
          choice.append(mark);
        }
        choice.addEventListener("mousedown", function (event) {
          event.preventDefault();
          input.value = name;
          hide();
          input.dispatchEvent(new Event("value-picked"));
        });
        item.append(choice);
        list.append(item);
      });
      list.hidden = false;
      input.setAttribute("aria-expanded", "true");
      setActive(0);
    }

    input.addEventListener("input", function () {
      render();
      refreshForm();
    });
    input.addEventListener("focus", render);
    input.addEventListener("keydown", function (event) {
      if (list.hidden) {
        return;
      }
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setActive(Math.min(active + 1, shown.length - 1));
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setActive(Math.max(active - 1, 0));
      } else if (event.key === "Enter" && active >= 0) {
        event.preventDefault();
        input.value = shown[active];
        hide();
        input.dispatchEvent(new Event("value-picked"));
      } else if (event.key === "Escape") {
        hide();
      }
    });
    return hide;
  }

  function formIsReady() {
    const place = placeAccepted(placeInput.value);
    if (placeInput.value.trim() && !place) {
      return false;
    }
    return Boolean(place && marketInput && marketInput.value && validProductRows().length);
  }

  function refreshForm() {
    const ready = (data.produktarten || []).length > 0 && formIsReady();
    button.disabled = !ready;
    if (hint) {
      hint.hidden = ready;
    }
  }

  bindList(placeInput, document.getElementById("wo-list"), function () {
    return data.orte;
  }, null, { maxResults: 40, minQuery: 1, byPlace: true });
  if (chosenList) {
    chosenList.querySelectorAll(".product-line").forEach(bindProductRow);
  }
  if (addButton) {
    addButton.addEventListener("click", addProductRow);
  }
  if (chosenList) {
    chosenList.addEventListener("click", function (event) {
      const stepButton = event.target.closest(".amount-minus, .amount-plus");
      if (stepButton) {
        const input = stepButton.parentElement.querySelector('input[name="mengen"]');
        if (input) {
          stepAmount(input, stepButton.classList.contains("amount-plus") ? 1 : -1);
        }
        return;
      }
      const remove = event.target.closest(".remove-product");
      if (!remove) {
        return;
      }
      remove.closest("li").remove();
      refreshForm();
    });
  }
  if (marketInput) {
    marketInput.addEventListener("change", refreshForm);
  }
  document.addEventListener("click", function (event) {
    if (!form.contains(event.target)) {
      form.querySelectorAll(".suggestions").forEach(function (list) {
        list.hidden = true;
        list.replaceChildren();
      });
    }
  });
  const waiting = document.getElementById("waiting");
  let submitting = false;
  form.addEventListener("submit", function (event) {
    if (!formIsReady() || submitting) {
      event.preventDefault();
      return;
    }
    event.preventDefault();
    submitting = true;
    const valid = new Set(validProductRows());
    chosenList.querySelectorAll(".product-line").forEach(function (row) {
      const input = row.querySelector(".product-field");
      const amount = row.querySelector('input[name="mengen"]');
      if (!valid.has(row)) {
        input.disabled = true;
        if (amount) {
          amount.disabled = true;
        }
        return;
      }
      const record = productRecord(input.value);
      if (record) {
        input.value = record.name;
      }
    });
    if (waiting) {
      waiting.hidden = false;
    }
    button.disabled = true;
    const waitMs = waiting ? Number(waiting.dataset.waitMs) || 2000 : 2000;
    window.setTimeout(function () {
      form.submit();
    }, waitMs);
  });

  fetch(form.dataset.katalog)
    .then(function (response) {
      return response.json();
    })
    .then(function (payload) {
      data = payload;
      refreshForm();
    })
    .catch(function () {
      button.disabled = true;
    });
})();
