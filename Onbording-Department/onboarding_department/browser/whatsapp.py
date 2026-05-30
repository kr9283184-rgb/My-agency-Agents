from typing import Optional


class WhatsAppAutomation:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._page = None

    def send_message(self, phone_number: str, message: str) -> bool:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    storage_state="whatsapp_storage.json"
                    if self._storage_exists()
                    else None
                )
                page = context.new_page()
                page.goto("https://web.whatsapp.com")

                if not self._storage_exists():
                    input("Scan QR code and press Enter to continue...")
                    context.storage_state(path="whatsapp_storage.json")

                encoded_phone = phone_number.replace("+", "").replace(" ", "")
                page.goto(f"https://web.whatsapp.com/send?phone={encoded_phone}")
                page.wait_for_timeout(3000)

                message_box = page.locator("div[contenteditable='true'][data-tab='10']")
                message_box.wait_for(timeout=10000)
                message_box.click()
                page.keyboard.type(message, delay=50)
                page.keyboard.press("Enter")

                page.wait_for_timeout(1000)
                browser.close()

            return True
        except Exception as e:
            print(f"[WhatsAppAutomation] Failed to send message to {phone_number}: {e}")
            return False

    def send_template(self, phone_number: str, template_name: str, params: dict) -> bool:
        message = self._render_template(template_name, params)
        return self.send_message(phone_number, message)

    def _render_template(self, template_name: str, params: dict) -> str:
        templates = {
            "welcome": (
                "Hi {contact_name},\n\n"
                "Welcome to the team! We're excited to start working together. "
                "Your onboarding process has officially begun. "
                "We'll be sending you details via email shortly.\n\n"
                "Let's get started!"
            ),
            "kickoff": (
                "Hi {contact_name},\n\n"
                "Heads up — your project is now in the planning phase. "
                "We'll keep you updated every step of the way. "
                "Stay tuned for updates!"
            ),
        }
        template = templates.get(template_name, "")
        if template and params:
            template = template.format(**params)
        return template

    def _storage_exists(self) -> bool:
        import os
        return os.path.isfile("whatsapp_storage.json")
