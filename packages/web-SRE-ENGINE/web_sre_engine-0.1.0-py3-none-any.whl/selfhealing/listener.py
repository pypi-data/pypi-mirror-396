import json
import os
import re
from dotenv import load_dotenv
from openai import AzureOpenAI
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
import difflib
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
import yaml



from bs4 import BeautifulSoup

# -----------------------------
# Self-Healing Web Listener
# -----------------------------
class SelfHealingWebListener:
    ROBOT_LISTENER_API_VERSION = 3

    # JS snippet (browser) to gather interactable elements — runs inside the page
    JS_GATHER_INTERACTABLES = r"""
    ({ strict, max }) => {
      const normalize = s => (s || '').replace(/\s+/g, ' ').trim();

      const isHidden = el => {
        try {
          const cs = getComputedStyle(el);
          const rect = el.getBoundingClientRect();
          const hiddenByStyle = cs && (cs.display === "none" || cs.visibility === "hidden" || parseFloat(cs.opacity || "1") < 0.01);
          const hiddenBySize = rect && (rect.width < 2 && rect.height < 2);
          const hiddenByAttr = el.closest && el.closest("[hidden], [inert], [aria-hidden='true']");
          return hiddenByStyle || hiddenBySize || hiddenByAttr;
        } catch(e) {
          return false;
        }
      };

      const isDisabled = el => {
        try {
          const disabled = (el.matches && el.matches(":disabled")) || el.getAttribute("aria-disabled") === "true";
          return strict ? disabled : false;
        } catch(e) {
          return false;
        }
      };

      const isInteractable = el => {
        try {
          if (isHidden(el)) return false;
          if (isDisabled(el)) return false;

          const role = el.getAttribute && el.getAttribute("role");
          if (el.matches && el.matches("button, input:not([type='hidden']), textarea, select, a[href], [contenteditable]")) return true;
          if (role === "button" || role === "link") return true;
          if (el.tabIndex >= 0) return true;
          if (typeof el.onclick === "function" || el.hasAttribute && el.hasAttribute("onclick")) return true;

          return false;
        } catch(e) {
          return false;
        }
      };

      const getLabel = el => {
        try {
          const id = el.getAttribute && el.getAttribute('id');
          if (id) {
            const byFor = document.querySelector(`label[for="${CSS.escape(id)}"]`);
            if (byFor) return normalize(byFor.innerText);
          }
          const wrapping = el.closest && el.closest('label');
          if (wrapping) return normalize(wrapping.innerText);
          const sib = el.parentElement && el.parentElement.querySelector && el.parentElement.querySelector('label');
          if (sib) return normalize(sib.innerText);
          const ariaLabel = el.getAttribute && el.getAttribute("aria-label");
          if (ariaLabel) return normalize(ariaLabel);
          const labelledBy = el.getAttribute && el.getAttribute("aria-labelledby");
          if (labelledBy) {
            const labelEl = document.getElementById(labelledBy);
            if (labelEl) return normalize(labelEl.innerText);
          }
          const title = el.getAttribute && el.getAttribute("title");
          if (title) return normalize(title);
        } catch(e) {}
        return "";
      };

      const getContext = el => {
        try {
          let node = el.closest && el.closest('fieldset, section, form, div');
          while (node) {
            const heading = node.querySelector && node.querySelector('legend,h1,h2,h3,h4,h5,h6');
            if (heading) return normalize(heading.innerText);
            node = node.parentElement;
          }
        } catch(e) {}
        return "";
      };

      const pickAttrs = el => {
        const attrs = {};
        try {
          const allow = ["id","name","type","placeholder","aria-label","title","href","value",
                        "data-testid","data-qa","data-test","data-cy","class"];
          for (const a of allow) {
            if (el.hasAttribute && el.hasAttribute(a)) {
              let v = el.getAttribute(a);
              // Keep values short for token safety
              if (v && v.length > 300) v = v.slice(0,300) + "...";
              attrs[a] = v;
            }
          }
        } catch(e) {}
        return attrs;
      };

      const textOf = el => {
        try {
          const raw = el.innerText || el.value || el.getAttribute && el.getAttribute("value") || "";
          return normalize(raw);
        } catch(e) { return ""; }
      };

      const pool = Array.from(document.querySelectorAll("*"));
      const items = [];
      for (const el of pool) {
        try {
          if (!isInteractable(el)) continue;
          items.push({
            tag: el.tagName.toLowerCase(),
            text: textOf(el),
            label: getLabel(el),
            context: getContext(el),
            attributes: pickAttrs(el)
          });
        } catch (err) { /* ignore element errors */ }
      }

      return (max && items.length > max) ? items.slice(0, max) : items;
    }
    """

    def __init__(self):
        load_dotenv()

        # Initialize Azure OpenAI client
        try:
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
        except Exception as e:
            # If client can't be created now, create lazily when needed
            self.client = None
            logger.warn(f"[Web Self-Healing] AzureOpenAI client init warning: {e}")

        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.browser = None

        # Track which keyword lines have already been healed in this test
        self._healed_keywords = set()

    # Reset per test so each test can heal once independently
    def start_test(self, data, result):
        self._healed_keywords = set()

    # Robot hook: called after each keyword
    def end_keyword(self, data, result):
        try:
            # Reset flag
            self._pending_yaml_variable = None
            self._is_yaml_variable = False

            if result.status != "FAIL" or not data.args:
                return

            locator = data.args[0]

            # Get raw locator BEFORE Robot variable expansion
            raw_locator = self._extract_raw_locator_from_robot_source(data)

            # Detect variable usage: ${locators.browse_link}
            if raw_locator and raw_locator.startswith("${") and raw_locator.endswith("}"):
                variable_name = raw_locator.strip("${}").strip()
                self._pending_yaml_variable = variable_name
                self._is_yaml_variable = True  # override guardrail

                logger.console(f"[Web Self-Healing] 📌 Variable locator detected: {variable_name}")

            # Guardrail: only treat actual locator failures
            # Always classify error type — even for YAML/Python variables
            reason = self._classify_error(result.message)
            logger.console(f"[Web Self-Healing] Failure Reason: {reason}")

            # Healing is ONLY allowed for true broken locators
            if reason != "BROKEN_LOCATOR":
                logger.console("[Web Self-Healing] ❌ Healing NOT allowed for this error type.")
                return

            logger.console(f"[Web Self-Healing] Failure Reason: {reason}")

            if reason != "BROKEN_LOCATOR":
                logger.console("[Web Self-Healing] ❌ Healing NOT allowed for this error type.")
                return

            key = (getattr(data, "source", ""), getattr(data, "lineno", 0))
            if key in self._healed_keywords:
                return
            self._healed_keywords.add(key)

            logger.warn(f"[Web Self-Healing] Locator failed: {locator}")

            self._attempt_self_heal(locator, data.name, data.args, result, data)

        except Exception as e:
            logger.error(f"[Web Self-Healing] end_keyword error: {e}")

    def _extract_raw_locator_from_robot_source(self, data):
        """Reads the .robot file line where the keyword was called and extracts raw locator."""
        try:
            if not data.source or not data.lineno:
                return None

            with open(data.source, "r", encoding="utf-8") as f:
                lines = f.readlines()

            line = lines[data.lineno - 1].strip()

            # Try to extract ${variable}
            m = re.search(r"(\$\{[A-Za-z0-9._]+\})", line)
            if m:
                return m.group(1)

            # Otherwise return the actual argument
            if data.args:
                return data.args[0]

        except Exception as e:
            logger.warn(f"[Web Self-Healing] Could not extract raw locator: {e}")

        return None

    def _get_yaml_value(self, variable_name):
        yaml_files = self._discover_yaml_files()
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            except:
                continue

            keys = variable_name.split(".")
            ref = data
            found = True

            for k in keys:
                if isinstance(ref, dict) and k in ref:
                    ref = ref[k]
                else:
                    found = False
                    break

            if found:
                return ref

        return None

    def _discover_yaml_files(self):
        yaml_files = []
        for root, dirs, files in os.walk(".", topdown=True):
            for f in files:
                if f.lower().endswith((".yml", ".yaml")):
                    yaml_files.append(os.path.join(root, f))
        return yaml_files

    def _update_yaml_variable(self, variable_name, new_locator):
        """
        SAFE YAML HEALING (Mode-B):
        - Preserves original locator style (no prefix, //, xpath=)
        - Only updates the exact YAML key when found
        - Prevents wrong-element healing
        """

        variable_name = variable_name.strip().lower()
        keys = variable_name.split(".")
        updated_any = False

        yaml_files = self._discover_yaml_files()

        if not yaml_files:
            logger.warn("[Web Self-Healing] ⚠ No YAML files found in project.")
            return False

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    yaml_data = yaml.safe_load(f)
            except Exception:
                continue

            if yaml_data is None:
                continue

            # Attempt recursive update with style-preservation
            changed, new_val = self._yaml_apply_update(yaml_data, keys, new_locator)
            # -------------------------------------------------------
            # FINAL ENFORCEMENT: Correct CSS Locator Format
            # -------------------------------------------------------
            if isinstance(new_val, str):
                v = new_val.strip()

                # Remove ANY accidental leading //  (your exact issue)
                if v.startswith("//css:"):
                    v = v[2:]

                # Convert css= to css:
                if v.startswith("css="):
                    v = "css:" + v[4:].strip()

                # Convert css:css= to css:
                if v.startswith("css:css="):
                    v = "css:" + v[len("css:css="):].strip()

                # If locator is CSS but missing css: prefix, enforce it
                # (detects patterns like button.x.y, .class, #id)
                if any(sym in v for sym in [".", "#"]) and not v.startswith(("css:", "xpath:")):
                    v = "css:" + v

                # Set final corrected value
                new_val = v

            if changed:
                # Save YAML
                try:
                    with open(yaml_file, "w", encoding="utf-8") as f:
                        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)

                    logger.console(
                        f"[Web Self-Healing] 🔧 YAML updated: {yaml_file}\n"
                        f"KEY: {variable_name}\n"
                        f"NEW VALUE: {new_val}"
                    )

                    updated_any = True

                except Exception as e:
                    logger.error(f"[Web Self-Healing] Failed to write YAML {yaml_file}: {e}")
                    return False

        if not updated_any:
            logger.warn(f"[Web Self-Healing] Variable '{variable_name}' NOT found in any YAML file.")
            return False

        return True

    # --------------------------------------------------------------------
    #                YAML UPDATE ENGINE (WITH STYLE PRESERVATION)
    # --------------------------------------------------------------------
    def _yaml_apply_update(self, yaml_data, keys, new_value):
        """
        Applies update into nested YAML dictionary.
        Ensures CSS prefixes are correct and NO accidental '//' is added.
        """

        # 1) Normalize healed locator ONCE
        new_value = self._normalize_healed_locator(new_value).strip()

        # 2) Fix Selenium style -> correct syntax
        if new_value.startswith("css="):
            new_value = "css:" + new_value[4:].strip()

        # 3) Remove duplicate css prefixes
        if new_value.startswith("css:css="):
            new_value = "css:" + new_value[len("css:css="):].strip()

        # 4) Remove accidental XPath prefix applied to CSS
        #    (the exact bug you reported: //css:button....)
        if new_value.startswith("//css:"):
            new_value = new_value[2:]  # Remove leading //

        # 5) Also remove triple-prefix case (rare but possible)
        if new_value.startswith("///css:"):
            new_value = new_value[3:]

        # 6) If value looks like CSS but missing prefix, add it
        if any(sym in new_value for sym in [".", "#"]) and not new_value.startswith(("css:", "xpath:")):
            if not new_value.startswith("//"):  # Avoid treating CSS as XPath
                new_value = "css:" + new_value

        # 7) If already a valid CSS selector, leave it EXACTLY AS IS
        if new_value.startswith("css:"):
            final_val = new_value
        else:
            final_val = new_value

        # --- WRITE VALUE INTO YAML STRUCTURE ---

        ptr = yaml_data
        for key in keys[:-1]:
            if key not in ptr or not isinstance(ptr[key], dict):
                return False, final_val
            ptr = ptr[key]

        last_key = keys[-1]

        if last_key not in ptr:
            return False, final_val

        # Quote CSS locator so YAML does not treat "css:" as a map key
        safe_val = final_val
        if safe_val.startswith("css:"):
            safe_val = f"\"{safe_val}\""
        # --- FINAL FIX: REMOVE accidental XPath prefix from CSS selectors ---
        # ALWAYS QUOTE CSS LOCATORS TO STOP YAML FROM TREATING THEM AS KEYS
        if new_value.startswith("css:"):
            ptr[last_key] = f'"{new_value}"'
        else:
            ptr[last_key] = new_value

        ptr[last_key] = safe_val
        return True, safe_val

    def _yaml_apply_update(self, node, keys, new_locator):
        """
        Recursive YAML update.
        ALWAYS RETURNS: (changed: bool, final_value: str|None)
        """

        # YAML must be a dictionary
        if not isinstance(node, dict):
            return False, None

        key = keys[0]

        if key not in node:
            return False, None

        # ----------------------------
        # FINAL KEY → apply update
        # ----------------------------
        if len(keys) == 1:

            old_value = node[key]

            # Only update string values
            if not isinstance(old_value, str):
                return False, None

            old_str = old_value.strip().strip('"').strip("'")

            # Strip prefixes like xpath= , id=, css=
            def strip_prefix(x):
                for p in ["xpath=", "css=", "id=", "name="]:
                    if x.lower().startswith(p):
                        return x[len(p):]
                return x

            # Detect original styling
            had_prefix_xpath = old_str.lower().startswith("xpath=")
            had_double_slash = old_str.startswith("//")
            had_no_prefix = not (had_prefix_xpath or had_double_slash)

            raw = strip_prefix(new_locator)

            # Apply SAME STYLE as original YAML value
            if had_no_prefix:
                final = raw

            elif had_double_slash:
                if raw.startswith("//"):
                    final = raw
                else:
                    final = "//" + raw.lstrip("/")

            elif had_prefix_xpath:
                if raw.startswith("//"):
                    final = "xpath=" + raw
                else:
                    final = "xpath=//" + raw.lstrip("/")

            else:
                final = new_locator  # fallback

            # No update needed
            if final == old_str:
                return False, old_str

            # Apply update
            node[key] = final
            return True, final

        # ----------------------------
        # NOT FINAL KEY → recurse deeper
        # ----------------------------
        return self._yaml_apply_update(node[key], keys[1:], new_locator)

    def _detect_popup(self, driver):
        """
        Detect common popup patterns:
        - Cookie/consent banners
        - Modals
        - Interstitial overlays
        """

        POPUP_XPATHS = [
            "//*[contains(@class,'consent')]",
            "//*[contains(@class,'cookie')]",
            "//*[contains(@id,'cookie')]",
            "//*[contains(@class,'popup')]",
            "//*[contains(@class,'modal')]",
            "//*[contains(@role,'dialog')]",
            "//*[contains(@class,'overlay')]",
            "//*[contains(@style,'position: fixed')]"
        ]

        for xp in POPUP_XPATHS:
            els = driver.find_elements(By.XPATH, xp)
            if els:
                return els[0]

        return None

    def _dismiss_popup(self, driver):
        """
        Try multiple strategies to dismiss a popup:
        - Click close/accept button
        - Press ESC
        - Remove via JS (last resort)
        """

        # Close button keywords
        BUTTON_XPATHS = [
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'accept')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'agree')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ok')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'close')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'dismiss')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'got it')]",
            "//a[contains(.,'close')]",
        ]

        # Attempt to click popup button
        for xp in BUTTON_XPATHS:
            btns = driver.find_elements(By.XPATH, xp)
            if btns:
                try:
                    btns[0].click()
                    time.sleep(1)
                    return True
                except:
                    pass

        # Try pressing ESC
        try:
            driver.execute_script("document.activeElement.blur();")
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
        except:
            pass

        # LAST RESORT: Remove popup via JS
        try:
            driver.execute_script("""
                let els = document.querySelectorAll('*');
                els.forEach(e => {
                    const s = getComputedStyle(e);
                    if (s.position == 'fixed' && s.zIndex >= 100) {
                        e.remove();
                    }
                });
            """)
            time.sleep(0.5)
            return True
        except:
            pass

        return False

    # Simple check whether the first argument looks like a locator
    def _is_locator(self, arg):
        """Always treat short plain text (<= 3 words) as healable locators."""
        if not isinstance(arg, str):
            return False

        arg = arg.strip()
        if not arg:
            return False

        # Real locator formats
        if arg.startswith(("xpath=", "//", "css=", "id=", "name=")):
            return True

        # NEW: Treat ANY short plain text as locator-like (to enable healing)
        if len(arg.split()) <= 3:
            return True

        return False

    def _classify_error(self, error_message):
        """
        Classifies failure reasons so we can decide if healing is allowed.
        Returns one of:
        - 'BROKEN_LOCATOR'
        - 'CLICK_ISSUE'
        - 'PAGE_ISSUE'
        - 'ASSERTION'
        - 'OTHER'
        """

        msg = (error_message or "").lower()
        # --------------------------------------------
        # FORCE HEALING FOR PLAIN-TEXT LOCATORS
        # Example: "Browse", "Firefox", "Address Bar"
        # --------------------------------------------
        # --------------------------------------------
        # FORCE HEALING FOR PLAIN-TEXT LOCATORS
        # Example: "Address Bar", "Browse Now", "Firefox Beta"
        # --------------------------------------------
        if self._pending_yaml_variable:
            yaml_val = self._get_yaml_value(self._pending_yaml_variable)

            # If YAML value is plain text AND contains a space AND is NOT xpath/css/id
            if yaml_val and " " in yaml_val and not any(
                    sym in yaml_val for sym in ["//", "xpath=", "css=", "id=", "name="]):
                return "BROKEN_LOCATOR"

        # ----- BROKEN LOCATOR -----
        broken_patterns = [
            "not found",  # <--- FIX HERE
            "element not found",
            "no such element",
            "unable to locate",
            "did not match any elements",
            "invalid selector",
            "invalid xpath",
            "invalid css selector",
            "unable to find element",
            "did not match exactly one element",
            "not found because"
            "syntaxerror",
            "invalid xpath",
            "not a valid xpath expression",
            "invalid selector"
            "invalid element state",
            "element not interactable",

        ]

        if any(p in msg for p in broken_patterns):
            return "BROKEN_LOCATOR"

        # ----- CLICK ISSUES -----
        click_patterns = [
            "not clickable",
            "element is not clickable",
            "other element would receive the click",
            "element obscured",
            "intercepted click",
            "element is not interactable",
            "is disabled"
        ]
        if any(p in msg for p in click_patterns):
            return "CLICK_ISSUE"

        # ----- PAGE LOAD / NETWORK ISSUES -----
        page_patterns = [
            "timeout",
            "page load",
            "navigation",
            "connection refused",
            "net::",
            "timed out"
        ]
        if any(p in msg for p in page_patterns):
            return "PAGE_ISSUE"

        # ----- ASSERTION FAILURES -----
        if "assert" in msg or "should be" in msg or "expected" in msg:
            return "ASSERTION"

        # ----- OTHER -----
        return "OTHER"

    def _find_clickable_parent(self, keyword):
        """
        Find the nearest clickable parent for the given text.
        Supports:
          - <a>
          - <button>
          - Amazon's <div class="nav-a">
          - role="link"
          - elements with cursor:pointer
        """

        try:
            selenium_lib = BuiltIn().get_library_instance("SeleniumLibrary")
            driver = selenium_lib.driver

            xpath = f"//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]"
            nodes = driver.find_elements(By.XPATH, xpath)

            for node in nodes:
                parent = node
                for _ in range(6):  # walk up max 6 levels
                    parent = parent.find_element(By.XPATH, "..")
                    tag = parent.tag_name.lower()

                    # Clickable tag
                    if tag in ["a", "button"]:
                        return parent

                    # Amazon classes
                    class_attr = parent.get_attribute("class") or ""
                    if any(c in class_attr for c in [
                        "nav-a", "nav-hasPanel", "nav-link", "a-link-normal", "a-declarative"
                    ]):
                        return parent

                    # ARIA roles
                    role = parent.get_attribute("role") or ""
                    if role in ["link", "button"]:
                        return parent

                    # Display + pointer cursor
                    style = (parent.get_attribute("style") or "").lower()
                    if "cursor: pointer" in style or "cursor:pointer" in style:
                        return parent

        except Exception as e:
            pass

        return None

    def _is_text_present_in_dom(self, keyword):
        try:
            script = """
                var walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    {
                        acceptNode: function(node) {
                            if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
                            let el = node.parentElement;
                            if (!el) return NodeFilter.FILTER_REJECT;
                            let style = window.getComputedStyle(el);
                            if (style &&
                                (style.visibility === 'hidden' ||
                                 style.display === 'none' ||
                                 parseFloat(style.opacity || '1') === 0)) {
                                return NodeFilter.FILTER_REJECT;
                            }
                            return NodeFilter.FILTER_ACCEPT;
                        }
                    }
                );
                var text = "";
                while (walker.nextNode()) {
                    text += " " + walker.currentNode.nodeValue;
                }
                return text;
            """
            visible_text = self.browser.execute_script(script)
            return keyword.lower() in (visible_text or "").lower()
        except Exception:
            return False

    def _is_text_on_page_but_not_clickable(self, keyword, interactables):
        keyword = (keyword or "").lower().strip()
        if not keyword:
            return False

        in_dom = self._is_text_present_in_dom(keyword)

        in_clickables = False
        for item in interactables:
            text = (item.get("text") or "").lower()
            if keyword in text:
                in_clickables = True
                break

        # Present somewhere in visible DOM, but not in any clickable element
        return in_dom and not in_clickables

    def _should_attempt_healing(self, failed_locator, interactables):
        """
        Decide if healing should be attempted.

        Healing is allowed ONLY when:
          - the keyword matches a clickable DOM element (text or attributes)
          - OR fuzzy match repairs malformed ID/XPath/CSS (generic input-safe rule)
          - AND locator is not unrelated garbage
          - AND not classified as NON_CLICKABLE earlier
        """

        locator = failed_locator.lower().strip()

        # Normalize "xpath = value"
        locator = re.sub(r"\s*=\s*", "=", locator)

        # ------------------------
        # 1. Extract keyword (contains(...) or raw value)
        # ------------------------
        m = re.search(r"contains\([^,]+,\s*['\"](.+?)['\"]\)", locator)
        keyword = m.group(1).strip().lower() if m else ""

        if not keyword:
            raw = locator
            for prefix in ("xpath=", "css=", "id=", "name="):
                if raw.startswith(prefix):
                    raw = raw[len(prefix):]
                    break

            raw = raw.strip("/[]()@ '\"")
            if 3 <= len(raw) <= 40:
                keyword = raw.lower()

        # No valid keyword → no healing
        if not keyword or len(keyword) < 3:
            return False

        # ------------------------
        # 2. Visible DOM text (cached earlier)
        # ------------------------
        try:
            dom_text = (self._visible_dom_text or "").lower()
        except:
            dom_text = ""

        # ------------------------
        # 3. Similarity helper with adaptive thresholds
        # ------------------------
        def similar_match(a, b):
            a = a.lower().strip()
            b = b.lower().strip()
            n = len(a)

            if n <= 2:
                return False
            similar_match
            # Short words → stricter, long → forgiving
            if n <= 4:
                threshold = 0.95
            elif n <= 8:
                threshold = 0.90
            else:
                threshold = 0.75

            return difflib.SequenceMatcher(None, a, b).ratio() >= threshold

        # ------------------------
        # 4. Check clickable interactables
        # ------------------------
        for item in interactables:
            text = (item.get("text") or "").lower().strip()
            label = (item.get("label") or "").lower().strip()
            context = (item.get("context") or "").lower().strip()

            # Full match
            if similar_match(keyword, text) or similar_match(keyword, label) or similar_match(keyword, context):
                return True

            # Word-level match
            for w in re.findall(r"[a-zA-Z0-9]+", text + " " + label + " " + context):
                if similar_match(keyword, w):
                    return True

        # ------------------------
        # 5. DOM text + clickable parent logic
        # ------------------------
        if keyword in dom_text or any(similar_match(keyword, w) for w in re.findall(r"[a-zA-Z0-9]+", dom_text)):
            parent = self._find_clickable_parent(keyword)
            if parent:
                return True
            else:
                return False  # text exists but not clickable → don't heal

        # ---------------------------------------------------------------------
        # 6. NEW GENERIC FUZZY INPUT-ID REPAIR LOGIC
        #
        # Fixes ALL malformed id/xpath/css like:
        #   id=searchtextbox → id=twotabsearchtextbox
        #   id=twotabsearchtexbo → id=twotabsearchtextbox
        #   id=srchtextbx → id=searchtextbox
        #
        # Works on ANY website (no hardcoded values)
        # ---------------------------------------------------------------------
        for prefix in ["xpath=", "id=", "css=", "name="]:
            if locator.startswith(prefix):
                raw_keyword = locator[len(prefix):].strip().lower()

                # skip too small or too large
                if not (3 <= len(raw_keyword) <= 50):
                    break

                # *** ONLY MATCH REAL <input> FIELDS ***
                for item in interactables:

                    if item.get("tag", "").lower() != "input":
                        continue  # do NOT compare with <a>, <div>, etc.

                    attrs = item.get("attributes") or {}
                    candidates = []

                    if "id" in attrs: candidates.append(attrs["id"].lower())
                    if "name" in attrs: candidates.append(attrs["name"].lower())
                    if "placeholder" in attrs: candidates.append(attrs["placeholder"].lower())
                    if "aria-label" in attrs: candidates.append(attrs["aria-label"].lower())

                    for cand in candidates:

                        # Adaptive threshold based on text length
                        L = max(len(raw_keyword), len(cand))
                        if L >= 15:
                            threshold = 0.45  # very forgiving for long IDs
                        elif L >= 10:
                            threshold = 0.55
                        elif L >= 6:
                            threshold = 0.62
                        else:
                            threshold = 0.70  # strict for short ones

                        score = difflib.SequenceMatcher(None, raw_keyword, cand).ratio()

                        if score >= threshold:
                            return True  # accept fuzzy match

                break  # stop prefix loop

        # ------------------------
        # 7. Otherwise → no healing
        # ------------------------
        return False

    def _verify_click_effect(self):
        """
        Detect UI change after clicking:
        - cart popup
        - toast/snackbar
        - DOM changes
        - button disappears
        """
        try:
            driver = BuiltIn().get_library_instance("SeleniumLibrary").driver

            # A) Toast/snackbar/pop-up
            if driver.find_elements(By.XPATH, "//*[contains(@class,'toast') or contains(@class,'snackbar')]"):
                return True

            # B) Detect "added to cart" action on Flipkart
            if driver.find_elements(By.XPATH, "//*[contains(text(),'added to')]"):
                return True

            # C) Button disappears (common Flipkart behavior)
            if not driver.find_elements(By.XPATH, "//button[contains(.,'ADD TO CART')]"):
                return True

            return False
        except:
            return False

    def _pick_best_suggestion(self, keyword, suggestions, interactables):
        """
        Rank LLM suggestions by semantic similarity to interactable text.
        Returns the most relevant locator instead of blindly picking the first one.
        """

        keyword = keyword.lower().strip()
        best_choice = None
        best_score = 0.0

        for locator in suggestions:
            locator_l = locator.lower()
            local_best = 0

            # Score this locator by checking similarity to all clickable texts on page
            for item in interactables:
                text = (item.get("text") or "").lower()

                # Full-string similarity
                score = difflib.SequenceMatcher(None, keyword, text).ratio()
                if score > local_best:
                    local_best = score

                # Per-word similarity
                for w in re.findall(r"[a-zA-Z0-9]+", text):
                    score2 = difflib.SequenceMatcher(None, keyword, w).ratio()
                    if score2 > local_best:
                        local_best = score2

            # Keep highest scoring locator
            if local_best > best_score:
                best_score = local_best
                best_choice = locator

        # Fallback: if for some weird reason nothing matched
        return best_choice or suggestions[0]

    def _is_yaml_locator_actually_broken(self, locator_value):
        """
        FIXED VERSION — works for both YAML & Python variable files.
        Any plain text locator (like 'Address Bar') is considered BROKEN.
        Only true locator formats (xpath/css/id/name) are validated by Selenium.
        """

        # Empty or non-string values are broken
        if not isinstance(locator_value, str) or locator_value.strip() == "":
            return True

        val = locator_value.strip()

        # If locator does NOT start with known locator prefixes → it is plain text
        is_plain_text = not any(
            val.lower().startswith(prefix)
            for prefix in ("xpath=", "//", "css=", "id=", "name=")
        )

        # Plain text locators should ALWAYS be healed
        if is_plain_text:
            return True

        # Attempt Selenium validation ONLY if it LOOKS like a real locator
        try:
            selenium_lib = BuiltIn().get_library_instance("SeleniumLibrary")
            selenium_lib.find_element(locator_value)
            return False  # found = valid
        except Exception as e:
            msg = str(e).lower()

            # typical broken patterns
            if "invalid" in msg or "not found" in msg or "syntax" in msg:
                return True

            # clickable problems mean element exists but is not interactable
            if "intercept" in msg or "not interactable" in msg:
                return False

            return True  # safe fallback

    def _normalize_healed_locator(self, locator):
        loc = locator.strip()

        # Already normalized
        if loc.startswith(("css:", "xpath:", "id:", "name:")):
            return loc

        # Convert Selenium style to unified style
        if loc.startswith("css="):
            return "css:" + loc[4:].strip()
        if loc.startswith("xpath="):
            return "xpath:" + loc[6:].strip()

        # CSS detection (contains . or # and is NOT XPath)
        if any(sym in loc for sym in [".", "#"]) and not loc.startswith("//"):
            return "css:" + loc

        # Raw XPath
        if loc.startswith("//"):
            return "xpath:" + loc

        return loc

    def _attempt_self_heal(self, failed_locator, keyword_name, args, result, data):
        # 1. Selenium driver
        try:
            selenium_lib = BuiltIn().get_library_instance("SeleniumLibrary")
            self.browser = selenium_lib.driver
        except Exception as e:
            logger.error(f"[Web Self-Healing] Cannot access Selenium driver: {e}")
            return

        # 2. DOM extraction
        try:
            small_dom = self._get_relevant_dom(failed_locator)
            if not small_dom:
                full = self.browser.page_source or ""
                small_dom = full[:4000] + ("... [TRUNCATED]" if len(full) > 4000 else "")
        except Exception:
            small_dom = ""

        # 3. Interactables extraction
        try:
            interactables = self._get_interactables(max_items=200)
        except:
            interactables = []

        # ---------------------------------------------------
        # 4. Determine intended meaning from YAML/Python
        # ---------------------------------------------------
        # ---------------------------------------------------
        # 4. Determine intended meaning from YAML/Python
        # ---------------------------------------------------
        intended_text = None

        if self._pending_yaml_variable:
            varname = self._pending_yaml_variable

            yaml_val = self._get_yaml_value(varname)
            py_val = self._get_python_value(varname)

            raw = yaml_val or py_val
            if raw and isinstance(raw, str):
                raw = raw.strip()

                # --- 1. Remove locator prefixes ---
                for p in ["xpath=", "css=", "id=", "name="]:
                    if raw.lower().startswith(p):
                        raw = raw[len(p):].strip()

                # --- 2. Extract literal text inside XPath ---
                import re

                # matches text()='Something'
                m1 = re.findall(r"text\(\)\s*=\s*['\"]([^'\"]+)['\"]", raw)

                # matches contains(text(), 'Something')  OR contains(., 'Something')
                m2 = re.findall(r"contains\([^,]+,\s*['\"]([^'\"]+)['\"]\)", raw)

                extracted = None
                if m1:
                    extracted = m1[0]
                elif m2:
                    extracted = m2[0]

                if extracted:
                    intended_text = extracted.strip()
                else:
                    # fallback: treat only last word-like token as intended meaning
                    # so that raw xpath becomes "mobiletablet" and not entire xpath fragment
                    tokens = re.findall(r"[a-zA-Z0-9]+", raw)
                    intended_text = tokens[-1].lower().strip() if tokens else raw.strip()

        # ---------------------------------------------------
        # 5. If variable: DO NOT SKIP HEAL CHECK ANYMORE
        #    (Fix: enforce intended-text fuzzy validation)
        # ---------------------------------------------------

        if self._pending_yaml_variable and intended_text:

            intended_l = intended_text.lower()
            found = False

            # ---- FUNC: fuzzy match ----
            def similar_match(a, b):
                a = a.lower().strip()
                b = b.lower().strip()
                n = len(a)

                if n <= 2:
                    return False
                if n <= 4:
                    threshold = 0.95
                elif n <= 8:
                    threshold = 0.90
                else:
                    threshold = 0.75

                return difflib.SequenceMatcher(None, a, b).ratio() >= threshold

            # -------- A) Check interactables fuzzy --------
            for item in interactables:
                for field in ["text", "label", "context"]:
                    value = (item.get(field) or "").lower().strip()
                    if value and similar_match(intended_l, value):
                        found = True
                        break
                if found:
                    break

            # -------- B) Check DOM visible text fuzzy --------
            if not found:
                try:
                    dom_text = self.browser.execute_script(
                        "return document.body.innerText.toLowerCase();"
                    )
                    words = re.findall(r"[a-zA-Z0-9]+", dom_text or "")
                    for w in words:
                        if similar_match(intended_l, w):
                            found = True
                            break
                except:
                    pass

            # -------- C) Block wrong healing --------
            # ------------------------------------------
            # C) Enhanced fuzzy + clickable validation
            # ------------------------------------------

            matched_fuzzily = False
            matched_clickable = False

            # A) Check interactables → clickable elements
            for item in interactables:
                for field in ["text", "label", "context"]:
                    value = (item.get(field) or "").lower().strip()
                    if value and similar_match(intended_l, value):
                        matched_fuzzily = True
                        matched_clickable = True
                        break
                if matched_clickable:
                    break

            # B) Check DOM text → but requires clickable parent
            if not matched_clickable:
                try:
                    dom_text = self.browser.execute_script(
                        "return document.body.innerText.toLowerCase();"
                    )
                    words = re.findall(r"[a-zA-Z0-9]+", dom_text or "")
                    for w in words:
                        if similar_match(intended_l, w):
                            matched_fuzzily = True

                            # Find clickable parent
                            clickable_parent = self._find_clickable_parent(w)
                            if clickable_parent:
                                matched_clickable = True
                            break
                except:
                    pass

            # C1) If no fuzzy match anywhere → block healing
            if not matched_fuzzily:
                logger.console(
                    f"[Web Self-Healing] 🛑 Healing BLOCKED: Intended text '{intended_text}' "
                    f"not found anywhere on the page."
                )
                return

            # C2) If fuzzy match exists but NOT clickable → block healing
            if not matched_clickable:
                logger.console(
                    f"[Web Self-Healing] 🛑 Healing BLOCKED: Intended text '{intended_text}' "
                    f"exists but is NOT associated with any clickable element."
                )
                return

            # C3) Otherwise → healing allowed
            logger.console(
                f"[Web Self-Healing] 🟢 Intended text '{intended_text}' matched AND clickable → healing allowed."
            )

        # ---------------------------------------------------
        # 6. Build prompt for LLM
        # ---------------------------------------------------
        prompt = self._build_prompt(
            failed_locator, small_dom, interactables, intended_text=intended_text
        )

        try:
            if not self.client:
                self.client = AzureOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01"),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                )

            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            locators = self._extract_locators(response)
        except Exception as e:
            logger.error(f"[Web Self-Healing] Azure OpenAI error: {e}")
            return

        if not locators:
            logger.error("[Web Self-Healing] ❌ No suggestions from LLM.")
            return

        # ---------------------------------------------------
        # 7. Multi-suggestion validation
        # ---------------------------------------------------
        locator_list = self._pick_best_suggestion_list(
            failed_locator, locators, interactables
        )

        valid_locator = None

        for suggested_locator in locator_list:
            logger.console(f"[Web Self-Healing] 🔍 Trying healed locator: {suggested_locator}")

            # Validate suggested locator
            try:
                el = selenium_lib.find_element(suggested_locator)

                if not el.is_displayed():
                    logger.console(f"[Web Self-Healing] ❌ Rejected (not visible): {suggested_locator}")
                    continue

                if not el.is_enabled():
                    logger.console(f"[Web Self-Healing] ❌ Rejected (not enabled): {suggested_locator}")
                    continue

            except Exception as e:
                logger.console(f"[Web Self-Healing] ❌ Invalid healed locator: {suggested_locator} | {e}")
                continue

            valid_locator = suggested_locator
            break

        if not valid_locator:
            logger.console("[Web Self-Healing] ❌ All suggestions invalid — cannot heal.")
            return

        # ---------------------------------------------------
        # 8. Update YAML/PY file
        # ---------------------------------------------------
        if self._pending_yaml_variable:
            varname = self._pending_yaml_variable

            # Normalize CSS/XPath prefix BEFORE saving
            normalized = self._normalize_healed_locator(valid_locator)

            yaml_updated = self._update_yaml_variable(varname, normalized)
            py_updated = self._update_python_variable(varname, normalized)

            if yaml_updated or py_updated:
                logger.console(f"[Web Self-Healing] 🟢 Variable healed: {varname}")

                try:
                    BuiltIn().set_test_variable(f"${{{varname}}}", valid_locator)
                except:
                    pass

                try:
                    selenium_lib.click_element(valid_locator)
                    logger.console(f"[Web Self-Healing] ✅ Clicked healed locator: {valid_locator}")
                    result.status = "PASS"
                except Exception as e:
                    logger.error(f"[Web Self-Healing] ❌ Failed to click healed locator: {e}")
                return

        # ---------------------------------------------------
        # 9. Normal non-variable healing path
        # ---------------------------------------------------
        if self._try_locator(valid_locator, keyword_name, args, result, data):
            logger.console(f"[Web Self-Healing] ✅ Healed using: {valid_locator}")
            return

        logger.error("[Web Self-Healing] ❌ Healing failed.")

    def _pick_best_suggestion_list(self, failed_locator, locators, interactables):
        """
        Return ALL locator suggestions sorted by similarity score.
        Highest score first.
        This allows healing to try multiple suggestions in order.

        Example output:
        [
            "id=twotabsearchtextbox",
            "xpath=//input[@name='field-keywords']",
            "id=nav-assist-search",
            ...
        ]
        """
        scored = []

        for loc in locators:
            try:
                score = self._score_similarity(failed_locator, loc, interactables)
            except Exception:
                score = 0
            scored.append((score, loc))

        # Sort descending by score
        scored.sort(key=lambda x: x[0], reverse=True)

        # Return only locator list
        return [loc for score, loc in scored]

    # Execute JS in browser to gather interactable elements
    # -----------------------------
    def _get_interactables(self, max_items=150):
        if not self.browser:
            return []
        try:
            # Build a safe JS call that returns the array
            # We pass an options object {strict:false, max: max_items}
            script = f"return ({self.JS_GATHER_INTERACTABLES})({{strict:false, max:{int(max_items)}}});"
            result = self.browser.execute_script(script)
            # Selenium will convert basic JS objects to Python dict/list
            if isinstance(result, list):
                # sanitize each item: trim long strings
                cleaned = []
                for it in result:
                    if not isinstance(it, dict):
                        continue
                    # Shorten large text/labels/context/attrs for token safety
                    text = (it.get("text") or "")[:500]
                    label = (it.get("label") or "")[:300]
                    context = (it.get("context") or "")[:300]
                    attrs = it.get("attributes") or {}
                    # shrink attribute values
                    for k, v in list(attrs.items()):
                        if isinstance(v, str) and len(v) > 300:
                            attrs[k] = v[:300] + "..."

                    cleaned.append({
                        "tag": it.get("tag"),
                        "text": text,
                        "label": label,
                        "context": context,
                        "attributes": attrs
                    })
                return cleaned
        except Exception as e:
            logger.warn(f"[Web Self-Healing] Interactable JS failed: {e}")
        return []

    # -----------------------------
    # Extract a small DOM snippet relevant to the failed locator
    # -----------------------------
    def _get_relevant_dom(self, locator):
        """
        Execute a JS snippet that tries to find elements similar to the failed locator
        and returns their outerHTML (limited and sanitized). Works with:
         - xpath=...
         - css=...
         - id=...
         - name=...
         - raw xpath starting with //
        """
        js = r"""
        function extract(locator) {
            function outerList(nodes) {
                const out = [];
                for (let i = 0; i < nodes.length && out.length < 8; i++) {
                    try {
                        const n = nodes[i];
                        if (!n) continue;
                        // ensure visible-ish elements only
                        const style = window.getComputedStyle(n);
                        if (style && (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0')) continue;
                        out.push(n.outerHTML);
                    } catch(e) {}
                }
                return out;
            }

            let results = [];
            try {
                if (locator.startsWith('xpath=')) {
                    const xp = locator.substring(6);
                    const res = document.evaluate(xp, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                    const nodes = [];
                    for (let i=0;i<res.snapshotLength;i++) nodes.push(res.snapshotItem(i));
                    results = outerList(nodes);
                } else if (locator.startsWith('//')) {
                    const xp = locator;
                    const res = document.evaluate(xp, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                    const nodes = [];
                    for (let i=0;i<res.snapshotLength;i++) nodes.push(res.snapshotItem(i));
                    results = outerList(nodes);
                } else if (locator.startsWith('css=')) {
                    const sel = locator.substring(4);
                    const nodes = document.querySelectorAll(sel);
                    results = outerList(Array.from(nodes));
                } else if (locator.startsWith('id=')) {
                    const id = locator.substring(3);
                    const el = document.getElementById(id);
                    if (el) results = [el.outerHTML];
                } else if (locator.startsWith('name=')) {
                    const name = locator.substring(5);
                    const nList = document.getElementsByName(name);
                    results = outerList(Array.from(nList));
                } else {
                    // Try treating locator as CSS first
                    try {
                        const nodes = document.querySelectorAll(locator);
                        if (nodes.length) results = outerList(Array.from(nodes));
                    } catch(e) {}
                }
            } catch(e) {}

            // If nothing found, pick several visible clickable elements as fallback
            if (results.length === 0) {
                const fallback = Array.from(document.querySelectorAll("button, a, [role='button'], input[type='button'], input[type='submit']"));
                results = outerList(fallback);
            }
            return results;
        }
        return extract(arguments[0]);
        """

        try:
            nodes = self.browser.execute_script(js, locator)
            if not nodes:
                return ""
            # Join and sanitize, truncate each node and overall length
            pieces = []
            total = 0
            for n in nodes:
                s = str(n)
                # strip scripts/styles accidentally included
                s = re.sub(r'<script[\s\S]*?</script>', '', s, flags=re.I)
                s = re.sub(r'<style[\s\S]*?</style>', '', s, flags=re.I)
                # limit per node
                if len(s) > 3000:
                    s = s[:3000] + "...[TRUNCATED]"
                pieces.append(s)
                total += len(s)
                if total > 10000:
                    break
            joined = "\n\n".join(pieces)
            # final truncate
            if len(joined) > 12000:
                joined = joined[:12000] + "...[TRUNCATED]"
            return joined
        except Exception as e:
            logger.warn(f"[Web Self-Healing] get_relevant_dom exception: {e}")

            return ""

    def _discover_python_locator_files(self):
        py_files = []
        for root, dirs, files in os.walk(".", topdown=True):
            for f in files:
                if f.lower().endswith(".py") and "locator" in f.lower():
                    py_files.append(os.path.join(root, f))
        return py_files

    def _get_python_value(self, variable_name):
        files = self._discover_python_locator_files()

        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    for line in f:
                        m = re.match(rf"\s*{variable_name}\s*=\s*['\"](.+?)['\"]", line)
                        if m:
                            return m.group(1)
            except:
                pass
        return None

    def _update_python_variable(self, variable_name, new_locator):
        files = self._discover_python_locator_files()
        updated = False

        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                changed = False
                new_lines = []
                for line in lines:
                    if re.match(rf"\s*{variable_name}\s*=", line):
                        new_line = f"{variable_name} = \"{new_locator}\"\n"
                        changed = True
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)

                if changed:
                    with open(file, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)

                    logger.console(
                        f"[Web Self-Healing] 🔧 PY updated: {file}\n"
                        f"KEY: {variable_name}\nNEW VALUE: {new_locator}"
                    )

                    updated = True

            except Exception as e:
                logger.error(f"[Web Self-Healing] Could not update PY file {file}: {e}")

        return updated

    # Build a compact, token-safe prompt for the LLM (now accepts interactables)
    def _build_prompt(self, failed_locator, small_dom, interactables, intended_text=None):
        """
        Build a compact but strongly-guided prompt for the LLM.
        intended_text = the human-meaning of the locator (extracted from YAML or Python file)
        """

        sanitized_dom = (small_dom or "").replace("\r", " ").replace("\n", " ")
        if len(sanitized_dom) > 9000:
            sanitized_dom = sanitized_dom[:9000] + "...[TRUNCATED]"

        try:
            interactables_slice = interactables[:30] if interactables else []
            interactables_json = json.dumps(interactables_slice, indent=2, ensure_ascii=False)
        except Exception:
            interactables_json = "[]"

        intended_clause = ""
        if intended_text:
            intended_clause = f"""
    The intended meaning of this locator is EXACTLY:
        ** "{intended_text}" **

    You MUST select a locator matching THAT meaning.
    Do NOT pick random branding elements such as:
     - Flipkart logo
     - Site-wide branding text
     - Header labels
     - Title attributes like @title='Flipkart'
     - aria-label='Flipkart'
    These are INVALID suggestions.

    Only choose locators that match the TEXT / LABEL / Clickable element associated with:
        "{intended_text}"

    If the DOM uses similar or shorter/longer versions of this text, you MAY use contains(), normalize-space(), etc.
    """

        prompt = f"""
    The following web locator FAILED:
    {failed_locator}

    {intended_clause}

    Below is a SMALL DOM snippet of candidate elements (outerHTML) near the target:
    {sanitized_dom}

    Here are some INTERACTABLE elements extracted from the live page (first {min(30, len(interactables or []))} items):
    {interactables_json}

    TASK:
    Return EXACTLY 3 alternative locators (best first) that are most likely to locate the SAME intended element.
    You MUST return ONLY a JSON array of 3 strings:
    ["xpath=...", "css=...", "id=..."]

    Rules:
    - The locator MUST match the intended meaning, NOT branding elements.
    - Prefer clickable parent elements (<a>, <button>) if the text is inside spans.
    - Prefer id, name, aria-label, data-* when stable.
    - Avoid logo/title/branding-based nodes.
    - Avoid generic contains(@*, 'Flipkart').
    - Keep XPaths short & robust.
    - Return no commentary, only JSON.
    """

        return prompt

    # Parse LLM response for locator strings (tries JSON array first)
    def _extract_locators(self, response):
        try:
            # response shape for AzureOpenAI chat completions may vary
            # support common shapes
            content = None
            if hasattr(response, "choices") and response.choices:
                # choices can be objects with message or text
                first = response.choices[0]
                if hasattr(first, "message") and first.message:
                    content = first.message.get("content") if isinstance(first.message, dict) else getattr(first.message, "content", None)
                elif hasattr(first, "text"):
                    content = first.text
            if not content:
                # try dict-like access
                try:
                    content = response["choices"][0]["message"]["content"]
                except Exception:
                    content = str(response)
        except Exception:
            content = str(response)

        content = (content or "").strip()

        # First try to find a JSON array in the response
        json_match = re.search(r"\[.*\]", content, flags=re.S)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, list):
                    return [p.strip() for p in parsed if isinstance(p, str)]
            except Exception:
                pass

        # fallback: extract lines containing locator patterns
        locators = []
        for line in content.splitlines():
            line = line.strip(" -•\t\"'")
            if any(x in line for x in ["xpath=", "css=", "id=", "name="]):
                # attempt to clean trailing punctuation
                cleaned = line.split(";")[0].strip()
                locators.append(cleaned)
        # final sanitize/truncate to 3
        return locators[:3]

    def _try_locator(self, locator, keyword_name, args, original_result, data):
        """
        Try to heal using the suggested locator.

        Improvements added:
          - Validates locator BEFORE clicking:
              • Must exist
              • Must be visible
              • Must be enabled
              • If keyword is input-type → must be an <input> or <textarea>
          - Rejects Amazon hidden locators like id=nav-assist-search
          - Only updates YAML AFTER a valid healed locator is confirmed
          - Uses JS click fallback

        Returns:
          True  -> healing succeeded
          False -> healing failed
        """
        try:
            selenium_lib = BuiltIn().get_library_instance("SeleniumLibrary")
        except Exception as e:
            logger.warn(f"[Web Self-Healing] Could not get SeleniumLibrary: {e}")
            return False

        keyword_lower = (keyword_name or "").lower()
        is_click_keyword = "click" in keyword_lower or "press" in keyword_lower
        is_input_keyword = any(
            x in keyword_lower
            for x in ["input", "type", "text", "keys", "press", "search"]
        )

        # ----------------------------------------------------------------------
        # VALIDATE ELEMENT BEFORE CLICKING
        # ----------------------------------------------------------------------
        try:
            web_el = selenium_lib.find_element(locator)
        except Exception as e:
            logger.console(f"[Web Self-Healing] ❌ Healed locator invalid: {locator} | {e}")
            return False

        # Element exists, now verify interactability
        try:
            if not web_el.is_displayed():
                logger.console(f"[Web Self-Healing] ❌ Rejected locator (not visible): {locator}")
                return False

            if not web_el.is_enabled():
                logger.console(f"[Web Self-Healing] ❌ Rejected locator (not enabled): {locator}")
                return False

            # Input keyword must match input field
            if is_input_keyword:
                tag = web_el.tag_name.lower()
                if tag not in ["input", "textarea"]:
                    logger.console(f"[Web Self-Healing] ❌ Rejected locator (not input field): {locator}")
                    return False
        except Exception as e:
            logger.console(f"[Web Self-Healing] ❌ Failed interactability check: {locator} | {e}")
            return False

        # ----------------------------------------------------------------------
        # CLICK FLOW
        # ----------------------------------------------------------------------
        if is_click_keyword:
            logger.info(f"[Web Self-Healing] Trying JS click for: {locator}")
            try:
                driver = selenium_lib.driver

                # Scroll into view
                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center', inline:'center'});",
                        web_el
                    )
                except Exception as se:
                    logger.warn(f"[Web Self-Healing] scrollIntoView failed: {se}")

                # Try JS click
                try:
                    driver.execute_script("arguments[0].click();", web_el)
                except Exception as ce:
                    logger.warn(f"[Web Self-Healing] JS click failed: {ce}")
                    # Selenium fallback
                    try:
                        selenium_lib.click_element(locator)
                    except Exception as ce2:
                        logger.warn(f"[Web Self-Healing] Selenium click failed: {ce2}")
                        return False

                # SUCCESS
                original_result.status = "PASS"
                original_result.message = f"Healed with JS click: {locator}"

                # Update Robot file after confirming success
                try:
                    self._update_robot_file(data, args[0], locator)
                except Exception as e:
                    logger.warn(f"[Web Self-Healing] Could not update robot file: {e}")

                return True

            except Exception as e:
                logger.warn(f"[Web Self-Healing] Click flow failed for '{locator}': {e}")
                return False

        # ----------------------------------------------------------------------
        # NON-CLICK KEYWORDS (input, type, etc.)
        # ----------------------------------------------------------------------
        try:
            new_args = list(args)
            new_args[0] = locator

            status, message = BuiltIn().run_keyword_and_ignore_error(
                keyword_name, *new_args
            )

            if status == "PASS":
                original_result.status = "PASS"
                original_result.message = f"Healed locator used: {locator}"

                try:
                    self._update_robot_file(data, args[0], locator)
                except Exception as e:
                    logger.warn(f"[Web Self-Healing] Could not update robot file: {e}")

                return True

            logger.warn(f"[Web Self-Healing] Retry with healed locator failed: {message}")
            return False

        except Exception as e:
            logger.warn(f"[Web Self-Healing] Retry exception: {e}")
            return False

    # Update the robot test file to replace old locator with new locator (best-effort)
    def _update_robot_file(self, data, old_locator, new_locator):
        try:
            file_path = data.source
            line_no = data.lineno - 1

            if not file_path or not os.path.exists(file_path):
                logger.warn("[Web Self-Healing] Robot file not found or path missing.")
                return

            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if line_no < 0 or line_no >= len(lines):
                logger.warn("[Web Self-Healing] Line number out of range.")
                return

            original_line = lines[line_no]
            if old_locator not in original_line:
                # Try a relaxed replace (escape and search)
                escaped_old = re.escape(old_locator)
                if re.search(escaped_old, original_line):
                    updated_line = re.sub(escaped_old, new_locator, original_line)
                else:
                    logger.warn("[Web Self-Healing] Old locator not found in exact line.")
                    return
            else:
                updated_line = original_line.replace(old_locator, new_locator)

            lines[line_no] = updated_line
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

            logger.console(f"[Web Self-Healing] ✅ Robot file updated: {file_path}")
            logger.console(f"OLD: {original_line.strip()}")
            logger.console(f"NEW: {updated_line.strip()}")

        except Exception as e:
            logger.error(f"[Web Self-Healing] File update failed: {e}")


# Important: expose listener instance for Robot to load
listener = SelfHealingWebListener()