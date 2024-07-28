import datetime
import random

import re
import time

import mysql.connector
import requests
import schedule

from CloudflareBypasser import CloudflareBypasser
from mail.mail_sender import send_mail_message
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.errors import ElementNotFoundError, NoRectError


proxy_ips = ["160.116.219.20", "80.243.132.224", "185.202.1.178",
             "185.202.1.155",
             "185.183.163.150"]


def create_database_local_connection():
    database_connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="lapa21",
        database="knifes_v2",
    )

    cursor = database_connection.cursor()

    return database_connection, cursor


conditions = {
    "FN": "%28Factory New%29",
    "MW": "%28Minimal Wear%29",
    "FT": "%28Field-Tested%29",
    "WW": "%28Well-Worn%29",
    "BS": "%28Battle-Scarred%29"
}


def csgo_checker(percent, profile_id,
                 link="https://lis-skins.ru/market/csgo/?sort_by=hot&type_id=46%2C48%2C49%2C47%2C50%2C51%2C36&price_from=11"):
    try:

        db_con, cursor = create_database_local_connection()
        # Создание опций и их настройка (для selenium)

        req_url_start = f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1"
        req_url_end = f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop"
        try:
            requests.get(req_url_end)
            time.sleep(5)
        except Exception as e:
            print(e)
            pass
        try:
            response = requests.get(req_url_start)
        except Exception as e:
            print(e)
        time.sleep(2)

        response_json = response.json()
        print(response_json)
        port = response_json['automation']['port']

        options = ChromiumOptions()
        options.set_load_mode('none')
        options.no_imgs(on_off=True)
        options.set_paths(address=f'127.0.0.1:{port}')

        # Список для хранения данных о ножах
        items_info = []

        # необходимые переменные
        n = 0
        last_market_items = []
        now = datetime.datetime.now()
        comp_year, comp_month, comp_day = int(now.strftime("%Y")), int(now.strftime("%m")), int(now.strftime("%d"))

        # драйвер и настройка

        driver = ChromiumPage(addr_or_opts=options)

        m_options = ChromiumOptions()
        m_options.no_imgs(on_off=True)

        market_driver = ChromiumPage(addr_or_opts=m_options)

        driver.get(link)
        market_driver.get("https://market.csgo.com/ru")
        time.sleep(8)

        while True:

            driver.get(link)
            time.sleep(2)

            # if count >= count_to_change:
            #     count = 0
            #     # proxy_idx += 1
            #     # if proxy_idx >= len(proxy_ips) - 1:
            #     #     proxy_idx -= (len(proxy_ips) - 1)
            #     #
            #     # driver.get(link)
            #     # time.sleep(2)
            #     pass

            # try:
            #     proxy_detection = driver.find_element(By.CLASS_NAME, value="message")
            #     print("Превышен лимит запросов. IP забанен")
            #     send_mail_message("Превышен лимит запросов. IP забанен")
            #     try:
            #         # count = 0
            #         # proxy_idx += 1
            #         # if proxy_idx >= len(proxy_ips) - 1:
            #         #     proxy_idx -= (len(proxy_ips) - 1)
            #         # fast_proxy_change(driver, proxy_idx)
            #         # driver.get(link)
            #         # time.sleep(2)
            #         pass
            #     except:
            #         pass
            # except:
            #     pass
            cf_bypasser = CloudflareBypasser(driver)
            cf_bypasser.bypass()

            try:
                login_status = driver.ele("css:a.login-button", timeout=0.2).ele("css:span.desktop-only", timeout=0.2)
                print(login_status.text)
                print("Слетел аккаунт")
                send_mail_message("Слетел аккаунт")
                cursor.close()
                db_con.close()
                driver.quit()
                requests.get(req_url_end)
                return

            except ElementNotFoundError:
                pass

            # Проверка отсутствия скинов
            try:
                time.sleep(0.3)

                no_skins_elem = driver.ele("css:div.no-skins", timeout=0.2)
                print(no_skins_elem.text)

            except ElementNotFoundError:
                market_items = driver.eles("css:div.market_item")[:12]
                try:
                    market_items_list = [i.attr("data-id") for i in market_items]
                except:
                    time.sleep(2)
                    market_items_list = [i.attr("data-id") for i in market_items]

                if len(market_items) != 0:
                    if n != 0:
                        if sorted(market_items_list) != sorted(last_market_items):
                            need_items = [i for i in market_items if i.attr("data-id") not in last_market_items]
                            for current_item in need_items:
                                cur_item_info = {}
                                cur_item_info["skin_full_name"] = current_item.ele("css:div.name-inner").text
                                cur_item_info["link_to_buy"] = current_item.ele("css:a.name").attr("href")
                                # if "Phase" in cur_item_info["skin_full_name"]:
                                #     phasing = " ".join(cur_item_info["skin_full_name"].split()
                                #                        [cur_item_info["skin_full_name"].split().index("Phase"):])
                                #     cur_item_info["skin_full_name"] = \
                                #         " ".join(cur_item_info["skin_full_name"].split()
                                #                  [:cur_item_info["skin_full_name"].split().index("Phase")])
                                skin_cost = current_item.ele("css:div.price").text
                                skin_cost = skin_cost.replace(" ", "")
                                try:
                                    skin_cost = float(skin_cost.replace(",", ".").replace("$", ""))
                                except:
                                    skin_cost = float(skin_cost.split(".cls")[0].replace("$", ""))
                                cur_item_info["skin_cost"] = skin_cost
                                skins_info = current_item.ele("css:div.skin-info")
                                delimiters = r"[ \n]"
                                skins_info = re.split(delimiters, skins_info.text)
                                cur_item_info["skins_info"] = skins_info
                                if "NP" in skins_info:
                                    continue
                                try:
                                    current_condition = [i for i in skins_info if i in conditions.keys()][0]
                                    cur_item_info["current_condition"] = current_condition
                                except:
                                    continue
                                if "ST™" in cur_item_info["skins_info"]:
                                    link_to_check = f"https://market.csgo.com/" \
                                                    f"ru/{cur_item_info['skin_full_name'].split(' | ')[0]}/StatTrak%E2%84%A2 {cur_item_info['skin_full_name']} {conditions[cur_item_info['current_condition']]}"
                                    link_to_check = link_to_check.replace(" ", "%20").replace("|", "%7C")
                                    cur_item_info["link_to_check"] = link_to_check
                                else:
                                    link_to_check = f"https://market.csgo.com/" \
                                                    f"ru/{cur_item_info['skin_full_name'].split(' | ')[0]}/{cur_item_info['skin_full_name']} {conditions[cur_item_info['current_condition']]}"
                                    link_to_check = link_to_check.replace(" ", "%20").replace("|", "%7C")
                                    cur_item_info["link_to_check"] = link_to_check
                                items_info.append(cur_item_info)
                            print(items_info)
                            for current_item in items_info:
                                cursor.execute(f'''SELECT * FROM `knifes` 
                                WHERE link = '{current_item["link_to_check"].replace("'", "''")}'
''')
                                knife_to_check = cursor.fetchall()
                                if len(knife_to_check) == 0:
                                    comparison_tab = market_driver.new_tab()
                                    comparison_tab.get(current_item['link_to_check'])
                                    time.sleep(3)
                                    comparison_tab.run_js("window.scrollTo({ top: window.scrollY + 500, behavior: 'smooth' });")
                                    time.sleep(2)


                                    try:
                                        prices = comparison_tab.eles("css:div.price")[:3]
                                        prices_ = []
                                        for i in prices:
                                            el = i.text.replace(",", ".").replace("$", "").replace(" ", "").replace("₽", "")
                                            el = float(el)
                                            prices_.append(el)

                                    except:
                                        comparison_tab.refresh()
                                        time.sleep(3)
                                        prices = comparison_tab.eles("css:div.price")[:3]
                                        time.sleep(2)
                                        prices_ = []
                                        for i in prices:
                                            el = i.text.replace(",", ".").replace("$", "").replace(" ", "").replace("₽",
                                                                                                                    "")
                                            el = float(el)
                                            prices_.append(el)

                                    cost_to_check = sum(prices_) / len(prices_)
                                    query = (f'''INSERT INTO `knifes`(link, cost, datetime) 
                                    VALUES('{current_item['link_to_check'].replace("'", "''")}', '{cost_to_check}', '{datetime.datetime.now().date()}');''')
                                    cursor.execute(query)
                                    db_con.commit()
                                    comparison_tab.close()
                                else:
                                    date_obj = knife_to_check[0][-1]
                                    print(date_obj, type(date_obj))
                                    current_date = datetime.datetime.now().date()
                                    difference = current_date - date_obj
                                    if difference > datetime.timedelta(days=7):
                                        comparison_tab = market_driver.new_tab()
                                        comparison_tab.get(current_item['link_to_check'])
                                        time.sleep(3)
                                        comparison_tab.run_js(
                                            "window.scrollTo({ top: window.scrollY + 500, behavior: 'smooth' });")
                                        time.sleep(2)

                                        try:
                                            prices = comparison_tab.eles("css:div.price")[:3]
                                            prices_ = []
                                            for i in prices:
                                                el = i.text.replace(",", ".").replace("$", "").replace(" ", "").replace(
                                                    "₽", "")
                                                el = float(el)
                                                prices_.append(el)

                                        except:
                                            comparison_tab.refresh()
                                            time.sleep(3)
                                            prices = comparison_tab.eles("css:div.price")[:3]
                                            time.sleep(2)
                                            prices_ = []
                                            for i in prices:
                                                el = i.text.replace(",", ".").replace("$", "").replace(" ", "").replace(
                                                    "₽",
                                                    "")
                                                el = float(el)
                                                prices_.append(el)

                                        cost_to_check = sum(prices_) / len(prices_)
                                        query = f'''UPDATE `knifes` SET cost = '{cost_to_check}',
                                         datetime = '{datetime.datetime.now().date()}'
                                          WHERE link = '{current_item["link_to_check"]}' '''
                                        cursor.execute(query)
                                        db_con.commit()
                                        comparison_tab.close()
                                    else:
                                        cost_to_check = float(knife_to_check[0][2])

                                print(cost_to_check)
                                if current_item["skin_cost"] <= (cost_to_check - (cost_to_check * percent / 100)):
                                    print("NEED TO BUY!")
                                    print(current_item["skin_full_name"])
                                    print("on lis skins", current_item["skin_cost"])
                                    print("on market", cost_to_check)
                                    buying_tab = driver.new_tab()
                                    buying_tab.get(current_item["link_to_buy"])
                                    time.sleep(2)
                                    cf_bypasser = CloudflareBypasser(buying_tab)
                                    cf_bypasser.bypass()
                                    try:
                                        buy_now_btn = buying_tab.ele("css:div.buy-now-button", timeout=5)
                                        buy_now_btn.click()
                                    except:
                                        buying_tab.get(current_item["link_to_buy"])
                                        time.sleep(3)
                                        buy_now_btn = buying_tab.ele("css:div.buy-now-button", timeout=5)
                                        buy_now_btn.click()
                                    try:

                                        try:
                                            buy_now_popup_btn = buying_tab.ele("css:div.buy-now-popup-bottom-button",
                                                                           timeout=5)
                                            buy_now_popup_btn.click()
                                            print("HAVE BEEN BOUGHT")
                                        except Exception as e:
                                            print(e)
                                            time.sleep(3)
                                            buy_now_popup_btn = buying_tab.ele("css:div.buy-now-popup-bottom-button",
                                                                           timeout=5)
                                            buy_now_popup_btn.click()
                                            print("HAVE BEEN BOUGHT")
                                        try:
                                            send_mail_message(f"Куплен нож {cur_item_info['skin_full_name']}\n"
                                                              f"Ссылка на нож: {cur_item_info['link_to_buy']}")
                                        except Exception as e:
                                            print(f"not sent:\n", e)
                                    except Exception as e:
                                        print(e)
                                        print("SOS!!! NO MONEY!")
                                    buying_tab.close()
                            driver.close_tabs(others=True)
                            driver.get_tab(0)
                            items_info = []

                            last_market_items = market_items_list
                    else:
                        last_market_items = market_items_list
                        print(last_market_items)
                        n = 1
        cursor.close()
        db_con.close()
        driver.quit()
        market_driver.quit()
        requests.get(req_url_end)
        time.sleep(5)
    except Exception as e:
        print(e)
        cursor.close()
        db_con.close()

        try:
            driver.quit()
            market_driver.quit()
        except Exception as e:
            pass

        try:
            requests.get(req_url_end)
            time.sleep(5)
        except:
            pass

        csgo_checker(percent, profile_id)


if __name__ == "__main__":
    percent_input = int(input("Введите процент: "))
    profile_id_input = input("Введите id профиля: ")
    csgo_checker(percent=percent_input, profile_id=profile_id_input)
