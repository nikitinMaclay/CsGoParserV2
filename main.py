import datetime
import os
import random
import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

from mail.mail_sender import send_mail_message

proxy_ips = ["185.202.1.178",
             "185.202.1.155", "45.132.23.43",
             "185.183.163.150",
             "80.243.132.224"]


# def fast_proxy_change(driver, proxy_idx):
#     driver.get("about:config")
#     # time.sleep(2)
#     # warning_btn = driver.find_element(By.ID, value="warningButton")
#     # time.sleep(1.5)
#     # warning_btn.click()
#     time.sleep(2)
#     setup_script = f'''
#                         var prefs = Components.classes["@mozilla.org/preferences-service;1"]
#                             .getService(Components.interfaces.nsIPrefBranch);
#
#                         prefs.setIntPref("network.proxy.type", 1);
#                         prefs.setCharPref("network.proxy.http", "{proxy_ips[proxy_idx]}");
#                         prefs.setIntPref("network.proxy.http_port", {8000});
#                         prefs.setCharPref("network.proxy.ssl", "{proxy_ips[proxy_idx]}");
#                         prefs.setIntPref("network.proxy.ssl_port", {8000});
#                         prefs.setCharPref("network.proxy.ftp", "{proxy_ips[proxy_idx]}");
#                         prefs.setIntPref("network.proxy.ftp_port", {8000});
#                     '''
#
#     driver.execute_script(setup_script)
#     time.sleep(2)
#
#
# def create_database_local_connection():
#     database_connection = mysql.connector.connect(
#         host="localhost",
#         port=3306,
#         user="root",
#         password="Lapa2174",
#         database="knifes",
#     )
#
#     cursor = database_connection.cursor()
#
#     return database_connection, cursor


conditions = {
    "FN": "%28Factory New%29",
    "MW": "%28Minimal Wear%29",
    "FT": "%28Field-Tested%29",
    "WW": "%28Well-Worn%29",
    "BS": "%28Battle-Scarred%29"
}


def csgo_checker(percent, link="https://lis-skins.ru/market/csgo/?"
                               "sort_by=hot&type_id=46%2C48%2C49%2C47%2C50%2C51&price_from=6"):
    try:

        # Создание опций и их настройка (для selenium)
        options = Options()
        options_buff = Options()

        # options.set_preference("network.proxy.type", 1)
        # options.set_preference("network.proxy.http", "91.229.112.142")
        # options.set_preference("network.proxy.http_port", 8000)
        # options.set_preference('network.proxy.socks', '91.229.112.142')
        # options.set_preference('network.proxy.socks_port', 8000)
        # options.set_preference('network.proxy.socks_remote_dns', False)
        # options.set_preference("network.proxy.ssl", "91.229.112.142")
        # options.set_preference("network.proxy.ssl_port", 8000)
        # options.add_argument("--headless")

        profile_directory = r'%AppData%\Mozilla\Firefox\Profiles\duhsw7lg.CsV2'
        # profile_directory = r'%AppData%\Mozilla\Firefox\Profiles\c0bsyocz.CsGoParser'
        profile = webdriver.FirefoxProfile(os.path.expandvars(profile_directory))
        # profile.set_preference('permissions.default.image', 2)
        # profile.set_preference('profile.managed_default_content_settings.stylesheet', 2)
        # profile.set_preference("profile.managed_default_content_settings.images", 2)
        # profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        options.profile = profile

        profile_directory_buff = r'%AppData%\Mozilla\Firefox\Profiles\duhsw7lg.CsV2'
        profile_buff = webdriver.FirefoxProfile(os.path.expandvars(profile_directory))
        options_buff.profile = profile_buff


        # Список для хранения данных о ножах
        items_info = []

        # необходимые переменные
        n = 0
        last_market_items = []
        # now = datetime.datetime.now()
        # comp_year, comp_month, comp_day = int(now.strftime("%Y")), int(now.strftime("%m")), int(now.strftime("%d"))

        # драйвер и настройка

        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(600)
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)
        try:
            driver.get(link)
        except:
            print("Страница не загрузилась за 10 минут")
            send_mail_message("Страница не загрузилась за 10 минут - Сервер со всем горячими предложениями")
            driver.get(link)

        time.sleep(3)
        driver.switch_to.default_content()

        # proxy_idx = 0
        # count = 0
        # count_to_change = 200

        driver_buff = webdriver.Firefox(options=options_buff)
        driver_buff.maximize_window()
        driver_buff.implicitly_wait(30)

        wait_buff = WebDriverWait(driver, 10)

        driver_buff.get("https://buff.163.com/market/csgo")

        while True:
            driver.refresh()

            try:
                proxy_detection = driver.find_element(By.CLASS_NAME, value="message")
                print("Превышен лимит запросов. IP забанен")
                send_mail_message("Превышен лимит запросов. IP забанен - Сервер со всем горячими предложениями")
            except:
                pass

            try:
                driver.switch_to.default_content()

                login_status = driver.find_element(By.CLASS_NAME,
                                                   value="login-button").find_element(by=By.CLASS_NAME,
                                                                                      value="desktop-only")
                print(login_status.text)
                print("Слетел аккаунт")
                send_mail_message("Слетел аккаунт - Сервер со всем горячими предложениями")
                driver.close()
                driver_buff.close()

            except:
                pass

            # Проверка отсутствия скинов
            try:
                time.sleep(0.3)
                driver.switch_to.default_content()

                no_skins_elem = driver.find_element(by=By.CLASS_NAME, value="no-skins")
                print(no_skins_elem.text)

            except NoSuchElementException:
                market_items = driver.find_elements(by=By.CLASS_NAME, value="market_item")[:12]
                try:
                    market_items_list = [i.get_attribute("data-id") for i in market_items]
                except:
                    time.sleep(1)
                    market_items_list = [i.get_attribute("data-id") for i in market_items]

                if len(market_items) != 0:
                    if n != 0:
                        if sorted(market_items_list) != sorted(last_market_items):
                            need_items = [i for i in market_items if i.get_attribute("data-id") not in last_market_items]
                            for current_item in need_items:
                                cur_item_info = {}
                                cur_item_info["skin_full_name"] = current_item.find_elements(by=By.TAG_NAME,
                                                                                             value='img')[-1].get_attribute("alt")
                                cur_item_info["link_to_buy"] = current_item.find_element(by=
                                                                                         By.TAG_NAME,
                                                                                         value="a").get_attribute("href")

                                skin_cost = current_item.find_element(by=By.CLASS_NAME, value="price").text
                                skin_cost = skin_cost.replace(" ", "")
                                skin_cost = skin_cost.replace("$", "").replace("₽", "")
                                try:
                                    skin_cost = float(skin_cost.replace(",", "."))
                                except:
                                    skin_cost = float(skin_cost.split(".cls")[0])
                                cur_item_info["skin_cost"] = skin_cost

                                items_info.append(cur_item_info)
                            print(items_info)
                            buff_search_input = driver_buff.find_element(By.ID,
                                                                         value="j_search").find_element(By.TAG_NAME,
                                                                                                        value="input")
                            for current_item in items_info:
                                buff_search_input.clear()
                                time.sleep(2)
                                buff_search_input.send_keys(current_item["skin_full_name"])
                                time.sleep(0.5)
                                driver_buff.find_element(By.ID, value="search_btn_csgo").click()
                                time.sleep(8)
                                if "StatTrak" in current_item["skin_full_name"]:
                                    cost_to_check = \
                                        driver_buff.find_element(
                                            By.CLASS_NAME, value="card_csgo").find_element(
                                            By.TAG_NAME, value="li").find_element(
                                            By.TAG_NAME, value="strong").text
                                else:
                                    elems = driver_buff.find_element(
                                            By.CLASS_NAME, value="card_csgo").find_elements(
                                            By.TAG_NAME, value="li")
                                    for el in elems:
                                        if "StatTrak" not in el.find_element(By.TAG_NAME, value="h3").text:
                                            cost_to_check = el.find_element(By.TAG_NAME, value="strong").text
                                            break
                                        else:
                                            cost_to_check = 0

                                cost_to_check = float(cost_to_check[1:].replace(' ', ''))
                                print(f"cost_to_check for {current_item['skin_full_name']} is", cost_to_check)

                                if current_item["skin_cost"] <= (cost_to_check - (cost_to_check * percent / 100)):
                                    print("NEED TO BUY!")
                                    print(current_item["skin_full_name"])
                                    print("on lis skins", current_item["skin_cost"])
                                    print("on market", cost_to_check)
                                    driver.get(current_item["link_to_buy"])

                                    buy_now_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "buy-now-button")))

                                    buy_now_btn.click()

                                    try:
                                        buy_now_popup_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,
                                                                                                   "buy-now-popup-bottom-button")))
                                        buy_now_popup_btn.click()
                                        print("HAVE BEEN BOUGHT")
                                        try:
                                            send_mail_message(f"Куплен нож {cur_item_info['skin_full_name']}\n"
                                                              f"Ссылка на нож: {cur_item_info['link_to_buy']} "
                                                              f"- Сервер со всем горячими предложениями")
                                        except Exception as e:
                                            print(f"not sent:\n", e)
                                    except TimeoutException:

                                        print("SOS!!! NO MONEY!")

                            items_info = []
                            driver.get(link)
                            time.sleep(1)

                            last_market_items = market_items_list
                    else:
                        last_market_items = market_items_list
                        print(last_market_items)
                        n = 1
            time.sleep(20)
        driver.quit()
        driver_buff.quit()
    except Exception as e:
        print(e)

        try:
            driver.quit()
            driver_buff.quit()
        except Exception as e:
            pass

        csgo_checker(percent)


percent = float(input("Введите процент : "))
csgo_checker(percent)
