from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

def create_search_query(summoner_name):
    return "https://eune.op.gg/summoner/userName={}".format(summoner_name.replace(" ","+"))

def get_html_code_from_summoner(summoner_name):
    outfile = open("html_files/"+summoner_name+".html","w+")
    path = "/Users/christianpederjacobsen/.wdm/drivers/chromedriver/mac64/92.0.4515.107/chromedriver"
    driver = webdriver.Chrome(path)
    url = create_search_query(summoner_name)
    driver.get(url)
    
    try:
        element = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.CLASS_NAME, "qc-cmp2-summary-buttons"))
        )
        driver.find_element_by_xpath("//*[@id=\"qc-cmp2-ui\"]/div[2]/div/button[2]").click()
    finally:
        # Load more games button
        driver.find_element_by_xpath("//*[@id=\"SummonerLayoutContent\"]/div[2]/div[2]/div/div[2]/div[4]").click()
        time.sleep(5)
        expand_knapper = driver.find_elements_by_xpath('//*[@id="right_match"]')
        for knap in expand_knapper:
            driver.execute_script("arguments[0].click();", knap)
        time.sleep(7)
        print(driver.page_source,file=outfile)
        driver.quit()





if __name__ == "__main__":
    # get_html_code_from_summoner("Hoobz")
    pass
    

