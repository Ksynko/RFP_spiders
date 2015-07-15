# from datetime import datetime
import random
import time

import requests
from bs4 import BeautifulSoup


from models import *
from myLogger import logger


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',}

def random_delay():
    time.sleep(random.uniform(0,3))

def fetch_summaries(keyword=None, category_id=None):
    # url = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=search&tabmode=list&='
    url = 'https://www.fbo.gov/?s=main&mode=list&tab=list'
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    states = soup.find('select', id='qs-pop').find_all('option')[1:]

    if keyword and category_id:
        keywords = {keyword:category_id}
        default_keywords = None
    else:
        # use default keywords
        keywords = None
        default_keywords = {'buy indian act': 1,
                            'buy indian': 2}

    # first fetch for all states
    if keywords:
        for keyword, category_id in keywords.items():
            fetch_summaries_state(state_val='', state_text='', soup=soup, keyword=keyword)
            fetch_summaries_state(state_val='', state_text='', soup=soup, keyword=keyword, category_id=category_id, exactly_matching=True)

    else:
        keyword = 'buy indian act'
        category_id = default_keywords[keyword]
        fetch_summaries_state(state_val='', state_text='', soup=soup, keyword=keyword)
        fetch_summaries_state(state_val='', state_text='', soup=soup, keyword=keyword, category_id=category_id, exactly_matching=True)

        keyword = 'buy indian'
        category_id = default_keywords[keyword]
        fetch_summaries_state(state_val='', state_text='', soup=soup, keyword=keyword)
        fetch_summaries_state(state_val='', state_text='', soup=soup, keyword=keyword, category_id=category_id, exactly_matching=True)

    # Requests by state
    for i, state in enumerate(states):
        logger.info('\t%s of %s: State %s' % (i+1, len(states), state.text.strip()))
        if keywords:
            for keyword, category_id in keywords.items():
                fetch_summaries_state(state['value'], state.text.strip(), soup, keyword, update_states=True)
        else:
            keyword = 'buy indian act'
            category_id = default_keywords[keyword]
            fetch_summaries_state(state['value'], state.text.strip(), soup, keyword, update_states=True)

            keyword = 'buy indian'
            category_id = default_keywords[keyword]
            fetch_summaries_state(state['value'], state.text.strip(), soup, keyword, update_states=True)


def fetch_summaries_state(state_val, state_text, soup, keyword, category_id='',
                          exactly_matching=False, update_states=False):
    # url = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=search&tabmode=list&pp=100&pageID=1&='
    # url = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=search&tabmode=list&='
    url = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=list'
    s = requests.session()
    s.headers.update(headers)
    # r = s.get(url)
    # soup = BeautifulSoup(r.content, 'html5lib')

    # create data dictionary required for POST form
    data = {}
    form = soup.find('form', attrs={'name':'search_filters'})
    tags = form.find_all('input', attrs={'type': 'hidden'})
    for tag in tags:
        data[tag['name']] = tag['value']
    data['dnf_class_values[procurement_notice][_posted_date]'] = '90'
    data['dnf_class_values[procurement_notice][set_aside][]'] = ''
    data['dnf_class_values[procurement_notice][zipstate]'] = state_val
    data['dnf_class_values[procurement_notice][procurement_type][]'] = ''
    if exactly_matching:
        keyword = '"' + keyword + '"'
    data['dnf_class_values[procurement_notice][keywords]'] = keyword
    data['autocomplete_input_dnf_class_values[procurement_notice][agency]'] = ''
    data['dnf_class_values[procurement_notice][agency]'] = ''
    data['dnf_class_values[procurement_notice][dnf_class_name]'] = 'procurement_notice'

    s.post(url, data=data)

    page_count = 0
    new_count = 0
    currently_fetched_urls = []

    url_search_results = 'https://www.fbo.gov/index?s=opportunity&mode=list&tab=list&pp=100'
    required_pages = []
    stop_pagination_flag = False
    while True:
        page_count += 1
        logger.info('\t\tPage %s' % page_count)
    
        random_delay()
        r = s.get(url_search_results)

        soup = BeautifulSoup(r.content, 'html5lib')

        ahrefs = soup.find_all('a', class_="lst-lnk-notice")

        breakloop = False
        for ahref in ahrefs:
            summary_url = 'https://www.fbo.gov/index' + ahref['href']
            if summary_url in currently_fetched_urls:
                continue
            else:
                currently_fetched_urls.append(summary_url)
            if Summary.query.filter_by(url=summary_url).first() is not None:
                # breakloop = True
                if exactly_matching:
                    smr = Summary.query.filter_by(url=summary_url).first()
                    existing_categories = smr.category_id
                    if existing_categories:
                        new_category = existing_categories + ',' + str(category_id)
                        smr.category_id = new_category
                    else:
                        smr.category_id = str(category_id)
                if update_states:
                    smr = Summary.query.filter_by(url=summary_url).first()
                    smr.state = state_text
                continue
            else:
                Summary(url=summary_url, state=state_text, category=keyword)
                new_count += 1

        # if page_count >= 5:
        #     breakloop = True
        session.commit()

        # if breakloop is True:
        #     break

        if not stop_pagination_flag:
            last_page = soup.find('a', attrs={'title': 'last page'})
            if last_page:
                max_page_number = last_page.text.replace('[', '').replace(']', '')
                max_page_number = int(max_page_number)
                for i in range(2, max_page_number+1):
                    required_pages.append(url_search_results + '&pageID=' + str(i))
                stop_pagination_flag = True

        if required_pages:
            url_search_results = random.choice(required_pages)
            required_pages.remove(url_search_results)
            print len(required_pages)
            print ('\n'*2)
        else:
            break
        # url_search_results = 'https://www.fbo.gov' + next_page_ahref['href']
        # print('+'*100)
        # print url_search_results
        # print('+'*100)

    logger.info('\t\tTotal %s new summaries fetched' % new_count)


def fetch_details_all():
    unprocessed_opps = Summary.query.filter_by(is_processed=False).all()
    for i, unprocessed_opp in enumerate(unprocessed_opps):
        logger.info('Fetching %s of %s: %s' % (i+1, len(unprocessed_opps), unprocessed_opp.url))
        fetch_details_single(unprocessed_opp.url, unprocessed_opp.state, unprocessed_opp.category, unprocessed_opp.category_id)
        unprocessed_opp.is_processed = True
        unprocessed_opp.date_processed = datetime.now()
        session.commit()
        # break


def fetch_details_single(url, state, keyword, category_id):
    random_delay()
    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.content, 'html5lib')

    if 'The requested notice cannot be found.' in str(r.content):
        logger.warning('\tNOT FOUND')
        return

    o = OpportunityDetail()

    o.url = url
    o.name = soup.find('div', class_='agency-header').h2.text

    sol_num = soup.find('div', class_='sol-num').text
    o.sol_num = sol_num[sol_num.index(':')+1:].strip()

    agency_name = soup.find('div', class_='agency-name').text.strip()
    if 'Agency' in agency_name:
        if 'Office' in agency_name:
            o.agency = agency_name[agency_name.index('Agency:')+7:agency_name.index('Office')].strip()
        elif 'Location' in agency_name:
            o.agency = agency_name[agency_name.index('Agency:')+7:agency_name.index('Location')].strip()
    if 'Office' in agency_name:
        o.office = agency_name[agency_name.index('Office:')+7:agency_name.index('Location')].strip() \
            if 'Location' in agency_name else agency_name[agency_name.index('Office:')+7:]
    if 'Location' in agency_name:
        o.location = agency_name[agency_name.index('Location:')+9:].strip()
    try:
        o.notice_type = soup.find('div', id='dnf_class_values_procurement_notice__procurement_type__widget').text.strip()
    except AttributeError:
        logger.warning('\tWARNING: Notice Type not available')

    original_posted_date = soup.find('div', id='dnf_class_values_procurement_notice__original_posted_date__widget')
    if original_posted_date is None:
        original_posted_date = soup.find('div', id='dnf_class_values_procurement_notice_archive__original_posted_date__widget')
    if original_posted_date is not None:
        original_posted_date = original_posted_date.text.strip()
        o.original_posted_date = datetime.strptime(original_posted_date, '%B %d, %Y')

    posted_date = soup.find('div', id='dnf_class_values_procurement_notice__posted_date__widget')
    if posted_date is None:
        posted_date = soup.find('div', id='dnf_class_values_procurement_notice_archive__posted_date__widget')
    if posted_date is not None:
        posted_date = posted_date.text.strip()
        o.posted_date = datetime.strptime(posted_date, '%B %d, %Y')

    response_date = soup.find('div', id='dnf_class_values_procurement_notice__response_deadline__widget')
    if response_date is None:
        response_date = soup.find('div', id='dnf_class_values_procurement_notice_archive__response_deadline__widget')
    if response_date is not None:
        o.response_date = response_date.text.strip()

    original_response_date = soup.find('div', id='dnf_class_values_procurement_notice__original_response_deadline__widget')
    if original_response_date is None:
        original_response_date = soup.find('div', id='dnf_class_values_procurement_notice_archive__original_response_deadline__widget')
    if original_response_date is not None:
        o.original_response_date = original_response_date.text.strip()

    archiving_policy = soup.find('div', id='dnf_class_values_procurement_notice__archive_type__widget')
    if archiving_policy is None:
        archiving_policy = soup.find('div', id='dnf_class_values_procurement_notice_archive__archive_type__widget')
    if archiving_policy is not None:
        o.archiving_policy = archiving_policy.text.strip()

    original_archive_date = soup.find('div', id='dnf_class_values_procurement_notice__original_archive_date__widget')
    if original_archive_date is None:
        original_archive_date = soup.find('div', id='dnf_class_values_procurement_notice_archive__original_archive_date__widget')
    if original_archive_date is not None:
        original_archive_date = original_archive_date.text.strip()
        if original_archive_date != '-':
            o.original_archive_date = datetime.strptime(original_archive_date, '%B %d, %Y')

    archive_date = soup.find('div', id='dnf_class_values_procurement_notice__archive_date__widget')
    if archive_date is None:
        archive_date = soup.find('div', id='dnf_class_values_procurement_notice_archive__archive_date__widget')
    if archive_date is not None:
        archive_date = archive_date.text.strip()
        if archive_date != '-':
            o.archive_date = datetime.strptime(archive_date, '%B %d, %Y')

    original_set_aside = soup.find('div', id='dnf_class_values_procurement_notice__original_set_aside__widget')
    if original_set_aside is None:
        original_set_aside = soup.find('div', id='dnf_class_values_procurement_notice_archive__original_set_aside__widget')
    if original_set_aside is not None:
        o.original_set_aside = original_set_aside.text.strip()

    set_aside = soup.find('div', id='dnf_class_values_procurement_notice__set_aside__widget')
    if set_aside is None:
        set_aside = soup.find('div', id='dnf_class_values_procurement_notice_archive__set_aside__widget')
    if set_aside is not None:
        o.set_aside = set_aside.text.strip()

    classification_code = soup.find('div', id='dnf_class_values_procurement_notice__classification_code__widget')
    if classification_code is None:
        classification_code = soup.find('div', id='dnf_class_values_procurement_notice_archive__classification_code__widget')
    if classification_code is not None:
        o.classification_code_num = classification_code.text.split('--')[0].strip()
        o.classification_code_desc = classification_code.text.split('--')[1].strip()

    naics_code = soup.find('div', id='dnf_class_values_procurement_notice__naics_code__widget')
    if naics_code is None:
        naics_code = soup.find('div', id='dnf_class_values_procurement_notice_archive__naics_code__widget')
    if naics_code is not None:
        naics_code = naics_code.text.strip()
        parent = naics_code.split('/')[0]
        try:
            child = naics_code.split('/')[1]
        except IndexError:
            pass
        else:
            parent_code, parent_desc = parent.split('--')[0].strip(), parent.split('--')[1].strip()
            child_code, child_desc = child.split('--')[0].strip(), child.split('--')[1].strip()
            parent_rec = NAICSParent.query.filter_by(code=parent_code).first()
            if parent_rec is None:
                parent_rec = NAICSParent(code=parent_code, desc=parent_desc)
            child_rec = NAICSChild.query.filter_by(code=child_code).first()
            if child_rec is None:
                child_rec = NAICSChild(code=child_code, desc=child_desc, parent_code=parent_rec)
            o.naics_code = child_rec

    synopsis = soup.find('div', id='dnf_class_values_procurement_notice__description__widget')
    try:
        for dates in synopsis.find_all('div', class_='notice_desc_dates'):
            dates.clear()
        o.synopsis = synopsis.text.strip()
    except AttributeError:
        pass

    contracting_office_address = soup.find('div', id='dnf_class_values_procurement_notice__office_address__widget')
    if contracting_office_address is None:
        contracting_office_address = soup.find('div', id='dnf_class_values_procurement_notice__office_address_text__widget')
    if contracting_office_address is not None:
        contracting_office_address = contracting_office_address.renderContents().replace('<br/>', '\n')
        o.contracting_office_address = ''
        for line in contracting_office_address.splitlines():
            if line.strip() != '':
                o.contracting_office_address += line.strip() + '\n'
        o.contracting_office_address = o.contracting_office_address.rstrip('\n')

    place_of_performance = soup.find('div', id='dnf_class_values_procurement_notice__place_of_performance__widget')
    if place_of_performance is None:
        place_of_performance = soup.find('div', id='dnf_class_values_procurement_notice__place_of_performance_text__widget')
    if place_of_performance is not None:
        place_of_performance = place_of_performance.text.strip()
        o.place_of_performance = ''
        for line in place_of_performance.splitlines():
            if line.strip() != '':
                o.place_of_performance += line.strip() + '\n'
        o.place_of_performance = o.place_of_performance.rstrip('\n')

    primary_poc = soup.find('div', id='dnf_class_values_procurement_notice__primary_poc__widget')
    if primary_poc is None:
        primary_poc = soup.find('div', id='dnf_class_values_procurement_notice__poc_text__widget')
    if primary_poc is not None:
        primary_poc = primary_poc.text.strip()
        o.primary_poc = ''
        for line in primary_poc.splitlines():
            if line.strip() != '':
                o.primary_poc += line.strip() + '\n'
        o.primary_poc = o.primary_poc.rstrip('\n')

    secondary_poc = soup.find('div', id='dnf_class_values_procurement_notice__secondary_poc__widget')
    if secondary_poc is not None:
        secondary_poc = secondary_poc.text.strip()
        o.secondary_poc = ''
        for line in secondary_poc.splitlines():
            if line.strip() != '':
                o.secondary_poc += line.strip() + '\n'
        o.secondary_poc = o.secondary_poc.rstrip('\n')

    o.state = state
    o.category = keyword
    o.category_id = category_id


if __name__ == '__main__':
    fetch_summaries()
    fetch_details_all()
    # fetch_details_single('https://www.fbo.gov/index?s=opportunity&mode=form&id=f315bd267c1917ec1c84ca70eb459e88&tab=core&_cview=1')
    # fetch_details_single('https://www.fbo.gov/index?s=opportunity&mode=form&id=dd5ccee6b505fed2f70d569c2cc1e2d1&tab=core&_cview=1')