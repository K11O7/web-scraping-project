from datetime import datetime
import requests
import csv
import bs4
import concurrent.futures
from tqdm import tqdm

User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
Request_header = {
    'User-Agent': User_Agent,
    'Accept-Language': 'en-US, en;q=0.5'
}
No_threads = 10


def get_html(url):
    res = requests.get(url=url, headers=Request_header)
    return res.content


def get_price(soup):
    main_price_span = soup.find('span', attrs={
        'class': "a-price-whole"
    })

    price = main_price_span.text.strip().replace("₹", "").replace(",", "").replace(".", "")
    return float(price)


def get_name(soup):
    product_name = soup.find('span', id="productTitle")
    name = product_name.text.strip()
    return name


def get_rating(soup):
    product_rating_div = soup.find('div', attrs={
        'id': 'averageCustomerReviews'
    })
    product_rating_section = product_rating_div.find('i', attrs={
       'class': 'a-icon-star'
    })
    product_rating_span = product_rating_section.find('span')
    rating = product_rating_span.text.strip().split()
    return float(rating[0])


def get_tech_details(soup):
    details = {}
    tech_details_section = soup.find('div', id='productOverview_feature_div')
    tech_table = tech_details_section.findAll('table', class_='a-normal a-spacing-micro')
    for table in tech_table:
        table_rows = table.findAll('tr')
        for row in table_rows:
            row_key = row.find('td', class_='a-span3')
            key = row_key.text.strip()
            row_value = row.find('td', class_='a-span9')
            value = row_value.text.strip().replace('\u200e', "")
            details[key] = value
    return details


def extract_info(url, output):
    product_info = {}
    html = get_html(url=url)
    soup = bs4.BeautifulSoup(html, 'lxml')
    product_info['title'] = get_name(soup)
    product_info['price'] = get_price(soup)
    product_info['rating'] = get_rating(soup)
    product_info.update(get_tech_details(soup))
    output.append(product_info)


if __name__ == '__main__':
    product_data = []
    urls = []
    with open('amazon_products.csv', newline="") as csvfile:
        urls = list(csv.reader(csvfile, delimiter=','))
    with concurrent.futures.ThreadPoolExecutor(max_workers=No_threads) as executor:
        for wkn in tqdm(range(0, len(urls))):
            executor.submit(extract_info, urls[wkn][0], product_data)
    output_filename = "output-{}.csv".format(datetime.today().strftime("%m-%d-%Y"))
    with open(output_filename, "w", encoding="utf-8") as opfile:
        writer = csv.writer(opfile)
        writer.writerow(product_data[0].keys())
        for p in product_data:
            writer.writerow(p.values())
