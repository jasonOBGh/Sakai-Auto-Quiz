"""
Sakai Quiz Bot — MAIN BOT (Groq AI)
Handles: single/multi question pages, radio + checkbox questions,
         stale elements, iframe ghosting, human-like delays, fuzzy matching
"""

import time
import random
import os
from groq import Groq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()
LOGIN_URL    = "https://sakai.ug.edu.gh/portal/site/!gateway/tool/55840c0d-ea44-4827-84cb-5270d764ecf7"
USERNAME     = os.getenv("USERNAME")
PASSWORD     = os.getenv("PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

QUIZ_PAGES = [
    {"title": "MATH 233", "url": "https://sakai.ug.edu.gh/portal/site/MATH-223-1-S1-2526/tool/4d3cad86-206e-49a6-9ac5-af1c111da079/jsf/index/mainIndex"},
    {"title": "DCIT 203", "url": "https://sakai.ug.edu.gh/portal/site/DCIT-203-1-S1-2526/tool/8d6a8e4a-0b8a-45da-8532-1f3f442fcfaa/jsf/index/mainIndex"},
    {"title": "DCIT 211", "url": "https://sakai.ug.edu.gh/portal/site/DCIT-211-1-S1-2526/tool/de8c3576-7bc2-4ffc-b69a-b40087140fbd/jsf/index/mainIndex"},
    {"title": "DCIT 201", "url": "https://sakai.ug.edu.gh/portal/site/DCIT-201-1-S1-2526/tool/fb5150aa-059f-4c47-87eb-08f99c508a85/jsf/index/mainIndex"},
    {"title": "DCIT 207", "url": "https://sakai.ug.edu.gh/portal/site/DCIT-207-1-S1-2526/tool/e3b9d77f-eaa9-45ae-a40a-4214a54bfaef/jsf/index/mainIndex"},
]


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def human_delay(min_s=2.0, max_s=5.0):
    time.sleep(random.uniform(min_s, max_s))


def fuzzy_match(best, label_text):
    """Check if AI answer matches a label (case-insensitive, ignores extra spaces)."""
    return best.strip().lower() in label_text.strip().lower()


def get_ai_answer(client, question, choices, multi=False):
    """Ask Groq to pick the best answer(s). multi=True allows multiple selections."""
    choices_text = "\n".join(f"{i+1}. {c}" for i, c in enumerate(choices))
    if multi:
        prompt = (
            f"You are answering a quiz question. This is a 'select all that apply' question.\n\n"
            f"Question: {question}\n\nChoices:\n{choices_text}\n\n"
            f"Reply with ONLY the numbers of ALL correct choices separated by commas (e.g. '1,3'). No explanation."
        )
    else:
        prompt = (
            f"You are answering a quiz question. Pick the single best answer.\n\n"
            f"Question: {question}\n\nChoices:\n{choices_text}\n\n"
            f"Reply with ONLY the number of the correct choice (e.g. '2'). No explanation."
        )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20
    )
    raw = response.choices[0].message.content.strip()

    if multi:
        # Parse comma-separated numbers like "1,3"
        selected = []
        for part in raw.replace(" ", "").split(","):
            for char in part:
                if char.isdigit():
                    idx = int(char) - 1
                    if 0 <= idx < len(choices):
                        selected.append(choices[idx])
                    break
        return selected if selected else [choices[0]]
    else:
        for char in raw:
            if char.isdigit():
                idx = int(char) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
        return choices[0]


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    # Uncomment below line once fully tested to run without browser window:
    # options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def safe_switch_iframe(driver, retries=3):
    for attempt in range(retries):
        try:
            driver.switch_to.default_content()
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src") or ""
                iid = iframe.get_attribute("id") or ""
                if any(k in src for k in ["samigo", "jsf", "tool", "sakai"]) or "Main" in iid or "tool" in iid.lower():
                    driver.switch_to.frame(iframe)
                    return True
            if iframes:
                driver.switch_to.frame(iframes[0])
                return True
        except Exception:
            time.sleep(1)
    return False


# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────

def login(driver, wait):
    print("[*] Logging in...")
    driver.get(LOGIN_URL)

    try:
        wait.until(EC.presence_of_element_located((By.ID, "eid")))
    except Exception:
        print("[!] Login page didn't load. Please log in manually.")
        input("Press Enter once logged in...")
        return

    time.sleep(1)
    eid = driver.find_element(By.ID, "eid")
    pw  = driver.find_element(By.ID, "pw")
    eid.clear()
    pw.clear()
    eid.send_keys(USERNAME)
    time.sleep(random.uniform(0.3, 0.7))
    pw.send_keys(PASSWORD)
    time.sleep(random.uniform(0.3, 0.7))

    clicked = False
    for sel in [
        (By.ID, "submit"),
        (By.XPATH, "//input[@value='Login']"),
        (By.XPATH, "//input[@value='Log In']"),
        (By.CSS_SELECTOR, "input[type='submit']"),
        (By.CSS_SELECTOR, "button[type='submit']"),
    ]:
        try:
            driver.find_element(*sel).click()
            clicked = True
            print("[+] Clicked login button.")
            break
        except Exception:
            continue

    if not clicked:
        print("[!] Could not find login button — please click manually.")
        input("Press Enter once logged in...")
        return

    print("[*] Waiting for login...")
    for i in range(20):
        time.sleep(1)
        if "Home" in driver.title or "Overview" in driver.title:
            print(f"[+] Logged in! Page: {driver.title}")
            return
        if i % 5 == 4:
            print(f"  [{i+1}s] Still waiting... ({driver.title})")

    print(f"[!] Login timed out. Page: {driver.title}")
    input("If logged in press Enter, otherwise log in manually first...")


# ─────────────────────────────────────────────
#  QUESTION ANSWERING
# ─────────────────────────────────────────────

def scrape_and_answer_block(driver, block, client):
    """Answer a single question block. Handles both radio and checkbox questions."""
    try:
        # Get question text
        q_text = ""
        for xpath in [
            ".//div[contains(@class,'itemText')]",
            ".//div[contains(@class,'questionText')]",
            ".//div[contains(@class,'shortAnswerText')]",
            ".//h3", ".//span[contains(@class,'text')]",
        ]:
            try:
                q_text = block.find_element(By.XPATH, xpath).text.strip()
                if q_text:
                    break
            except Exception:
                continue
        if not q_text:
            q_text = block.text.split("\n")[0].strip()
        if not q_text or len(q_text) < 5:
            return False

        # Detect question type: radio or checkbox
        radios    = block.find_elements(By.XPATH, ".//input[@type='radio']")
        checkboxes = block.find_elements(By.XPATH, ".//input[@type='checkbox']")
        is_multi  = len(checkboxes) > 0 and len(radios) == 0
        inputs    = checkboxes if is_multi else radios

        if not inputs:
            return False

        # Get labels using fuzzy approach
        choices = []
        for inp in inputs:
            try:
                rid = inp.get_attribute("id")
                label = driver.find_element(By.XPATH, f"//label[@for='{rid}']")
                choices.append(label.text.strip())
            except Exception:
                val = inp.get_attribute("value") or ""
                if val:
                    choices.append(val)
        choices = [c for c in choices if c]
        if not choices:
            return False

        q_type = "checkbox (select all that apply)" if is_multi else "radio (single choice)"
        print(f"\n    Q [{q_type}]: {q_text[:120]}")
        print(f"    Options: {choices}")

        human_delay(2.0, 5.0)

        if is_multi:
            best_list = get_ai_answer(client, q_text, choices, multi=True)
            print(f"    → Groq picked: {best_list}")
            for i, inp in enumerate(inputs):
                if i < len(choices) and any(fuzzy_match(b, choices[i]) for b in best_list):
                    driver.execute_script("arguments[0].click();", inp)
        else:
            best = get_ai_answer(client, q_text, choices, multi=False)
            print(f"    → Groq picked: '{best}'")
            for i, inp in enumerate(inputs):
                if i < len(choices) and fuzzy_match(best, choices[i]):
                    driver.execute_script("arguments[0].click();", inp)
                    break

        return True

    except StaleElementReferenceException:
        print("    [!] Stale element — will retry after iframe re-enter.")
    except Exception as e:
        print(f"    [!] Error: {e}")
    return False


def answer_all_questions(driver, wait, client):
    """Loop through all questions — handles both single-page and paginated layouts."""
    answered  = 0
    page      = 0
    max_pages = 100

    while page < max_pages:
        page += 1
        time.sleep(1.5)

        # Always re-enter iframe at start of each page (prevents ghosting)
        safe_switch_iframe(driver)
        time.sleep(1)

        # Try block-based (all questions on one page)
        question_blocks = []
        for xpath in [
            "//div[contains(@class,'tier1')]",
            "//div[@class='question']",
            "//div[contains(@class,'questionBlock')]",
            "//div[contains(@class,'multipleChoice')]",
            "//div[contains(@class,'shortAnswer')]",
            "//table[.//input[@type='radio']]",
            "//div[.//input[@type='radio']]",
            "//div[.//input[@type='checkbox']]",
        ]:
            question_blocks = driver.find_elements(By.XPATH, xpath)
            if question_blocks:
                break

        if question_blocks:
            print(f"\n  [page {page}] {len(question_blocks)} question block(s) found.")
            for block in question_blocks:
                try:
                    if scrape_and_answer_block(driver, block, client):
                        answered += 1
                except StaleElementReferenceException:
                    safe_switch_iframe(driver)
                    print("    [!] Stale block — re-entered iframe.")
        else:
            # Single question layout
            q_text  = ""
            choices = []
            inputs  = []
            is_multi = False

            for xpath in [
                "//*[contains(@class,'questionText')]",
                "//*[contains(@class,'itemText')]",
                "//*[contains(@class,'shortAnswerText')]",
            ]:
                try:
                    q_text = driver.find_element(By.XPATH, xpath).text.strip()
                    if q_text:
                        break
                except Exception:
                    continue

            radios     = driver.find_elements(By.XPATH, ".//input[@type='radio']")
            checkboxes = driver.find_elements(By.XPATH, ".//input[@type='checkbox']")
            is_multi   = len(checkboxes) > 0 and len(radios) == 0
            inputs     = checkboxes if is_multi else radios

            for inp in inputs:
                try:
                    label = driver.find_element(By.XPATH, f"//label[@for='{inp.get_attribute('id')}']")
                    choices.append(label.text.strip())
                except Exception:
                    val = inp.get_attribute("value") or ""
                    if val:
                        choices.append(val)
            choices = [c for c in choices if c]

            if q_text and choices:
                print(f"\n  [page {page}] Q: {q_text[:100]}")
                print(f"  Options: {choices}")
                human_delay(2.0, 5.0)

                if is_multi:
                    best_list = get_ai_answer(client, q_text, choices, multi=True)
                    print(f"  → Groq picked: {best_list}")
                    for i, inp in enumerate(inputs):
                        if i < len(choices) and any(fuzzy_match(b, choices[i]) for b in best_list):
                            driver.execute_script("arguments[0].click();", inp)
                    answered += 1
                else:
                    best = get_ai_answer(client, q_text, choices, multi=False)
                    print(f"  → Groq picked: '{best}'")
                    for i, inp in enumerate(inputs):
                        if i < len(choices) and fuzzy_match(best, choices[i]):
                            driver.execute_script("arguments[0].click();", inp)
                            answered += 1
                            break
            else:
                print(f"  [page {page}] No question found.")

        human_delay(0.5, 1.5)

        # Check for Submit button
        submitted = False
        for btn_text in ["Submit for Grading", "Submit Assessment", "Submit Quiz"]:
            try:
                btn = driver.find_element(By.XPATH,
                    f"//input[@value='{btn_text}'] | //button[contains(text(),'{btn_text}')]"
                )
                if btn.is_displayed():
                    human_delay(1.0, 2.0)
                    btn.click()
                    submitted = True
                    print(f"\n  [+] Submitted!")
                    time.sleep(2)
                    try:
                        confirm = wait.until(EC.element_to_be_clickable((By.XPATH,
                            "//input[@value='Submit'] | //button[text()='OK'] | //button[text()='Yes']"
                        )))
                        confirm.click()
                        print("  [+] Confirmed.")
                    except Exception:
                        pass
                    break
            except Exception:
                continue

        if submitted:
            break

        # Click Next
        clicked_next = False
        for next_text in ["Next", "Next Item", "Next Page"]:
            try:
                next_btn = driver.find_element(By.XPATH,
                    f"//input[@value='{next_text}'] | //button[normalize-space()='{next_text}']"
                )
                if next_btn.is_displayed():
                    next_btn.click()
                    clicked_next = True
                    human_delay(1.0, 2.0)
                    break
            except Exception:
                continue

        if not clicked_next and not submitted:
            print(f"  [!] No Next or Submit found on page {page}. Done.")
            break

    print(f"\n  [✓] Answered {answered} question(s) total.")
    return answered


# ─────────────────────────────────────────────
#  COURSE NAVIGATION
# ─────────────────────────────────────────────

def answer_quiz_page(driver, wait, client, quiz_url, quiz_title):
    print(f"\n{'='*55}")
    print(f"[*] Course: {quiz_title}")
    print(f"{'='*55}")

    driver.get(quiz_url)
    time.sleep(4)
    driver.switch_to.default_content()
    safe_switch_iframe(driver)
    time.sleep(2)

    iframe_text = driver.find_element(By.TAG_NAME, "body").text

    if "There are currently no assessments available" in iframe_text:
        print(f"  [!] No quizzes available for {quiz_title}.")
        driver.switch_to.default_content()
        return

    if "currently available for you to take" not in iframe_text:
        print(f"  [!] No available assessments for {quiz_title}.")
        driver.switch_to.default_content()
        return

    print(f"  [+] Quiz available! Finding link...")

    skip_words = ['Tests & Quizzes', 'Title', 'Time Limit', 'Due Date', 'Previous',
                  'Next', 'Display', 'Search', 'Submitted', 'Statistics', 'View All',
                  'View Only', 'UG Website', 'MIS', 'Copyright']

    all_links = driver.find_elements(By.TAG_NAME, "a")
    best_link = None
    for link in all_links:
        text = link.text.strip()
        href = link.get_attribute("href") or ""
        if not text or not href or len(text) < 2:
            continue
        if any(w.lower() == text.lower() for w in skip_words):
            continue
        if any(w in text.lower() for w in ["quiz", "test", "exam", "assessment"]):
            best_link = {"title": text, "element": link}
            break
    if not best_link:
        for link in all_links:
            text = link.text.strip()
            href = link.get_attribute("href") or ""
            if text and href and len(text) > 2 and not any(w.lower() == text.lower() for w in skip_words):
                best_link = {"title": text, "element": link}
                break

    if not best_link:
        print("  [!] Could not find quiz link — please click manually!")
        driver.switch_to.default_content()
        input("  Press Enter once quiz questions are visible...")
        safe_switch_iframe(driver)
        answer_all_questions(driver, wait, client)
        driver.switch_to.default_content()
        return

    print(f"  --> Clicking: '{best_link['title']}'")
    try:
        best_link["element"].click()
    except Exception:
        pass
    time.sleep(3)

    driver.switch_to.default_content()
    safe_switch_iframe(driver)
    time.sleep(2)

    # Honor pledge checkbox
    try:
        pledge = driver.find_element(By.XPATH, "//input[@type='checkbox']")
        if not pledge.is_selected():
            pledge.click()
            print("  [+] Checked honor pledge.")
        time.sleep(0.5)
    except Exception:
        pass

    # Begin Assessment
    for btn_text in ["Begin Assessment", "Start Quiz", "Take Quiz", "Begin", "Start"]:
        try:
            btn = driver.find_element(By.XPATH,
                f"//input[@value='{btn_text}'] | //button[contains(text(),'{btn_text}')]"
            )
            btn.click()
            print(f"  [+] Clicked '{btn_text}'")
            time.sleep(3)
            driver.switch_to.default_content()
            safe_switch_iframe(driver)
            time.sleep(2)
            break
        except Exception:
            continue

    answer_all_questions(driver, wait, client)
    driver.switch_to.default_content()


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    print("=" * 55)
    print("   Sakai Quiz Bot (Groq AI) — Starting")
    print("=" * 55)

    if not USERNAME or not PASSWORD or not GROQ_API_KEY:
        print("[!] Missing credentials! Make sure your .env file exists with:")
        print("    USERNAME=your_id")
        print("    PASSWORD=your_password")
        print("    GROQ_API_KEY=your_key")
        return

    client = Groq(api_key=GROQ_API_KEY)
    driver = init_driver()
    wait   = WebDriverWait(driver, 15)

    try:
        login(driver, wait)
        time.sleep(2)

        for course in QUIZ_PAGES:
            answer_quiz_page(driver, wait, client, course["url"], course["title"])

        print("\n[✓] All courses processed!")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        input("\nPress Enter to close the browser...")
        driver.quit()


if __name__ == "__main__":
    main()