import unittest
import json
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By

ORIGINAL_URL = 'https://en.wikipedia.org/wiki/Software_metric'
CYCLES = 10

class TestPerformanceMetrics(unittest.TestCase):

    def setUp(self):
        """Set up the test variables."""
        self.url = ORIGINAL_URL
        self.cycles = CYCLES

    def test_performance(self):
        """Test performance by measuring resource load times."""
        raw_data = defaultdict(list)

        for cycle in range(self.cycles):
            print(f"Cycle {cycle + 1}/{self.cycles}")
            options = webdriver.ChromeOptions()
            options.add_argument("--incognito")

            try:
                driver = webdriver.Chrome(options=options)
                driver.get(self.url)

                # Verify page title contains expected text
                title_element = driver.find_element(By.CSS_SELECTOR, "#firstHeading > span")
                self.assertIn('Software metric', title_element.text)

                # Collect performance data using JavaScript
                performance_script = (
                    "return window.performance.getEntries().map(entry => [entry.name, entry.duration]);"
                )
                performance_data = driver.execute_script(performance_script)

                for resource_name, duration in performance_data:
                    raw_data[resource_name].append(duration)

            except Exception as e:
                self.fail(f"An error occurred during the test: {e}")

            finally:
                driver.quit()

        # Save raw data to JSON
        self._save_json("map.json", raw_data)

        # Process data to calculate averages
        processed_data = self._process_data(raw_data)

        # Save processed data to JSON
        self._save_json("processedMap.json", processed_data)

    def _process_data(self, raw_data):
        """Process raw data to compute average durations."""
        processed_data = defaultdict(list)

        for resource_name, durations in raw_data.items():
            non_zero_durations = [duration for duration in durations if duration > 0]
            average_duration = (
                sum(non_zero_durations) / len(non_zero_durations)
                if non_zero_durations
                else 0
            )
            processed_data[resource_name] = average_duration

        return processed_data

    @staticmethod
    def _save_json(file_name, data):
        """Save data to a JSON file."""
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    def tearDown(self):
        """Clean up after the test."""
        print("Test completed.")

if __name__ == "__main__":
    unittest.main()
