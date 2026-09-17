document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('select[data-neo-select]').forEach(initNeoSelect);
});

function initNeoSelect(selectEl) {
  const wrap = document.createElement('div');
  wrap.className = 'neo-select-wrap';
  selectEl.parentNode.insertBefore(wrap, selectEl);
  wrap.appendChild(selectEl);

  const trigger = document.createElement('div');
  trigger.className = 'neo-select-trigger';
  trigger.tabIndex = 0;
  wrap.appendChild(trigger);

  const panel = document.createElement('div');
  panel.className = 'neo-select-panel';
  wrap.appendChild(panel);

  function buildPanel() {
    panel.innerHTML = '';
    let currentGroup = null;
    Array.from(selectEl.children).forEach(child => {
      if (child.tagName === 'OPTGROUP') {
        const label = document.createElement('div');
        label.className = 'neo-optgroup-label';
        label.textContent = child.label;
        panel.appendChild(label);
        Array.from(child.children).forEach(opt => panel.appendChild(buildOption(opt)));
      } else if (child.tagName === 'OPTION') {
        panel.appendChild(buildOption(child));
      }
    });
  }

  function buildOption(opt) {
    const row = document.createElement('div');
    row.className = 'neo-option' + (opt.selected ? ' selected' : '');
    row.textContent = opt.textContent;
    row.dataset.value = opt.value;
    row.addEventListener('click', () => {
      selectEl.value = opt.value;
      selectEl.dispatchEvent(new Event('change', { bubbles: true }));
      syncTrigger();
      closePanel();
    });
    return row;
  }

  function syncTrigger() {
    const selectedOpt = selectEl.options[selectEl.selectedIndex];
    trigger.textContent = selectedOpt ? selectedOpt.textContent : '';
    panel.querySelectorAll('.neo-option').forEach(o => {
      o.classList.toggle('selected', o.dataset.value === selectEl.value);
    });
  }

  function openPanel() {
    trigger.classList.add('open');
    panel.classList.add('open');
    const selected = panel.querySelector('.selected');
    if (selected) selected.scrollIntoView({ block: 'nearest' });
  }

  function closePanel() {
    trigger.classList.remove('open');
    panel.classList.remove('open');
  }

  trigger.addEventListener('click', () => {
    panel.classList.contains('open') ? closePanel() : openPanel();
  });

  document.addEventListener('click', (e) => {
    if (!wrap.contains(e.target)) closePanel();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closePanel();
  });

  // Listen for external changes to the select (e.g. from auto-suggest)
  selectEl.addEventListener('change', syncTrigger);

  buildPanel();
  syncTrigger();
}
