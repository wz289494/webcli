"""页面内 JavaScript 片段工厂。

当前不少交互能力还是通过 `exec` 执行页面脚本实现，
所以把所有脚本模板集中放在这里，避免分散在 CLI 命令处理函数中。
"""

from __future__ import annotations

import json
from textwrap import dedent


def js_click(selector: str) -> str:
    return dedent(f"""
    (() => {{
      const el = document.querySelector({selector!r});
      if (!el) return {{ error: 'selector_not_found', selector: {selector!r} }};
      el.click();
      return {{ clicked: true, selector: {selector!r} }};
    }})()
    """).strip()


def js_focus(selector: str) -> str:
    return dedent(f"""
    (() => {{
      const el = document.querySelector({selector!r});
      if (!el) return {{ error: 'selector_not_found', selector: {selector!r} }};
      el.focus();
      return {{ focused: true, selector: {selector!r} }};
    }})()
    """).strip()


def js_hover(selector: str) -> str:
    return dedent(f"""
    (() => {{
      const el = document.querySelector({selector!r});
      if (!el) return {{ error: 'selector_not_found', selector: {selector!r} }};
      el.dispatchEvent(new MouseEvent('mouseover', {{ bubbles: true }}));
      return {{ hovered: true, selector: {selector!r} }};
    }})()
    """).strip()


def js_dblclick(selector: str) -> str:
    return dedent(f"""
    (() => {{
      const el = document.querySelector({selector!r});
      if (!el) return {{ error: 'selector_not_found', selector: {selector!r} }};
      el.dispatchEvent(new MouseEvent('dblclick', {{ bubbles: true }}));
      return {{ dblclicked: true, selector: {selector!r} }};
    }})()
    """).strip()


def js_set_value(selector: str, value: str, *, mode: str) -> str:
    return dedent(f"""
    (() => {{
      const el = document.querySelector({selector!r});
      if (!el) return {{ error: 'selector_not_found', selector: {selector!r} }};
      el.focus();
      if ('value' in el) el.value = {value!r}; else el.textContent = {value!r};
      el.dispatchEvent(new Event('input', {{ bubbles: true }}));
      el.dispatchEvent(new Event('change', {{ bubbles: true }}));
      return {{ mode: {mode!r}, selector: {selector!r}, value: 'value' in el ? el.value : el.textContent }};
    }})()
    """).strip()


def js_select(selector: str, value: str) -> str:
    return dedent(f"""
    (() => {{
      const el = document.querySelector({selector!r});
      if (!el) return {{ error: 'selector_not_found', selector: {selector!r} }};
      if (!(el instanceof HTMLSelectElement)) return {{ error: 'not_a_select', selector: {selector!r} }};
      el.value = {value!r};
      el.dispatchEvent(new Event('change', {{ bubbles: true }}));
      return {{ selected: el.value, selector: {selector!r} }};
    }})()
    """).strip()


def js_text(selector: str) -> str:
    return dedent(f"""
    (() => {{
      const el = document.querySelector({selector!r});
      if (!el) return {{ error: 'selector_not_found', selector: {selector!r} }};
      return {{ value: (el.innerText || el.textContent || '').trim(), selector: {selector!r} }};
    }})()
    """).strip()


def js_value(selector: str) -> str:
    return dedent(f"""
    (() => {{
      const el = document.querySelector({selector!r});
      if (!el) return {{ error: 'selector_not_found', selector: {selector!r} }};
      return {{ value: ('value' in el ? el.value : null), selector: {selector!r} }};
    }})()
    """).strip()


def js_attributes(selector: str) -> str:
    return dedent(f"""
    (() => {{
      const el = document.querySelector({selector!r});
      if (!el) return {{ error: 'selector_not_found', selector: {selector!r} }};
      return Object.fromEntries(Array.from(el.attributes).map(a => [a.name, a.value]));
    }})()
    """).strip()


def js_html(selector: str | None = None) -> str:
    target = f"document.querySelector({selector!r})" if selector else "document.documentElement"
    return dedent(f"""
    (() => {{
      const el = {target};
      if (!el) return {{ error: 'selector_not_found', selector: {selector!r} }};
      return {{ html: el.outerHTML ?? '' }};
    }})()
    """).strip()


def js_state() -> str:
    return dedent("""
    (() => {
      const interactive = Array.from(document.querySelectorAll('a, button, input, select, textarea, [role="button"], [tabindex]'))
        .slice(0, 100)
        .map((el, index) => ({
          ref: index + 1,
          tag: el.tagName.toLowerCase(),
          text: (el.innerText || el.textContent || '').trim().slice(0, 120),
          id: el.id || null,
          name: el.getAttribute('name'),
          role: el.getAttribute('role'),
          href: el.getAttribute('href'),
        }));
      return {
        url: location.href,
        title: document.title,
        interactive,
      };
    })()
    """).strip()


def js_find(css: str, limit: int = 50) -> str:
    return dedent(f"""
    (() => {{
      const els = Array.from(document.querySelectorAll({css!r})).slice(0, {limit});
      return {{
        matches_n: els.length,
        entries: els.map((el, index) => ({{
          ref: index + 1,
          tag: el.tagName.toLowerCase(),
          text: (el.innerText || el.textContent || '').trim().slice(0, 120),
          id: el.id || null,
          class: el.className || null,
        }})),
      }};
    }})()
    """).strip()


def js_scroll(direction: str, amount: int) -> str:
    sign = -1 if direction == "up" else 1
    return f"(() => {{ window.scrollBy({{ top: {sign * amount}, behavior: 'smooth' }}); return {{ scrolled: true, direction: {direction!r}, amount: {amount} }}; }})()"


def js_wait_text(text: str) -> str:
    return dedent(f"""(() => !!(document.body && document.body.innerText.includes({text!r})))()""").strip()


def js_wait_selector(selector: str) -> str:
    return dedent(f"""(() => !!document.querySelector({selector!r}))()""").strip()


def js_extract(selector: str | None = None) -> str:
    target = f"document.querySelector({selector!r})" if selector else "document.querySelector('main, article, body')"
    return dedent(f"""
    (() => {{
      const root = {target};
      if (!root) return {{ error: 'selector_not_found', selector: {selector!r} }};
      return {{
        url: location.href,
        title: document.title,
        text: (root.innerText || root.textContent || '').trim(),
      }};
    }})()
    """).strip()


def js_console() -> str:
    return "window.__opencli_console || []"


def js_network() -> str:
    return "window.__opencli_net || []"


def js_check(selector: str, checked: bool) -> str:
    return dedent(f"""
    (() => {{
      const el = document.querySelector({selector!r});
      if (!el) return {{ error: 'selector_not_found', selector: {selector!r} }};
      if (!('checked' in el)) return {{ error: 'not_checkable', selector: {selector!r} }};
      el.checked = {json.dumps(checked)};
      el.dispatchEvent(new Event('change', {{ bubbles: true }}));
      return {{ checked: !!el.checked, selector: {selector!r} }};
    }})()
    """).strip()


def js_analyze() -> str:
    return dedent("""
    (() => ({
      url: location.href,
      title: document.title,
      has_forms: !!document.querySelector('form'),
      links: document.querySelectorAll('a').length,
      buttons: document.querySelectorAll('button,[role="button"]').length,
      inputs: document.querySelectorAll('input,textarea,select').length,
    }))()
    """).strip()
