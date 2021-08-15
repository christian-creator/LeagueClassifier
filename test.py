from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

path = "/Users/christianpederjacobsen/.wdm/drivers/chromedriver/mac64/92.0.4515.107/chromedriver"
driver = webdriver.Chrome(path)
driver.get("https://eune.op.gg/summoner/userName=2Jacks1Shaco")
outfile = open("2Jacks1Shaco.html","w+")
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "qc-cmp2-summary-buttons"))
    )
    driver.find_element_by_xpath("//*[@id=\"qc-cmp2-ui\"]/div[2]/div/button[2]").click()
    # Clicking the expand button
    driver.find_element_by_xpath("//*[@id=\"SummonerLayoutContent\"]/div[2]/div[2]/div/div[2]/div[4]").click()
    time.sleep(10)
    expand_knapper = driver.find_elements_by_xpath('//*[@id="right_match"]')
    print(len(expand_knapper))
    for knap in expand_knapper:
        driver.execute_script("arguments[0].click();", knap)
        # knap.click()
    print("Alle knapper trykket")
    time.sleep(10)
finally:
    print(driver.page_source,file=outfile)
    driver.quit()


