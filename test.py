# import time
#
# from DrissionPage import ChromiumPage, ChromiumOptions
# from DrissionPage.errors import ElementNotFoundError, NoRectError
# m_options = ChromiumOptions()
# m_options.no_imgs(on_off=True)
#
# market_driver = ChromiumPage(addr_or_opts=m_options)
#
# market_driver.get("https://market.csgo.com/ru")
# comparison_tab = market_driver.new_tab()
# comparison_tab.get("https://market.csgo.com/ru/Rifle/AK-47/AK-47%20%7C%20Head%20Shot%20%28Well-Worn%29")
# time.sleep(2)
# comparison_tab.run_js("window.scrollTo({ top: window.scrollY + 500, behavior: 'smooth' });")
# prices = comparison_tab.eles("css:div.price")[:3]
#
# prices = [float(i.text.replace(",", ".").replace("$", "").replace(" ", "")) for i in prices]
# print(prices)

