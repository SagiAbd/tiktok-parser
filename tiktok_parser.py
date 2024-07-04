# importing required libraries
import os
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def update_dataset(dataset_to_update, data_to_append):
    df = pd.DataFrame(data_to_append)
    # Check if the CSV file exists and load existing data if it does
    existing_df = pd.read_csv(dataset_to_update, index_col=0) if os.path.exists(dataset_to_update) else pd.DataFrame()

    # Concatenate the existing DataFrame with the new DataFrame
    updated_df = pd.concat([existing_df, df], ignore_index=True)

    # Save the updated DataFrame to the CSV file
    updated_df.to_csv(dataset_to_update)


# defining browser
options = Options()
options.add_experimental_option("detach", True)  # to leave the browser open
# options.add_argument("--headless=new")  # to make the browser invisible; delete it if needed
options.add_argument("--mute-audio")  # mute audio of the browser
driver = webdriver.Chrome(options=options)

url = 'https://www.tiktok.com/foryou'
driver.maximize_window()  # maximize the window
driver.get(url)  # open the URL
driver.implicitly_wait(20)  # maximum time to load the link

try:
    # Handle the login popup if it appears
    driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div/div[1]/div/div/div[3]/div/div[2]').click()
    driver.implicitly_wait(10)
    time.sleep(0.5)
except Exception as e:
    print("Login popup not found or already handled.")

data = []
num_of_videos = 150  # Number of videos to watch and filter
for i in range(num_of_videos):
    # Wait for the video elements to be present on the page
    wait = WebDriverWait(driver, 30)
    videos = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, ".//*[contains(@class, 'css-1l0odge-DivContentContainer etvrc4k1')]")))

    if i % 10 == 0:  # update dataset every 10 videos
        update_dataset('data.csv', data)
        data = []

    # Scroll down by 1 pixel
    scroll_script = "window.scrollBy(0, 1);"
    driver.execute_script(scroll_script)
    time.sleep(0.3)

    # Find the video elements on the For You page
    videos = driver.find_elements(By.XPATH,
                                  ".//*[contains(@class, 'css-1l0odge-DivContentContainer etvrc4k1')]")

    # titles of videos
    try:  # avoiding xpath not found errors
        title = videos[0].find_element(By.XPATH,
                                       ".//*[contains(@class, 'css-j2a19r-SpanText efbd9f0')]").text
        driver.implicitly_wait(0.2)
    except:
        title = None  # if no titles found, leave None

    # getting metrics to get the number of likes and comments
    metrics = videos[0].find_elements(By.XPATH,
                                      ".//*[contains(@class, 'css-w1dlre-StrongText e1hk3hf92')]")
    driver.implicitly_wait(0.2)

    # traversing metrics
    like, comment = '', ''
    for index, metric in enumerate(metrics):
        if index == 0:
            like = metric.text
        elif index == 1:
            comment = metric.text

    # hashtags
    hashtags = []
    try:  # avoiding xpath not found errors
        hashtag_elements = videos[0].find_elements(By.XPATH,
                                                   ".//*[contains(@class, 'css-1p6dp51-StrongText ejg0rhn2')]")
        driver.implicitly_wait(0.2)
        for hashtag_element in hashtag_elements:
            hashtags.append(hashtag_element.text)
    except:
        pass  # if no hashtags found

    data.append({
        'title': title,
        'likes': like,
        'comments': comment,
        'hashtags': hashtags
    })

    to_remove = driver.find_elements(By.XPATH, ".//*[contains(@class, 'css-14bp9b0-DivItemContainer etvrc4k0')]")
    # Execute JavaScript to remove the first video element from the DOM
    driver.execute_script("arguments[0].remove();", to_remove[0])

    # Wait briefly before proceeding to the next iteration
    time.sleep(1)

driver.quit()
