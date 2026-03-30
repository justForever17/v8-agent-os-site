const pageOrder = ["overview", "runtimes", "install", "docs"];
const pageTrack = document.querySelector("[data-page-track]");
const panels = Array.from(document.querySelectorAll("[data-page]"));
const navButtons = Array.from(document.querySelectorAll("[data-page-target]"));
const docButtons = Array.from(document.querySelectorAll("[data-doc-url]"));
const docViewerTitle = document.querySelector("[data-doc-viewer-title]");
const docViewerBody = document.querySelector("[data-doc-viewer-body]");
const docOpenLink = document.querySelector("[data-doc-open-link]");
const copyButtons = Array.from(document.querySelectorAll(".copy-command"));
const marqueeLines = Array.from(document.querySelectorAll("[data-hover-marquee]"));
const isMobileLayout = () => window.matchMedia("(max-width: 820px)").matches;
const locale = document.body.dataset.locale === "zh" ? "zh" : "en";

const i18n = {
  en: {
    loading: "Loading document...",
    loadFailed: "Unable to load the document right now.",
    copied: "Copied",
    copyFailed: "Copy failed",
  },
  zh: {
    loading: "正在加载文档...",
    loadFailed: "暂时无法加载这份文档。",
    copied: "已复制",
    copyFailed: "复制失败",
  },
};

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderInline(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
}

function renderMarkdown(markdown) {
  const lines = markdown.replace(/\r/g, "").split("\n");
  const html = [];
  let paragraph = [];
  let listType = null;
  let inCodeBlock = false;
  let codeFenceLanguage = "";
  let codeBuffer = [];

  const flushParagraph = () => {
    if (!paragraph.length) {
      return;
    }
    html.push(`<p>${renderInline(paragraph.join(" ").trim())}</p>`);
    paragraph = [];
  };

  const flushList = () => {
    if (!listType) {
      return;
    }
    html.push(`</${listType}>`);
    listType = null;
  };

  const flushCodeBlock = () => {
    const code = escapeHtml(codeBuffer.join("\n"));
    const languageClass = codeFenceLanguage ? ` class="language-${escapeHtml(codeFenceLanguage)}"` : "";
    html.push(`<pre><code${languageClass}>${code}</code></pre>`);
    codeBuffer = [];
    codeFenceLanguage = "";
  };

  for (const rawLine of lines) {
    const line = rawLine.replace(/\t/g, "  ");

    if (line.startsWith("```")) {
      flushParagraph();
      flushList();
      if (inCodeBlock) {
        flushCodeBlock();
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
        codeFenceLanguage = line.slice(3).trim();
      }
      continue;
    }

    if (inCodeBlock) {
      codeBuffer.push(rawLine);
      continue;
    }

    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }

    if (/^#{1,3}\s/.test(line)) {
      flushParagraph();
      flushList();
      const level = line.match(/^#+/)[0].length;
      html.push(`<h${level}>${renderInline(line.replace(/^#{1,3}\s+/, ""))}</h${level}>`);
      continue;
    }

    if (/^>\s?/.test(line)) {
      flushParagraph();
      flushList();
      html.push(`<blockquote>${renderInline(line.replace(/^>\s?/, ""))}</blockquote>`);
      continue;
    }

    if (/^---+$/.test(line.trim())) {
      flushParagraph();
      flushList();
      html.push("<hr />");
      continue;
    }

    if (/^[-*]\s+/.test(line)) {
      flushParagraph();
      if (listType !== "ul") {
        flushList();
        listType = "ul";
        html.push("<ul>");
      }
      html.push(`<li>${renderInline(line.replace(/^[-*]\s+/, ""))}</li>`);
      continue;
    }

    if (/^\d+\.\s+/.test(line)) {
      flushParagraph();
      if (listType !== "ol") {
        flushList();
        listType = "ol";
        html.push("<ol>");
      }
      html.push(`<li>${renderInline(line.replace(/^\d+\.\s+/, ""))}</li>`);
      continue;
    }

    flushList();
    paragraph.push(line.trim());
  }

  flushParagraph();
  flushList();

  if (inCodeBlock) {
    flushCodeBlock();
  }

  return html.join("");
}

function getCurrentPage() {
  const hash = window.location.hash.replace(/^#/, "").trim();
  return pageOrder.includes(hash) ? hash : "overview";
}

function syncPageState(pageName, options = {}) {
  if (!pageOrder.includes(pageName)) {
    return;
  }

  navButtons.forEach((button) => {
    const isActive = button.dataset.pageTarget === pageName;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-current", isActive ? "page" : "false");
  });

  panels.forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.page === pageName);
  });

  if (!options.skipHash) {
    window.history.replaceState(null, "", `#${pageName}`);
  }
}

function getDocSources(button) {
  const items = [];

  if (locale === "zh" && button.dataset.docUrlZh) {
    items.push({
      url: button.dataset.docUrlZh,
      open: button.dataset.docOpenZh || button.dataset.docOpen || "#",
    });
  }

  if (button.dataset.docUrl) {
    items.push({
      url: button.dataset.docUrl,
      open: button.dataset.docOpen || "#",
    });
  }

  return items;
}

async function loadDocument(button) {
  if (!docViewerBody || !docViewerTitle || !docOpenLink) {
    return;
  }

  docButtons.forEach((item) => item.classList.toggle("is-active", item === button));
  docViewerTitle.textContent = button.dataset.docTitle || "Document";
  docViewerBody.innerHTML = `<p>${i18n[locale].loading}</p>`;

  const sources = getDocSources(button);
  if (!sources.length) {
    docOpenLink.href = "#";
    docViewerBody.innerHTML = `<p>${i18n[locale].loadFailed}</p>`;
    return;
  }

  docOpenLink.href = sources[0].open;

  let lastError = "Unknown error";

  for (const source of sources) {
    try {
      const response = await fetch(source.url, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`Request failed with ${response.status}`);
      }

      const markdown = await response.text();
      docOpenLink.href = source.open;
      docViewerBody.innerHTML = renderMarkdown(markdown);
      return;
    } catch (error) {
      lastError = error instanceof Error ? error.message : "Unknown error";
    }
  }

  docViewerBody.innerHTML = `<p>${i18n[locale].loadFailed}</p><p><code>${escapeHtml(lastError)}</code></p>`;
}

function bindCopyButtons() {
  copyButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      const text = button.dataset.copy;
      if (!text) {
        return;
      }

      try {
        await navigator.clipboard.writeText(text);
        const previous = button.textContent;
        button.textContent = i18n[locale].copied;
        button.classList.add("is-copied");
        window.setTimeout(() => {
          button.textContent = previous;
          button.classList.remove("is-copied");
        }, 1500);
      } catch {
        button.textContent = i18n[locale].copyFailed;
      }
    });
  });
}

function bindNavigation() {
  navButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const target = button.dataset.pageTarget;
      if (!target) {
        return;
      }
      syncPageState(target);
    });
  });

  window.addEventListener("resize", () => {
    syncPageState(getCurrentPage(), { skipHash: true });
    bindHoverMarquee();
  });
}

function bindDocs() {
  docButtons.forEach((button) => {
    button.addEventListener("click", () => {
      loadDocument(button);
    });
  });

  if (docButtons.length) {
    loadDocument(docButtons[0]);
  }
}

function bindHoverMarquee() {
  marqueeLines.forEach((line) => {
    const textNode = line.querySelector(".runtime-scroll-text");
    if (!textNode || isMobileLayout()) {
      line.dataset.overflow = "false";
      line.style.setProperty("--overflow-shift", "0px");
      if (textNode) {
        textNode.style.transform = "translateX(0)";
      }
      return;
    }

    line.dataset.overflow = "false";
    line.style.setProperty("--overflow-shift", "0px");

    const overflow = Math.max(0, Math.ceil(textNode.scrollWidth - line.clientWidth));
    if (overflow > 8) {
      line.dataset.overflow = "true";
      line.style.setProperty("--overflow-shift", `${overflow + 12}px`);
    }
  });
}

bindNavigation();
bindDocs();
bindCopyButtons();
bindHoverMarquee();
syncPageState(getCurrentPage(), { skipHash: true });
