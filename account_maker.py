from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from random import choice
import _config
import util
import time
import sheets

subs = [
    'gaming',
    'csgo',
    'memes',
    'tf2',
    'askreddit',
    'abruptchaos',
    'perfectlycutscreams',
    'askouija',
    'apple',
    'linux',
    'pcmasterrace',
    'clashroyale',
    'minecraft',
    'cursed_comments',
    'cringetopia',
    'shitposting'
]

while True:
    try:
        email = _config.config['account-maker-email']
        username = util.random_letters()
        password = util.random_string()
        options = webdriver.ChromeOptions()
        # options.headless = True #disabled for testing
        options.add_extension('extension_1_3_1_0.crx')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0')

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        def send_keys_better(element, text):  # to avoid automation detection. if you type it instantly, recaptcha detects it.
            for t in text:
                element.send_keys(t)
                time.sleep(0.1)

        driver.implicitly_wait(20)
        driver.get('http://httpbin.org/ip')
        driver.get('https://www.reddit.com/register/')
        email_input = driver.find_element_by_id('regEmail')
        send_keys_better(email_input, email)
        time.sleep(0.5)
        email_input.submit()
        time.sleep(1)
        username_btn = driver.find_element_by_xpath('/html/body/div/main/div[2]/div/div/div[2]/div[2]/div/div/a[1]')
        username = username_btn.text
        username_btn.click()
        time.sleep(1)
        password_input = driver.find_element_by_id('regPassword')
        send_keys_better(password_input, password)
        time.sleep(0.5)
        driver.switch_to_frame(driver.find_element_by_css_selector('iframe[src^="https://www.google.com/recaptcha/api2/anchor?"]'))
        driver.find_element_by_xpath('//span[@id="recaptcha-anchor"]').click()
        driver.switch_to.parent_frame()
        driver.switch_to_frame(driver.find_element_by_css_selector('iframe[src^="https://www.google.com/recaptcha/api2/bframe?"]'))
        driver.find_element_by_xpath('//*[@id="rc-imageselect"]/div[3]/div[2]/div[1]/div[1]/div[4]').click()
        time.sleep(10)
        driver.switch_to.parent_frame()
        driver.find_element_by_xpath('/html/body/div[1]/main/div[2]/div/div/div[3]/button').click()
        time.sleep(1)
        try:
            driver.find_element_by_xpath('/html/body/div[1]/main/div[2]/div/div/div[3]/button').click()
        except:
            pass
        time.sleep(5)
        sheets.add([email, username, password])
        driver.get(f'https://www.reddit.com/r/{choice(subs)}')
        driver.find_element_by_xpath('//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div[2]/div/div/div/div[2]/div[1]/div/div[1]/div/div[2]/div[1]/button').click()
        time.sleep(5)
        driver.quit()
        break
    except KeyboardInterrupt:
        break
    except Exception:
        driver.quit()
        continue
