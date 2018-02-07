import threading
from queue import Queue
from spider import Spider
from domain import *
from general import *
from scanners.ip_address import *
from scanners.robots_txt import *
# from scanners.nmap import *
# from scanners.whois import *
from models.webpage import Webpage
from models.analytics import Analytics


PROJECT_NAME = 'dzimiks'
HOMEPAGE = 'https://github.com/'
DOMAIN_NAME = get_domain_name(HOMEPAGE)
QUEUE_FILE = PROJECT_NAME + '/queue.txt'
CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
NUMBER_OF_THREADS = 4

queue = Queue()
Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)

data = read_json('sample_data/data.json')
webpage = Webpage(data)
analytics = Analytics(data)


# Create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Do the next job in the queue
def work():
    while True:
        url = queue.get()
        Spider.crawl_page(threading.current_thread().name, url)
        queue.task_done()


# Each queued link is a new job
def create_jobs():
    for link in file_to_set(QUEUE_FILE):
        queue.put(link)

    queue.join()
    crawl()


# Check if there are items in the queue, if so, crawl them
def crawl():
    queued_links = file_to_set(QUEUE_FILE)

    if len(queued_links) > 0:
        print(str(len(queued_links)) + ' links in the queue')
        create_jobs()


# Retrieve info from given url
def gather_info(name, url):
    domain_name = get_domain_name(url)
    ip_address = get_ip_address(domain_name)
    robots_txt = get_robots_txt(url)
    create_report(name, url, domain_name, ip_address, robots_txt)


# Create files with retrieved information
def create_report(name, full_url, domain_name, ip_address, robots_txt):
    project_dir = PROJECT_NAME + '/' + name
    create_project_dir(project_dir)
    write_file(project_dir + '/full_url.txt', full_url)
    write_file(project_dir + '/domain_name.txt', domain_name)
    write_file(project_dir + '/robots_txt.txt', robots_txt)
    write_file(project_dir + '/ip_address.txt', ip_address)


# Save analytics from json file
def print_analytics():
    output = ''

    output += str('URL: ')
    output += str(webpage.url) + '\n'

    output += str('\n' + 'Status: ')
    output += str(webpage.status) + '\n'

    output += str('\n' + 'Content length: ')
    output += str(len(analytics.content)) + '\n'

    output += str('\n' + 'Title: ')
    output += str(webpage.title) + '\n'

    output += str('\n' + 'Meta description: ')
    output += str(webpage.meta_description) + '\n'

    output += str('\n' + 'Links:\n')

    for link in webpage.links:
        output += str(link) + '\n'

    output += str('\n' + 'Images:\n')

    for image in webpage.images:
        output += str(image) + '\n'

    output += str('\n' + 'Headings:\n')
    heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']

    for h in heading_tags:
        for x in webpage.get_tag_content(h):
            output += str(h + ' - ' + x) + '\n'

    output += str('\n' + 'Paragraphs:\n')

    for i, x in enumerate(webpage.get_tag_content('p')):
        output += str(str(i + 1) + ' - ' + x) + '\n'

    output += str('\n' + 'Keyword frequency:\n')

    for item in analytics.keyword_count:
        output += str(str(item[1]) + ' - ' + item[0]) + '\n'

    write_file('sample_data/output_data.txt', output)
    print('Analytics from ' + get_domain_name(webpage.url) + ' has been successfully saved!')


print_analytics()
gather_info('data', HOMEPAGE)
create_workers()
crawl()