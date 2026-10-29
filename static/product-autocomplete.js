(function () {
  const input = document.getElementById("was");
  const list = document.getElementById("was-list");
  if (!input || !list) {
    return;
  }

  let catalog = [];
  let shown = [];
  let active = -1;

  function fold(value) {
    return value
      .toLocaleLowerCase("de")
      .replaceAll("ä", "ae")
      .replaceAll("ö", "oe")
      .replaceAll("ü", "ue")
      .replaceAll("ß", "ss");
  }

  function hide() {
    list.hidden = true;
    list.replaceChildren();
    input.setAttribute("aria-expanded", "false");
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

  function choose(index) {
    if (!shown[index]) {
      return;
    }
    input.value = shown[index].name;
    hide();
  }

  function render(matches) {
    list.replaceChildren();
    shown = matches;
    if (!matches.length) {
      hide();
      return;
    }
    matches.forEach(function (entry, index) {
      const item = document.createElement("li");
      item.setAttribute("role", "option");
      const button = document.createElement("button");
      button.type = "button";
      const name = document.createElement("span");
      name.textContent = entry.name;
      const kind = document.createElement("span");
      kind.className = "kind";
      kind.textContent = entry.kind;
      button.append(name, kind);
      button.addEventListener("mousedown", function (event) {
        event.preventDefault();
        choose(index);
      });
      item.append(button);
      list.append(item);
    });
    list.hidden = false;
    input.setAttribute("aria-expanded", "true");
    setActive(0);
  }

  function search(query) {
    const folded = fold(query.trim());
    if (folded.length < 2) {
      return [];
    }
    const hits = catalog.filter(function (entry) {
      return fold(entry.name).includes(folded);
    });
    hits.sort(function (left, right) {
      const leftStart = fold(left.name).startsWith(folded) ? 0 : 1;
      const rightStart = fold(right.name).startsWith(folded) ? 0 : 1;
      if (leftStart !== rightStart) {
        return leftStart - rightStart;
      }
      const rank = { Kategorie: 0, Marke: 1, Produkt: 2 };
      const leftKind = rank[left.kind];
      const rightKind = rank[right.kind];
      if (leftKind !== rightKind) {
        return leftKind - rightKind;
      }
      return left.name.localeCompare(right.name, "de");
    });
    return hits.slice(0, 8);
  }

  function refresh() {
    load().then(function () {
      render(search(input.value));
    });
  }

  async function load() {
    if (catalog.length) {
      return;
    }
    const response = await fetch(input.dataset.products);
    const data = await response.json();
    catalog = data.kategorien
      .map(function (name) {
        return { name: name, kind: "Kategorie" };
      })
      .concat(
        data.marken.map(function (name) {
          return { name: name, kind: "Marke" };
        })
      )
      .concat(
        data.produkte.map(function (name) {
          return { name: name, kind: "Produkt" };
        })
      );
  }

  input.addEventListener("input", refresh);
  input.addEventListener("focus", refresh);
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
      choose(active);
    } else if (event.key === "Escape") {
      hide();
    }
  });
  document.addEventListener("click", function (event) {
    if (!input.parentElement.contains(event.target)) {
      hide();
    }
  });
})();
