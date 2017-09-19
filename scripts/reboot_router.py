#!/d/Python27/python
# -*- coding: UTF-8 -*-

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

reload(sys)
sys.setdefaultencoding('utf8')

def exist(browser, attr, txt):
    try:
        item = browser.find_element(attr, txt)
        return item
    except Exception,e:
        return None


url = 'http://10.0.0.1/'
#browser = webdriver.PhantomJS()
browser = webdriver.Firefox()

try:
    browser.get(url)
    item = browser.find_element_by_id('txt_usr_name')
    item.clear()
    item.send_keys('admin')
    item = browser.find_element_by_id('txt_password')
    item.clear()
    item.send_keys('123456')
    item = browser.find_element_by_id('btn_logon')
    item.click()

    time.sleep(3)
    item = exist(browser, 'id', 'btn_confirm')
    if item != None:
        item.click()
        time.sleep(3)
    browser.switch_to_frame('bottomLeftFrame')
    item = browser.find_element_by_link_text('系统工具')
    act = ActionChains(browser);
    act.move_to_element(item)
    act.click(item);
    act.perform()

    time.sleep(3)
    browser.switch_to_default_content()
    browser.switch_to_frame('mainFrame')
    item = browser.find_element_by_xpath('//span[text()="重启路由器"]')
    item.click()
    item = browser.find_element_by_id('btn_reboot')
    item.click()

    time.sleep(3)
    item = browser.switch_to_alert()

    #item.dismiss()
    item.accept()
    time.sleep(3)
except Exception,e:
    print e

while True:
    ask = raw_input('Quit ? : ')
    if ask=='y' or ask=='yes':
        break
browser.quit()


