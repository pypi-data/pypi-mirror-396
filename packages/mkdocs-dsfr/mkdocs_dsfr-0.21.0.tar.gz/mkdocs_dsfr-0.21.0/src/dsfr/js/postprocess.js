document.addEventListener("DOMContentLoaded", addBackToTopButton);
document.addEventListener("DOMContentLoaded", checkboxReplacer);
document.addEventListener("DOMContentLoaded", strikethroughReplacer);
document.addEventListener("DOMContentLoaded", copyCode);
document.addEventListener("DOMContentLoaded", swapHeadingTags);
document.addEventListener("DOMContentLoaded", addTocPrintPage);

function addBackToTopButton() {
  console.log("Check if add back to top is needed");
  if (document.documentElement.scrollHeight > window.innerHeight * 2) {
    console.log("Back to top is needed");
    const link = document.createElement("a");
    link.className = "fr-link fr-icon-arrow-up-fill fr-link--icon-right";
    link.href = "#top";
    link.textContent = "Haut de page";

    const contenuDiv = document.getElementById("backtop");
    if (contenuDiv) {
      contenuDiv.appendChild(link);
    }

    const lateralDiv = document.getElementById("backtop_lateral");
    if (lateralDiv) {
      const lateralLink = link.cloneNode(true);
      lateralLink.className =
        "fr-sidemenu__link fr-icon-arrow-up-fill fr-link--icon-right";
      lateralDiv.appendChild(lateralLink);
    }
  } else {
    console.log("Back to top is not needed");
  }
}

function copyCode() {
  const codeBlocks = document.querySelectorAll("pre > code");
  console.log(codeBlocks);

  for (const [index, codeBlock] of codeBlocks.entries()) {
    const copyButton = document.createElement("button");
    copyButton.textContent = "Copier";
    copyButton.className =
      "fr-btn fr-btn--sm copy-code-button fr-btn--secondary";
    copyButton.dataset.clipboardIndex = index;
    codeBlock.parentElement.style.position = "relative";
    codeBlock.parentElement.appendChild(copyButton);

    copyButton.addEventListener("click", (event) => {
      if (navigator.clipboard && globalThis.isSecureContext) {
        navigator.clipboard
          .writeText(codeBlock.textContent)
          .catch((err) => {
            console.error("Erreur de copie dans le presse-papiers :", err);
          })
          .then(() => {
            copyButton.textContent = "Copié !";
            setTimeout(() => {
              copyButton.textContent = "Copier";
            }, 2000);
          });
      }
    });
  }
}

function checkboxReplacer() {
  // Sélectionner tous les éléments avec la classe 'markdown-content'
  const markdownElements = document.querySelectorAll(".markdown-content");

  // Parcourir chaque élément ayant la classe 'markdown-content'
  for(const element of markdownElements) {
    // Obtenir tous les éléments de liste dans chaque élément 'markdown-content'
    const listItems = element.querySelectorAll("li");

    // Parcourir chaque élément de la liste
    for(const listItem of listItems) {
      let innerHTML = listItem.innerHTML;

      // Remplacer [x] par une case à cocher cochée en HTML ou [ ] par une case non cochée
      if (innerHTML.includes("[x]") || innerHTML.includes("[ ]")) {
        // Supprimer les balises <p> enveloppantes si elles existent
        innerHTML = innerHTML.replaceAll(/(.*?)/, "$1").trim();

        // Appliquer des styles en ligne pour supprimer le style de liste
        listItem.style.listStyleType = "none";

        // Si la tâche est cochée ([x])
        if (innerHTML.includes("[x]")) {
          const taskDescription = innerHTML.replace("[x]", "").trim();
          listItem.innerHTML = `
                  <div class="fr-checkbox-group">
                      <input  id="checkbox-${taskDescription}" type="checkbox" checked>
                      <label class="fr-label" for="checkbox-${taskDescription}">
                          ${taskDescription}
                      </label>
                  </div>`;
        }

        // Si la tâche n'est pas cochée ([ ])
        else if (innerHTML.includes("[ ]")) {
          const taskDescription = innerHTML.replace("[ ]", "").trim();
          listItem.innerHTML = `
                  <div class="fr-checkbox-group">
                      <input id="checkbox-${taskDescription}" type="checkbox">
                      <label class="fr-label" for="checkbox-${taskDescription}">
                          ${taskDescription}
                      </label>
                  </div>`;
        }
      }
    }
  }
}

function strikethroughReplacer() {
  // Sélectionne tous les éléments avec la classe markdown-content
  const markdownElements = document.querySelectorAll(".markdown-content");

  for (const element of markdownElements) {
    let innerHTML = element.innerHTML;

    // Remplace ~~texte~~ par <del>texte</del>
    innerHTML = innerHTML.replaceAll(/~~(.*?)~~/, "<del>$1</del>");

    element.innerHTML = innerHTML;
  }
}
function swapHeadingTags() {
  const node1 = document.querySelector("h1");
  const node2 = document.getElementById("tags-navigation");
  if (node1 && node2) {
    // Déplace node1 avant node2
    node1.before(node2);
    // Déplace node2 après node1 (nouvelle position)
    node2.after(node1);
  }
}


function addTocPrintPage() {
  const toc = document.querySelector("#print-page-toc nav");
  if (!toc) {
    console.info("No TOC container found for print page.");
    return;
  }

  const tocContainer = document.createElement("ul");
  const headings = document.querySelectorAll("section.print-page");

  for (const heading of headings) {
    const titleElements = heading.querySelectorAll("h1, h2");
    for (const titleElement of titleElements) {
      const listItem = document.createElement("li");
      // Add class 'h1-entry', 'h2-entry', etc. based on heading level
      listItem.className = `${titleElement.tagName.toLowerCase()}-entry`;
      const link = document.createElement("a");
      link.href = `#${titleElement.id}`;
      link.textContent = titleElement.textContent;
      listItem.appendChild(link);
      tocContainer.appendChild(listItem);
    }
  }
  toc.appendChild(tocContainer);
}
