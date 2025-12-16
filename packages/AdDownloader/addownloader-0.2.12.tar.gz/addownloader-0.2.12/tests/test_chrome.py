from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from AdDownloader.helpers import update_access_token
from AdDownloader.media_download import accept_cookies
import pandas as pd

access_token = input() # your fb-access-token-here
data_path = 'output/test1/ads_data/test1_processed_data.xlsx'
data = pd.read_excel(data_path)
data = update_access_token(data = data, new_access_token = access_token)

chrome_opts = Options()
chrome_opts.add_argument("--disable-gpu")
chrome_opts.add_argument("--no-sandbox")        # needed on some locked-down hosts

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_opts,
)

driver.get(data['ad_snapshot_url'][6009]) # start from here to accept cookies
accept_cookies(driver)

shadow_host = driver.find_element(By.CSS_SELECTOR, "div[data-testid='cookie-policy-manage-dialog']")
shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
allow_btn = shadow_root.find_element(By.XPATH, ".//div[@role='button' and @aria-label='Allow all cookies']")
allow_btn.click()