#amazonで出品されているiphoneの商品情報を取得できるコード
#ステータス：実行成功
#20240915 priceがNULLのものが大量にある。

# import
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import uuid
import boto3
from decimal import Decimal

# wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# selenium 4.0 ↑
from selenium.webdriver.common.by import By
from time import sleep

chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

HREFS = []

# URL開く 
driver.get("https://www.amazon.co.jp/s?i=electronics&bbn=128188011&rh=n%3A2497181051%2Cp_n_feature_eleven_browse-bin%3A2519089051%2Cp_123%3A110955&dc&ds=v1%3A3k4BPCvrpusaTJGy4t7Mu5coWfgrizh5VW5yqsABypg&qid=1725942426&rnid=23341432051&ref=sr_nr_p_123_2")
# 待機処理
# driver.implicitly_wait(10)
sleep(10)
wait = WebDriverWait(driver=driver, timeout=60)

while True:
    #待機処理
    wait.until(EC.presence_of_all_elements_located)
    #ブラウザのウインドウ高を取得
    win_height = driver.execute_script("return window.innerHeight")
    
    #スクロール開始位置の初期値（ページの先頭からスクロールを開始する）
    last_top = 1
    
    #ページの最下部までスクロールする無限ループ
    while True:
    
      #スクロール前のページの高さを取得
      last_height = driver.execute_script("return document.body.scrollHeight")
      
      #スクロール開始位置を設定
      top = last_top
    
      #ページ最下部まで、徐々にスクロールしていく
      while top < last_height:
        top += int(win_height * 0.8)
        driver.execute_script("window.scrollTo(0, %d)" % top)
        sleep(0.5)
    
      #１秒待って、スクロール後のページの高さを取得する
      sleep(1)
      new_last_height = driver.execute_script("return document.body.scrollHeight")
    
      #スクロール前後でページの高さに変化がなくなったら無限スクロール終了とみなしてループを抜ける
      if last_height == new_last_height:
        break

    #次のループのスクロール開始位置を設定
    last_top = last_height
    
    #商品URLの取得
    URLS = driver.find_elements(By.CSS_SELECTOR,"a.a-link-normal.s-no-outline")
    
    for URL in URLS:
        URL = URL.get_attribute("href")
        # print("[INFO] URL :", URL)
        HREFS.append(URL)
    #待機処理
    wait.until(EC.presence_of_all_elements_located)

    # 次のページへ
    try:
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, ".s-pagination-next.s-pagination-separator")
            next_btn.click()
        except KeyboardInterrupt:
            break
    except:
        break
    
    #商品詳細の取得
for HREF in HREFS:
    driver.get(HREF)
    
    #uniqueID
    unique_id = f"AIP-{uuid.uuid4()}"

    #price
    try:
        # 最初に、a-offscreenクラスを持つspan要素を探す
        price = driver.find_element(By.XPATH, "//span[@class='a-price-whole']").text
    except NoSuchElementException:
        try:
            # 次に、a-price-wholeクラスを持つspan要素を探す
            price = driver.find_element(By.XPATH, "//span[@class='a-price']/span[@class='a-offscreen']").text
        except NoSuchElementException:
            try:
                price = driver.find_element(By.XPATH,'//span[@class="a-price a-text-price a-size-medium"]//span[@aria-hidden="true"]').text
            except NoSuchElementException:
                price = "NULL"

    # 価格のクリーンアップ
    price = ''.join(filter(str.isdigit, price))
    print(price)