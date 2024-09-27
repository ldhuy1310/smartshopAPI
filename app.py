# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from sanic import Sanic, response
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib import parse

app = Sanic(__name__)
app.config.update_config("./.env")


@app.listener("before_server_start")
async def set_up_db(app, loop):
    app.ctx.mdb = AsyncIOMotorClient(app.config.URI_MONGO)[app.config.DB_MONGO]
    app.ctx.aio_request = aiohttp.ClientSession(loop=loop)


@app.listener("after_server_start")
async def set_up_task(app, loop):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome(service=Service(), options=chrome_options)
    app.ctx.chrome_driver = driver


@app.route("/health_check", methods=["GET"])
async def health_check(req):
    return response.json({"status": "OK"})


@app.route("/count", methods=["GET"])
async def count(req):
    try:
        count = await req.app.ctx.mdb.smart_shop.count_documents({})
        return response.json({"count": count})
    except Exception as ex:
        return response.json({"Error": str(ex)})


#
# @app.route("/insert", methods=["GET"])
# async def insert(req):
#     try:
#         pass
#         # await req.app.ctx.mdb.smart_shop.insert_one(})
#     except Exception as ex:
#         return response.json({"Error": str(ex)})


def get_url(product_name):
    product_name = product_name.replace(' ', '%20').replace("#", "%23")
    template = f"https://www.google.com/search?q={product_name}"
    url = template.format(product_name)
    return url


@app.route('/search')
async def search(req):
    try:
        key_search = "shopee " + "#" + req.args.get("q", "").replace(" ", "")
        url_search = "https://www.google.com/search?q=" + parse.quote(key_search)
        driver = app.ctx.chrome_driver
        driver.get(url_search)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', class_='MjjYud')
        lst_out = []
        for index, result in enumerate(results):
            title_tag = result.find(class_="LC20lb")
            description_tag = result.find(class_="VwiC3b")
            img_tag = result.find('img', {'class': 'VeBrne'})
            avg_rating_tag = result.find(class_="yi40Hd")
            total_rating_tag = result.find(class_="RDApEe")
            price_tag = result.find(class_="LI0TWe")

            img = img_tag.get('src').split(",")[-1] if img_tag else ""
            title = title_tag.text if title_tag else ""
            description = description_tag.text if description_tag else ""
            avg_rating = avg_rating_tag.text if avg_rating_tag else ""
            total_rating = total_rating_tag.text if total_rating_tag else ""
            price = price_tag.text if price_tag else ""
            if title:
                lst_out.append({
                    "title": title,
                    "description": description,
                    "img": img,
                    "avg_rating": avg_rating,
                    "total_ratign": total_rating,
                    "price": price
                })

        return response.json({"data": lst_out})
    except Exception as ex:
        print(str(ex))
        return response.json({"data": [], "error": str(ex)})


if __name__ == "__main__":
    print("start!")
    app.run(host="0.0.0.0", port=app.config.PORT, workers=app.config.WORKER, debug=app.config.DEBUG, access_log=app.config.ACCESS_LOG,
            auto_reload=True)
