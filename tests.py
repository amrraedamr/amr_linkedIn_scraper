from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import json
from selenium.webdriver.chrome.service import Service


def get_login_info(driver, username, password):
    if username and not password:
        password = input("Please Enter Password: ")
        password = password
    elif not username and password:
        username = input("Please Enter Username: ")
        username = username


def login(driver, username, password):
    if not username or not password:
        get_login_info()

    else:
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        email_elem = driver.find_element(By.ID, "username")
        email_elem.send_keys(username)

        password_elem = driver.find_element(By.ID, "password")
        password_elem.send_keys(password)
        password_elem.submit()
        # time.sleep(10)


def is_logged_in(driver):
    try:
        driver.find_element(By.ID, "global-nav-search")
        return True
    except:
        pass
    return False


def load_page(driver, url):
    # driver = self.driver
    driver.get(url)
    start = time.time()
    initial_scroll = 0
    final_scroll = 1000
    while True:
        driver.execute_script(f"window.scrollTo({initial_scroll},{final_scroll})")
        initial_scroll = final_scroll
        final_scroll += 1000
        time.sleep(0.5)
        end = time.time()
        if round(end - start) > 5:
            break


def get_publications(driver, profile_url):
    url = profile_url + 'details/publications/'
    publications = {}
    months = ['Jan ', 'Feb ', 'Mar ', 'Apr ',
              'May ', 'Jun ', 'Jul ', 'Aug ',
              'Sep ', 'Oct ', 'Nov ', 'Dec ']

    load_page(driver, url)
    src = driver.page_source
    soup = BeautifulSoup(src, 'lxml')

    try:
        nthn = soup.find('section', {'class': 'artdeco-card ember-view pb3'}).find(
            'h2', {
                'class': 'artdeco-empty-state__headline artdeco-empty-state__headline--mercado-empty-room-large '
                         'artdeco-empty-state__headline--mercado-spots-large'}).get_text().strip()
        if nthn == 'Nothing to see for now':
            publications = None
            return publications
    except AttributeError:
        pass

    publications_list = soup.find('div', {'class': 'pvs-list__container'}).find_all(
        'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

    for i, j in enumerate(publications_list):
        display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})
        inner_display_flex = display_flex.find('div', {'class': 'display-flex flex-row justify-space-between'})

        title = inner_display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
            'span', {'class': 'visually-hidden'}
        ).get_text().strip()
        try:
            publisher_date = inner_display_flex.find('span', {'class': 't-14 t-normal'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip().split(' · ')

            if len(publisher_date) == 2:
                publisher = publisher_date[0]
                date = publisher_date[1]
            elif len(publisher_date) == 1:
                for month in months:
                    if month in publisher_date[0]:
                        publisher = None
                        date = publisher_date[0]
                    else:
                        publisher = publisher_date[0]
                        date = None
            else:
                publisher = None
                date = None
        except Exception as e:
            publisher = None
            date = None
            raise e

        other_authors_str = 'Other authors'
        outer_container = j.find('div', {'class': 'pvs-list__outer-container'})
        outer_container_list = outer_container.find_all('li', {'class': ''})
        other_authors = []
        driver1 = driver

        if len(outer_container_list) == 3:
            publication_url = outer_container_list[0].find('a').get('href')
            description = outer_container_list[1].find('span', {'class': 'visually-hidden'}).get_text().strip()
            # OTHER AUTHORS
            url = outer_container_list[2].find('a').get('href')
            driver1.get(url)
            time.sleep(0.5)
            temp_src = driver1.page_source
            temp_soup = BeautifulSoup(temp_src, 'lxml')
            artdeco_model = temp_soup.find(
                'div', {'class': 'artdeco-modal__content artdeco-modal__content--no-padding '
                                 'ember-view pvs-modal__content'})
            other_authors_list = artdeco_model.find_all(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})
            for k in other_authors_list:
                temp_author = k.find('span', {'class': 'mr1 t-bold'}).get_text().strip()
                other_authors.append(temp_author)

        elif len(outer_container_list) == 2:

            # description
            try:
                temp = outer_container_list[0].find('span', {'class': 'visually-hidden'}).get_text().strip()
                if temp and temp != other_authors_str:
                    description = temp
                    temp = outer_container_list[1].find('div', {'class': 'pv2'}).find('a').get('href')
                    if temp:
                        publication_url = temp
                        other_authors = None
                    else:
                        publication_url = None
                        url = outer_container_list[1].find('a').get('href')
                        driver1.get(url)
                        time.sleep(0.5)
                        temp_src = driver1.page_source
                        temp_soup = BeautifulSoup(temp_src, 'lxml')
                        artdeco_model = temp_soup.find(
                            'div', {'class': 'artdeco-modal__content artdeco-modal__content--no-padding '
                                             'ember-view pvs-modal__content'})
                        other_authors_list = artdeco_model.find_all(
                            'li',
                            {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})
                        for k in other_authors_list:
                            temp_author = k.find('span', {'class': 'mr1 t-bold'}).get_text().strip()
                            other_authors.append(temp_author)
            except Exception as e:
                print(e, 'line 169')
                pass

            # publication_url
            try:
                temp = outer_container_list[0].find('div', {'class': 'pv2'}).find('a').get('href')
                if temp:
                    publication_url = temp
                    temp = outer_container_list[1].find('span', {'class': 'visually-hidden'}).get_text().strip()
                    if temp and temp != other_authors_str:
                        description = temp
                        other_authors = None
                    else:
                        description = None
                        url = outer_container_list[1].find('a').get('href')
                        driver1.get(url)
                        time.sleep(0.5)
                        temp_src = driver1.page_source
                        temp_soup = BeautifulSoup(temp_src, 'lxml')
                        artdeco_model = temp_soup.find(
                            'div', {'class': 'artdeco-modal__content artdeco-modal__content--no-padding '
                                             'ember-view pvs-modal__content'})
                        other_authors_list = artdeco_model.find_all(
                            'li',
                            {
                                'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})
                        for k in other_authors_list:
                            temp_author = k.find('span', {'class': 'mr1 t-bold'}).get_text().strip()
                            other_authors.append(temp_author)
            except Exception as e:
                print(e, 'line 199')
                pass

            # other_authors
            try:
                temp = outer_container_list[0].find('span', {'class': 'visually-hidden'}).get_text().strip()
                if temp and temp == other_authors_str:
                    url = outer_container_list[0].find('a').get('href')
                    driver1.get(url)
                    time.sleep(0.5)
                    temp_src = driver1.page_source
                    temp_soup = BeautifulSoup(temp_src, 'lxml')
                    artdeco_model = temp_soup.find(
                        'div', {'class': 'artdeco-modal__content artdeco-modal__content--no-padding '
                                         'ember-view pvs-modal__content'})
                    other_authors_list = artdeco_model.find_all(
                        'li',
                        {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})
                    for k in other_authors_list:
                        temp_author = k.find('span', {'class': 'mr1 t-bold'}).get_text().strip()
                        other_authors.append(temp_author)

                    temp = outer_container_list[1].find('span', {'class': 'visually-hidden'}).get_text().strip()
                    if temp:
                        description = temp
                        publication_url = None
                    else:
                        description = None
                        publication_url = outer_container_list[1].find(
                            'div', {'class': 'pv2'}).find('a').get('href')
            except Exception as e:
                print(e, 'line 230')
                pass

        elif len(outer_container_list) == 1:
            try:
                temp = outer_container_list[0].find('span', {'class': 'visually-hidden'}).get_text().strip()
                if temp:
                    description = outer_container_list[0].find('span', {'class': 'visually-hidden'}).get_text().strip()
            except Exception as e:
                print(e, 'line 239')
                pass
            try:
                temp = outer_container_list[0].find('div', {'class': 'pv2'}).find('a').get('href')
                if temp:
                    publication_url = outer_container_list[0].find('div', {'class': 'pv2'}).find('a').get('href')
            except Exception as e:
                print(e, 'line 246')
                pass
            try:
                url = outer_container_list[0].find('a').get('href')
                driver1.get(url)
                time.sleep(0.5)
                temp_src = driver1.page_source
                temp_soup = BeautifulSoup(temp_src, 'lxml')
                artdeco_model = temp_soup.find(
                    'div', {'class': 'artdeco-modal__content artdeco-modal__content--no-padding '
                                     'ember-view pvs-modal__content'})
                other_authors_list = artdeco_model.find_all(
                    'li',
                    {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})
                for k in other_authors_list:
                    temp_author = k.find('span', {'class': 'mr1 t-bold'}).get_text().strip()
                    other_authors.append(temp_author)
            except Exception as e:
                print(e, 'line264')
                pass

        else:
            description = None
            publication_url = None
            other_authors = None

        publications.update({
            i: {
                'Title': title,
                'Publisher': publisher,
                'Date': date,
                'Description': description,
                'Publication_url': publication_url,
                'Other_authors': other_authors,
            }
        })

    return publications


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
email = "ztataz04@gmail.com"
password = "DR#(Li,g#2Q.F,Z"
linkedin_url = 'https://www.linkedin.com/in/otamimi/'

login(driver, email, password)

data = get_publications(driver, linkedin_url)

data_json = json.dumps(data)

driver.quit()

print(data_json)
