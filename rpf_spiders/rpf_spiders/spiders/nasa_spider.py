import lxml

from scrapy import Spider
from scrapy.loader import ItemLoader
from scrapy.http import Request

from rpf_spiders.items import RpfSpidersItem
from rpf_spiders.spiders import cond_set_value

class NASASpider(Spider):
    name = "nasa_spider"
    allowed_domains = ["prod.nais.nasa.gov"]
    url = 'https://prod.nais.nasa.gov/cgibin/eps/bizops.cgi?' \
              'gr=D&pin=62#149695'
    start_urls = [url]

    def parse(self, response):
        # links = response.xpath(
        #     './/dt/a[contains(text(),"Synopsis")]/@href'
        # ).extract()
        opp = response.xpath(
            '//dt/*[contains(text(),"Synopsis")]/../..'
        )

        for op in opp:
            link = cond_set_value(
                op.xpath('./dt/a[contains(text(),"Synopsis")]/@href').extract()
            )
            url = 'https://prod.nais.nasa.gov' + link

            item = RpfSpidersItem()
            item['response_due'] = cond_set_value(op.xpath(
                './/b[contains(text(), "Response Due")]/../text()').extract())

            yield Request(url=url, callback=self.parse_rfp,
                          meta={'item': item})

    def parse_rfp(self, response):
        item = response.meta['item']
        l = ItemLoader(item=item, response=response)
        title = cond_set_value(response.xpath('//h2/text()').extract())
        l.add_value('title', title.strip())
        l.add_value('URL', response.url)
        l.add_value('posted',
                    cond_set_value(
                        response.xpath('//td[contains(text(), "Posted Date:")]'
                                       '/following::td[1]/text()').extract())
                    )
        l.add_value('classification_code',
                    cond_set_value(
                        response.xpath('//td[contains(text(), '
                                       '"Classification Code:")]/'
                                       'following::td[1]/text()').extract())
                    )
        l.add_value('NAICS_code',
                    cond_set_value(
                        response.xpath('//td[contains(text(), '
                                       '"NAICS Code:")]/'
                                       'following::td[1]/text()').extract()
                    ).strip()
                    )
        l.add_value('set_aside_code',
                    cond_set_value(
                        response.xpath('//td[contains(text(), '
                                       '"Set-Aside Code:")]/'
                                       'following::td[1]/text()').extract(), ''
                    )
                    )
        l.add_value('contracting_office_address',
                    cond_set_value(
                        response.xpath('//b[contains(text(), '
                                       '"Contracting Office Address")]/'
                                       'following::dd[2]/text()').extract())
                    )
        description = cond_set_value(
            response.xpath('//b[contains(text(), "Description")]/'
                           'following::dd[2]').extract()
        )

        l.add_value('description',
                    lxml.html.fromstring(description).text_content()
                    )

        tables = response.xpath(
            '//b[contains(text(), "Point of Contact")]/following::dd/table'
        )
        list_point_of_contact = []
        for table in tables:
            point_of_contact = {}
            for tr in table.xpath('./tr'):
                key = cond_set_value(tr.xpath('./td[1]/text()').re('(\w+):'))
                if 'Email' in key:
                    value = cond_set_value(
                        tr.xpath('./td[2]/a/text()').extract())
                else:
                    value = cond_set_value(
                        tr.xpath('./td[2]/text()').extract())
                point_of_contact[key] = value


            list_point_of_contact.append(point_of_contact)

        l.add_value('point_of_contact', list_point_of_contact)

        return l.load_item()
