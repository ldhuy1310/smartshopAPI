# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from bson import ObjectId
from sanic import Sanic, response
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib import parse
from utils import generate_qr_code, task_insert_data_crawled, remove_vietnamese_accents

app = Sanic(__name__)
app.config.update_config("./.env")


@app.listener("before_server_start")
async def set_up_db(app, loop):
    app.ctx.mdb = AsyncIOMotorClient(app.config.URI_MONGO)[app.config.DB_MONGO]
    app.ctx.aio_request = aiohttp.ClientSession(loop=loop)
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
    print("Started!")


@app.listener("after_server_start")
async def set_up_task(app, loop):
    pass


@app.route("/health_check", methods=["GET"])
async def health_check(req):
    return response.json({"status": "OK"})


@app.route("/products", methods=["GET"])
async def count(req):
    try:
        lst = []
        async for i in req.app.ctx.mdb.smart_shop.find().sort([("time_crawled", -1)]):
            i["_id"] = str(i["_id"])
            if "time_crawled" in i:
                i["time_crawled"] = str(i["time_crawled"])
            lst.append(i)
        return response.json(lst)
    except Exception as ex:
        return response.json({"Error": str(ex)})


@app.route("/products/<id>", methods=["GET"])
async def product_Detail(req, id):
    try:
        lst = []
        async for i in req.app.ctx.mdb.smart_shop.find({"id": id}).sort([("time_crawled", -1)]):
            i["_id"] = str(i["_id"])
            if "time_crawled" in i:
                i["time_crawled"] = str(i["time_crawled"])
            lst.append(i)
        return response.json(lst)
    except Exception as ex:
        return response.json({"Error": str(ex)})



@app.route("/products/<id>", methods=["DELETE"])
async def del_product(req, id):
    try:
        res = await req.app.ctx.mdb.smart_shop.delete_one({'_id': ObjectId(id)})
        return response.json(res.deleted_count)
    except Exception as ex:
        return response.json({"Error": str(ex)})


@app.route('/search')
async def search(req):
    try:
        keyword = req.args.get("q", "fptplay box")
        lst_out = []
        async for i in req.app.ctx.mdb.smart_shop.find({"keyword": remove_vietnamese_accents(keyword)}).sort(
                [("time_crawled", -1)]).limit(50):
            lst_out.append({
                "id": i["id"],
                "title": i["title"],
                "description": i["description"],
                "img": i["img"],
                "avg_rating": i["avg_rating"],
                "total_rating": i["total_rating"],
                "price": i["price"],
                "href_value": i["href_value"],
                "qrcode": i["qrcode"],
                "e_commerce_platform": i["e_commerce_platform"],
            })
        if lst_out:
            return response.json({"data": lst_out, "msg": "{} from db".format(remove_vietnamese_accents(keyword))})

        key_search = "shopee " + keyword
        url_search = "https://www.google.com/search?q={}&tbm=shop&tbs=p_ord:r".format(parse.quote(key_search))
        driver = app.ctx.chrome_driver
        driver.get(url_search)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', class_='sh-dgr__content')
        for index, result in enumerate(results):
            title_tag = result.find(class_="tAxDx")
            description_tag = result.find(class_="vEjMR")
            avg_rating_tag = result.find(class_="Rsc7Yb")
            e_commerce_platform_tag = result.find(class_="IuHnof")
            div_tag_pre_rating_tag = result.find('div', class_='uqAnbd')
            total_rating = div_tag_pre_rating_tag.next_sibling.strip() if \
                (div_tag_pre_rating_tag and div_tag_pre_rating_tag.next_sibling) else ""
            price_tag = result.find(class_="OFFNJ")
            href_tag = result.find('a', class_='xCpuod')
            product_n_img_tag = result.find('div', class_='ArOc1c')
            product_n_img = product_n_img_tag.find('img') if product_n_img_tag else None

            product_id = product_n_img['id'] if product_n_img else ""
            img_src = product_n_img['src'] if product_n_img else ""
            title = title_tag.text if title_tag else ""
            description = description_tag.text if description_tag else ""
            avg_rating = avg_rating_tag.text if avg_rating_tag else ""
            e_commerce_platform = e_commerce_platform_tag.text if e_commerce_platform_tag else ""
            price = price_tag.text if price_tag else ""
            href_value = href_tag.get('href').replace(u"/url?url=", "").split("%3F")[0].split("&rct=")[0].replace(
                "http://www.google.com", "") if href_tag else ""

            if title:
                lst_out.append({
                    "id": product_id,
                    "title": title,
                    "description": description,
                    "img": img_src,
                    "avg_rating": avg_rating,
                    "total_rating": total_rating,
                    "price": price,
                    "href_value": href_value,
                    "href_value_origin": href_value,
                    "qrcode": generate_qr_code(href_value) if href_value else "",
                    "e_commerce_platform": e_commerce_platform,
                })
        await app.add_task(task_insert_data_crawled(req, remove_vietnamese_accents(keyword), lst_out))
        return response.json({"data": lst_out})
    except Exception as ex:
        print(str(ex))
        return response.json({"data": [], "error": str(ex)})


if __name__ == "__main__":
    print("Loading!")
    app.run(host="0.0.0.0", port=app.config.PORT, workers=app.config.WORKER, debug=app.config.DEBUG,
            access_log=app.config.ACCESS_LOG,
            auto_reload=True)
