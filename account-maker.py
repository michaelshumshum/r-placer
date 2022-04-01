from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import util
import time
import sheets

while True:
    try:
        email = util.random_string() + '@yopmail.com'
        username = util.random_letters()
        password = util.random_string()

        options = webdriver.ChromeOptions()
        #options.headless = True
        options.add_extension('/Users/shum/Desktop/projects/reddit-place-bot/extension_1_3_1_0.crx')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0')

        driver = webdriver.Chrome(executable_path='/Users/shum/Desktop/projects/reddit-place-bot/chromedriver', options=options)

        def send_keys_better(element, text):
            for t in text:
                element.send_keys(t)
                time.sleep(0.1)

        driver.implicitly_wait(5)
        driver.get('https://www.reddit.com/')
        driver.find_element_by_xpath('//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div[1]/header/div/div[2]/div/div[1]/a[2]').click()
        driver.switch_to_frame(driver.find_element_by_css_selector('iframe[src^="https://www.reddit.com/register"]'))

        email_input = driver.find_element_by_id('regEmail')
        send_keys_better(email_input, email)
        time.sleep(0.5)
        email_input.submit()
        time.sleep(0.5)
        send_keys_better(driver.find_element_by_id('regUsername'), username)
        time.sleep(0.5)
        password_input = driver.find_element_by_id('regPassword')
        send_keys_better(password_input, password)
        time.sleep(0.5)
        driver.switch_to_frame(driver.find_element_by_css_selector('iframe[src^="https://www.google.com/recaptcha/api2/anchor?"]'))
        driver.find_element_by_xpath('//span[@id="recaptcha-anchor"]').click()
        driver.switch_to.parent_frame()
        driver.switch_to_frame(driver.find_element_by_css_selector('iframe[src^="https://www.google.com/recaptcha/api2/bframe?"]'))
        driver.find_element_by_xpath('//*[@id="rc-imageselect"]/div[3]/div[2]/div[1]/div[1]/div[4]').click()
        time.sleep(7)
        driver.switch_to.parent_frame()
        time.sleep(0.5)
        driver.find_element_by_xpath('/html/body/div[1]/main/div[2]/div/div/div[3]/button').click()
        driver.find_element_by_xpath('/html/body/div[1]/main/div[2]/div/div/div[3]/button').click()
        sheets.add([email, username, password])
        time.sleep(5)
        driver.quit()
        time.sleep(300)
    except:
        driver.quit()
        continue
