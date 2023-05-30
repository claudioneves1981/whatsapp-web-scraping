import os
import pickle

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

# you can set the chromedriver path on the system path and remove this variable
CHROMEDRIVER_PATH = '/usr/lib/chromium-browser/chromedriver'
global SCROLL_TO, SCROLL_SIZE


# test sending a message
def send_a_message(driver):
    name = input('Enter the name of a user')
    msg = input('Enter your message')

    # saving the defined contact name from your WhatsApp chat in user variable
    user = driver.find_element('xpath','//span[@title = "{}"]'.format(name))
    user.click()

    # name of span class of contatct
    msg_box = driver.find_element(By.CLASS_NAME ,'_3Uu1_')
    msg_box.send_keys(msg)
    sleep(5)


def pane_scroll(dr):
    global SCROLL_TO, SCROLL_SIZE

    print('>>> scrolling side pane')
    side_pane = dr.find_element('id','pane-side')
    dr.execute_script('arguments[0].scrollTop ={} '.format(SCROLL_TO), side_pane)
    sleep(3)
    SCROLL_TO += SCROLL_SIZE


def get_messages(driver, contact_list):
    global SCROLL_SIZE
    print('>>> getting messages')
    conversations = []
        
    for contact in contact_list:
        
        try:
        	WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//span[contains(@title, "{}")]'.format(contact)))).click()
        except TimeoutException:
        	print("Timed Out. \n>>> processing next contact...")
        	
        sleep(10)	
        conversation_pane = driver.find_element(By.XPATH, '//div[@class = "_2Ts6i _2xAQV"]')
    	
        messages = set()
        length = 0
        scroll = SCROLL_SIZE
        while True:
            elements = driver.find_elements(By.CLASS_NAME,"copyable-text")
            for e in elements:
                if "+" not in e.text:
                    messages.add(e.text)
            if length == len(messages):
                break
            else:
                length = len(messages)
            driver.execute_script('arguments[0].scrollTop = -{}'.format(scroll), conversation_pane)
            sleep(2)
            scroll += SCROLL_SIZE
        conversations.append(messages)
        filename = 'collected_data/conversations/{}.json'.format(contact)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as fp:
            pickle.dump(messages, fp)
    return conversations


def main():
    global SCROLL_TO, SCROLL_SIZE
    SCROLL_SIZE = 600
    SCROLL_TO = 600
    conversations = []

    options = Options()
    options.add_argument('user-data-dir=./User_Data')  # saving user data so you don't have to scan the QR Code again
    driver = webdriver.Chrome(CHROMEDRIVER_PATH)
    driver.get('https://web.whatsapp.com/')
    input('Press enter after scanning QR code or after the page has fully loaded\n')

    try:
        # retrieving the contacts
        print('>>> getting contact list')
        contacts = set()
        length = 0
        while True:
            contacts_sel = driver.find_elements(By.CLASS_NAME, "_21S-L") 
            contacts_sel = set([j.text for j in contacts_sel])
            conversations.extend(get_messages(driver, list(contacts_sel-contacts)))
            contacts.update(contacts_sel)
            if length == len(contacts) and length != 0:
                break
            else:
                length = len(contacts)
                print(length, " contacts processed... \n>>> retrieving messages")
            pane_scroll(driver)
        print(len(contacts), "contacts retrieved")
        print(len(conversations), "conversations retrieved")
        filename = 'collected_data/all.json'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as fp:
            pickle.dump(conversations, fp)
    except Exception as e:
        print(e)
        driver.quit()


if __name__ == "__main__":
    main()
