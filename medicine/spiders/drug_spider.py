import scrapy
import re
from datetime import datetime


class DrugSpider(scrapy.Spider):
    name = 'drugs'
    start_urls = ['https://www.drugs.com']

    def parse(self, response, **kwargs):

        categories = response.css('nav.ddc-paging li:not([class]) a::attr(href)').getall()
        yield from response.follow_all(categories, callback=self.parse_medicine)

    def parse_medicine(self, response):

        medicines = response.css('.ddc-list-column-2 li a::attr(href)').getall()
        yield from response.follow_all(medicines, callback=self.parse_description)

    def parse_description(self, response):

        date_short_form = '%B %d, %Y'
        date_full_form = '%b %d, %Y'
        dated_text = response.css('.ddc-reviewed-by span ::text').getall()
        dated_text = ''.join(dated_text)
        dated = re.findall(r'on (.*?)\.', dated_text)
        dated = ''.join(dated)
        local_date = None

        if dated:

            try:
                date_with_time = datetime.strptime(dated, date_full_form)
                local_date = date_with_time.strftime('%Y-%m-%d')
            except:
                date_with_time = datetime.strptime(dated, date_short_form)
                local_date = date_with_time.strftime('%Y-%m-%d')

        medically_reviewed = response.css('.ddc-reviewed-by span ::text').getall()
        medically_reviewed = ''.join(medically_reviewed)
        medically_reviewed = re.findall(r'by.+m', medically_reviewed)

        for updated_medically_reviewed in medically_reviewed:

            yield {
                'title': response.css('.contentBox h1::text').get(),
                'medically_reviewed': updated_medically_reviewed,
                'updated_on': local_date,
                'drug_info': self.fetch_details_medicine(response),
                'url': response.url
            }

    def fetch_details_medicine(self, response):

        medicine_info = {}

        for heading in response.css(".drug-subtitle b"):
            value = heading.xpath("./following-sibling::text()").get().strip()
            if not value:
                value = heading.css('b + a::text').get()
            medicine_info[heading.css('::text').get()] = value

        return medicine_info
