from openai import OpenAI
from Listeners.logger_settings import ai_logger
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException, TimeoutException
from utility import ReadConfigFile

class Healenium:
    def __init__(self, driver):
        self.driver = driver

    @staticmethod
    def __suggest_path_with_llm(by_locator, html, element_description):
        client = OpenAI(api_key=ReadConfigFile.ReadConfig.get_api_key_ai('API_KEY'))
        prompt = f"""
        You are a Selenium automation expert.

        A user is trying to locate a web element described as:
        "{element_description}"

        They want to use the following locator type: {by_locator}

        Below is the current HTML of the page:{html}
        🔧 Your task:
        - Suggest **only** the best possible **value** for the specified locator type ({by_locator})
        - Ensure the value is accurate and uniquely identifies the element
        - ❌ Do not include any explanation
        - ❌ Do not return By.{by_locator}, just return the **locator value as a plain string**
        
        ✅ Example Output (if {by_locator} was name):
        login_button
        
        Your response:
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            print(response)
            return response.choices[0].message.content.strip()
        except Exception as e:
            print("[❌] Error calling GPT-4o:", e)

    def find_element_with_llm(self, by_locator, path, description):
        try:
            return self.driver.find_element(by_locator, path)
        except (NoSuchElementException, InvalidSelectorException, TimeoutException) as e:
            if hasattr(e, 'msg'):    # Clean log message
                msg = e.msg.split("\n")[0]
            else:
                msg = str(e).split("\n")[0]
            ai_logger.error(msg)
            print(f"Path failed: {path}")

            html = self.driver.page_source
            new_path = self.__suggest_path_with_llm(by_locator, html, description)
            clean_path = new_path.strip("`") # Remove surrounding backticks if they exist
            ai_logger.info(f"LLM generated Path: {clean_path}")
            print(f"LLM suggested Path: {clean_path}")
            try:
                return clean_path
            except Exception as e:
                ai_logger.error(clean_path)
                print(f"Still failed: {e}")
                return None
