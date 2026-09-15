from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import logging
from main import get_agent_response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_driver():
    session_path = os.path.join(os.getcwd(), "whatsapp_session")
    options = Options()
    options.add_argument(f"user-data-dir={session_path}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://web.whatsapp.com")
    return driver


def wait_for_whatsapp_load(driver, timeout=30):
    logger.info("Waiting for WhatsApp Web to load (scan QR if needed)...")
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#pane-side"))
    )
    logger.info("WhatsApp Web loaded successfully.")


def get_unread_chats(driver):
    return driver.find_elements(
        By.XPATH, '//span[contains(@aria-label, "unread message")]/ancestor::div[@role="row"]'
    )


def get_chat_title(driver):
    try:
        header = driver.find_element(By.XPATH, '//header')
        title_span = header.find_element(By.XPATH, './/span[@dir="auto"]')
        return title_span.text
    except Exception:
        return "unknown_customer"


def get_last_message_text(driver):
    messages = driver.find_elements(By.CSS_SELECTOR, '[data-testid="selectable-text"]')
    return messages[-1].text if messages else None


def send_reply(driver, reply_text):
    reply_text = reply_text.replace("\n", " ")
    input_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
    )
    input_box.send_keys(reply_text)
    input_box.send_keys(u'\ue007')


def process_next_chat(driver, last_seen_per_customer, last_bot_reply_per_customer):
    # Pehle unread chats check karo, agar hain to kholo
    unread_chats = get_unread_chats(driver)

    if unread_chats:
        chat = unread_chats[0]
        try:
            ActionChains(driver).move_to_element(chat).click().perform()
            time.sleep(3)
        except Exception as e:
            logger.warning(f"Failed to click unread chat: {e}")
            return False

    # Chahe unread thi ya already khuli hai - current open chat check karo
    try:
        chat_title = get_chat_title(driver)
        last_message = get_last_message_text(driver)

        if not last_message:
            return bool(unread_chats)

        # Agar ye humara khud ka bheja hua reply hai, skip karo
        if last_message == last_bot_reply_per_customer.get(chat_title):
            return bool(unread_chats)

        # Agar ye message pehle process ho chuka hai, skip karo
        if last_seen_per_customer.get(chat_title) == last_message:
            return bool(unread_chats)

        last_seen_per_customer[chat_title] = last_message
        logger.info(f"Customer ({chat_title}): {last_message}")

        reply = get_agent_response(last_message, chat_title)
        send_reply(driver, reply)

        last_bot_reply_per_customer[chat_title] = reply.replace("\n", " ")
        logger.info(f"Bot to {chat_title}: {reply}")

    except Exception as chat_error:
        logger.warning(f"Failed to process chat: {chat_error}")

    return True


def run_bot():
    driver = setup_driver()

    try:
        wait_for_whatsapp_load(driver)
    except Exception:
        logger.error("WhatsApp Web load nahi hua. QR scan karke script dobara chalayein.")
        driver.quit()
        return

    logger.info("Bot is running, monitoring messages...")
    last_seen_per_customer = {}
    last_bot_reply_per_customer = {}

    while True:
        try:
            had_work = process_next_chat(driver, last_seen_per_customer, last_bot_reply_per_customer)
            time.sleep(2 if had_work else 3)

        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
            break

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(5)

    driver.quit()


if __name__ == "__main__":
    run_bot()