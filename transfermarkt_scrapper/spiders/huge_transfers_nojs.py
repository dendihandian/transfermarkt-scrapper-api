import logging
import scrapy
from dateutil.parser import parse
from datetime import datetime


class HugeTransfersNojsSpider(scrapy.Spider):
    name = 'huge_transfers_nojs'
    allowed_domains = ['transfermarkt.com']
    base_url = 'https://www.transfermarkt.com'

    transfer_date = '2022-02-01'
    transfer_date_display = 'Feb 1, 2022'
    page_start = 1
    page_end = 100


    def start_requests(self):
        starting_url = f"https://www.transfermarkt.com/transfers/transfertagedetail/statistik/top/land_id_zu/0/land_id_ab/0/leihe//datum/{self.transfer_date}/sort//plus/1/page/{self.page_start}"

        logging.info('scraping page: ' + starting_url)

        yield scrapy.Request(url=starting_url, callback=self.transfer_date_page, cb_kwargs={'current_page': self.page_start})


    def transfer_date_page(self, response, current_page):
        if (current_page <= self.page_end):

            yield from self.parse(response, current_page)

            if (int(current_page) + 1 <= self.page_end):
                next_page_path = response.xpath("//li[@class='tm-pagination__list-item tm-pagination__list-item--icon-next-page']/a/@href").get()
                if (next_page_path):
                    logging.info('next page: ' + str(next_page_path))
                    yield scrapy.Request(
                        url=self.base_url + next_page_path,
                        callback=self.transfer_date_page,
                        cb_kwargs={'current_page': int(current_page) + 1}
                    )

    def parse(self, response, current_page):

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        transfers = response.xpath("//table[@class='items']/tbody/tr")


        for transfer in transfers:
            href = transfer.xpath("./td[1]/table/tr[1]/td[2]/a[1]/@href").get()
            player_id = href.split("/").pop()

            name = transfer.xpath("./td[1]/table/tr[1]/td[2]/a[1]/text()").get()
            position = transfer.xpath("./td[1]/table/tr[2]/td/text()").get()
            age = transfer.xpath("./td[2]/text()").get()
            national_1 = transfer.xpath("./td[3]/img[1]/@title").get()
            national_2 = transfer.xpath("./td[3]/img[2]/@title").get()
            left_club = transfer.xpath("./td[4]/table/tr[1]/td[2]/a/text()").get()
            left_club_league = transfer.xpath("./td[4]/table/tr[2]/td[1]/a/text()").get()
            left_club_country = transfer.xpath("./td[4]/table/tr[2]/td[1]/img/@title").get()
            joined_club = transfer.xpath("./td[5]/table/tr[1]/td[2]/a/text()").get()
            joined_club_league = transfer.xpath("./td[5]/table/tr[2]/td[1]/a/text()").get()
            joined_club_country = transfer.xpath("./td[5]/table/tr[2]/td[1]/img/@title").get()
            market_value = transfer.xpath("./td[6]/text()").get()
            fee = transfer.xpath("./td[7]/a/text()").get()
            loan_fee = transfer.xpath("./td[7]/a/i[@class='normaler-text']/text()").get()

            yield {
                'player_id': player_id,
                'name': name,
                'position': position,
                'age': age,
                'national_1': national_1,
                'national_2': national_2,
                'left_club': left_club,
                'left_club_league': left_club_league,
                'left_club_country': left_club_country,
                'joined_club': joined_club,
                'joined_club_league': joined_club_league,
                'joined_club_country': joined_club_country,
                'market_value': market_value,
                'market_value_p': self.parse_value(market_value),
                'fee': fee,
                'loan_fee': loan_fee,
                'loan_fee_p': self.parse_value(loan_fee),
                'transfer_date': self.transfer_date_display,
                'transfer_date_p': self.transfer_date,

                'temp_dates_page': None,
                'temp_players_page': current_page,

                'created_at': current_time,
                'updated_at': current_time
            }

    def parse_value(self, value_string):
        if (value_string):
            value = value_string.replace('€', '')
            if ("Th." in value):
                value = value.replace("Th.", '')
                value = float(value) * 1000
            elif ("m" in value):
                value = value.replace("m", '')
                value = float(value) * 1000000
            else:
                value = value.replace("Th.", '').replace("m", '')

            return int(value)
        else:
            return None

"""
poetry run scrapy crawl huge_transfers_nojs
poetry run scrapy crawl huge_transfers_nojs --nolog
poetry run scrapy crawl huge_transfers_nojs --loglevel INFO
poetry run scrapy crawl huge_transfers_nojs --loglevel WARNING
poetry run scrapy crawl huge_transfers_nojs -o data/transfers/transfers.json
poetry run scrapy crawl huge_transfers_nojs -o data/transfers/transfers.jl
"""