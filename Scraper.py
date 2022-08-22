from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import time


class Scraper:
    def __init__(self, driver, username=None, password=None):
        self.data = None
        self.driver = driver
        self.username = username
        self.password = password

    def get_data(self):
        return self.data

    def get_login_info(self):
        if self.username and not self.password:
            password = input("Please Enter Password: ")
            self.password = password
        elif not self.username and self.password:
            username = input("Please Enter Username: ")
            self.username = username

    def login(self):
        if not self.username or not self.password:
            self.get_login_info()

        else:
            self.driver.get("https://www.linkedin.com/login")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
            email_elem = self.driver.find_element(By.ID, "username")
            email_elem.send_keys(self.username)

            password_elem = self.driver.find_element(By.ID, "password")
            password_elem.send_keys(self.password)
            password_elem.submit()
            # time.sleep(10)

    def is_logged_in(self):
        try:
            self.driver.find_element(By.ID, "global-nav-search")
            return True
        except:
            pass
        return False

    def load_page(self, url, scroll_time=5):
        # driver = self.driver
        self.driver.get(url)
        start = time.time()
        initial_scroll = 0
        final_scroll = 1000
        while True:
            self.driver.execute_script(f"window.scrollTo({initial_scroll},{final_scroll})")
            initial_scroll = final_scroll
            final_scroll += 1000
            time.sleep(0.5)
            end = time.time()
            if round(end - start) > scroll_time:
                break
        # return driver

    def scrape_profile(self, profile_url):
        if self.is_logged_in():
            print(f"You are logged in with email {self.username}")
            self.scrape(profile_url)
        else:
            print(f"You are not logged in\nLogging you in now...")
            self.login()
            self.scrape_profile(profile_url)

    def get_profile_picture_url(self, profile_url):
        try:
            url = profile_url + 'overlay/photo/'
            self.driver.get(url)
            src = self.driver.page_source
            soup = BeautifulSoup(src, 'lxml')

            panel = soup.find(
                'div', {'class': 'pv-member-photo-modal__content pv-member-photo-modal__content--padded'})
            profile_picture_url = panel.find('img').get('src')

            return profile_picture_url
        except Exception as e:
            print(e)
        return None

    def get_about(self, soup):
        try:
            about = soup.find('div', {'class': 'display-flex ph5 pv3'}).find("span").get_text().strip()
            return about
        except Exception as e:
            print(e)
        return None

    def get_name(self, soup):
        try:
            panel = soup.find('div', {'class': 'pv-text-details__left-panel'})
            name = panel.find('h1', {'class': 'text-heading-xlarge'}).get_text().strip()
            return name
        except Exception as e:
            print(e)
        return None

    def get_headline(self, soup):
        try:
            panel = soup.find('div', {'class': 'pv-text-details__left-panel'})
            headline = panel.find('div', {'class': 'text-body-medium break-words'}).get_text().strip()
            return headline
        except Exception as e:
            print(e)
        return None

    def get_location(self, soup):
        try:
            panel = soup.find('div', {'class': 'pv-text-details__left-panel pb2'})
            location = panel.find("span",
                                  {'class': 'text-body-small inline t-black--light break-words'}).get_text().strip()
            return location
        except Exception as e:
            print(e)
        return None

    def get_contact_info_url(self, soup):
        try:
            panel = soup.find('div', {'class': 'pv-text-details__left-panel pb2'})
            contact_info_url = panel.find(
                'a', {'class': 'ember-view link-without-visited-state cursor-pointer text-heading-small '
                               'inline-block break-words'}).get('href')
            return contact_info_url
        except Exception as e:
            print(e)
        return None

    def no_connections_followers(self, soup):
        no_connections, no_followers = None, None
        names = ['connections', 'followers']
        try:
            panel = soup.find('ul', {'class': 'pv-top-card--list pv-top-card--list-bullet display-flex pb1'}).find_all(
                'li')
            if len(panel) == 2:
                for i in range(len(panel)):
                    panel[i] = panel[i].get_text().strip()
            else:
                panel[0] = panel[0].get_text().strip()

            if len(panel) == 2:
                # x, y = panel[0], panel[1]
                if names[0] in panel[0] and names[1] in panel[1]:
                    no_connections = panel[0].replace(names[0], '').replace(' ', '')
                    no_followers = panel[1].replace(names[1], '').replace(' ', '')
                elif names[1] in panel[0] and names[0] in panel[1]:
                    no_connections = panel[1].replace(names[0], '').replace(' ', '')
                    no_followers = panel[0].replace(names[1], '').replace(' ', '')
                return no_connections, no_followers
            else:
                if names[0] in panel[0]:
                    no_connections = panel[0].replace(names[0], '').replace(' ', '')
                    no_followers = None
                else:
                    no_connections = None
                    no_followers = panel[0].replace(names[1], '').replace(' ', '')
                return no_connections, no_followers

        except Exception as e:
            print(e)
            return None, None

    # NOT UP TO STANDARDS -- REWRITE
    def get_experience(self, profile_url):
        url = profile_url + 'details/experience/'
        experiences = {}

        self.driver.get(url)
        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                'div', {'class': 'pvs-list__container'}).find(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'}).find(
                'h2').get_text().strip()
            if nthn == 'Nothing to see for now':
                experiences = None
                return experiences
        except:
            pass

        exp_list = soup.find_all('li', {
            'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        # HANDLE EDGE CASE FOR https://www.linkedin.com/in/sandraaclark/details/experience/
        counter = 0
        for i, j in enumerate(exp_list):
            try:
                big_display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})

                company_name_duration = big_display_flex.find(
                    'div', {'class': 'display-flex flex-row justify-space-between'})
                company_name = company_name_duration.find(
                    'div', {'class': 'display-flex align-items-center'}).get_text().strip()
                duration = company_name_duration.find(
                    'span', {'class': 't-14 t-normal'}).get_text().strip()

                big_outer_container = big_display_flex.find('div', {'class': 'pvs-list__outer-container'})
                inner_list = big_outer_container.find_all('li', {'class': 'pvs-list__paged-list-item'})
                for k in inner_list:
                    inner_big_display_flex = k.find(
                        'div', {'class': 'display-flex flex-column full-width align-self-center'})
                    inner_display_flex = inner_big_display_flex.find(
                        'div', {'class': 'display-flex flex-row justify-space-between'})

                    title = inner_display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
                        'span', {'class': 'visually-hidden'}).get_text().strip()

                    try:
                        employment_type = inner_display_flex.find('span', {'class': 't-14 t-normal'}).find(
                            'span', {'class': 'visually-hidden'}).get_text().strip()
                    except:
                        employment_type = None

                    date_place = inner_display_flex.find_all('span', {'class': 't-14 t-normal t-black--light'})
                    dates_duration = date_place[0].find(
                        'span', {'class': 'visually-hidden'}).get_text().strip().split(' · ')
                    dates = dates_duration[0].split(' - ')
                    fromm = dates[0]
                    to = dates[1]
                    duration = dates_duration[1]

                    if len(date_place) == 2:
                        location = date_place[1].find('span', {'class': 'visually-hidden'}).get_text().strip()
                    else:
                        location = None

                    description = None
                    skills = None
                    medias = []
                    try:
                        inner_outer_container = inner_big_display_flex.find(
                            'div', {'class': 'pvs-list__outer-container'})

                        inner_outer_container_list = inner_outer_container.find_all('li', {'class': ''})

                        if len(inner_outer_container_list) == 3:
                            description = inner_outer_container_list[0].find(
                                'span', {'class': 'visually-hidden'}).get_text().strip()
                            skills = inner_outer_container_list[1].find(
                                'span', {'class': 'visually-hidden'}).get_text().strip().replace('Skills:', '').split(
                                ' · ')
                            media_list = inner_outer_container_list[2].find_all(
                                'a', {'class': 'optional-action-target-wrapper'})
                            for media in media_list:
                                medias.append(media.get('href'))


                        else:
                            for kk in inner_outer_container_list:
                                # description
                                try:
                                    temp = kk.find(
                                        'span', {'class': 'visually-hidden'}).get_text().strip()
                                    if temp and not temp.startswith('Skills:'):
                                        description = temp
                                        continue
                                except:
                                    pass

                                # skills
                                try:
                                    temp = kk.find('span', {'class': 'visually-hidden'}).get_text().strip()
                                    if temp and temp.startswith('Skills:'):
                                        skills = temp.replace('Skills:', '').split(' · ')
                                        continue
                                except:
                                    pass

                                # medias
                                try:
                                    media_list = kk.find_all('a', {'class': 'optional-action-target-wrapper'})
                                    if media_list:
                                        for media in media_list:
                                            medias.append(media.get('href'))
                                        continue
                                except:
                                    pass
                    except:
                        pass

                    experiences.update({
                        counter: {
                            'Title': title,
                            'Company': company_name,
                            'Employment_type': employment_type,
                            'From': fromm,
                            'To': to,
                            'Duration': duration,
                            'Location': location,
                            'Description': description,
                            'Skills': skills,
                            'Medias': medias,
                        }
                    })
                    counter += 1
            except:
                pass

            big_display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})

            try:
                big_outer_container = big_display_flex.find('div', {'class': 'pvs-list__outer-container'})
                inner_list = big_outer_container.find_all('li', {'class': 'pvs-list__paged-list-item'})
                if inner_list:
                    continue
            except:
                pass

            display_flex = big_display_flex.find('div', {'class': 'display-flex flex-row justify-space-between'})
            title = display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip()

            temp = display_flex.find('span', {'class': 't-14 t-normal'}).find('span', {
                'class': 'visually-hidden'}).get_text().strip().split(' · ')
            if len(temp) == 2:
                company_name = temp[0]
                employment_type = temp[1]
            else:
                company_name = temp[0]
                employment_type = None

            temp = display_flex.find_all('span', {'class': 't-14 t-normal t-black--light'})
            if len(temp) == 2:
                dates_duration = temp[0].find('span', {'class': 'visually-hidden'}).get_text().strip().split(' · ')
                from_to = dates_duration[0].split(' - ')
                if len(from_to) == 2:
                    fromm = from_to[0]
                    to = from_to[1]
                else:
                    fromm = from_to[0]
                    to = None
                duration = dates_duration[1]
                location = temp[1].find('span', {'class': 'visually-hidden'}).get_text().strip()
            else:
                dates_duration = temp[0].find('span', {'class': 'visually-hidden'}).get_text().strip().split(' · ')
                from_to = dates_duration[0].split(' - ')
                if len(from_to) == 2:
                    fromm = from_to[0]
                    to = from_to[1]
                else:
                    fromm = from_to[0]
                    to = None
                duration = dates_duration[1]
                location = None

            try:
                outer_container = big_display_flex.find('div', {'class': 'pvs-list__outer-container'})
                outer_container_list = outer_container.find_all('li', {'class': ''})
                description = None
                skills = None
                medias = []
                if len(outer_container_list) == 3:
                    description = outer_container_list[0].find(
                        'span', {'class': 'visually-hidden'}).get_text().strip()
                    skills = outer_container_list[1].find(
                        'span', {'class': 'visually-hidden'}).get_text().strip().replace('Skills:', '')
                    media_list = outer_container_list[2].find_all(
                        'a', {'class': 'optional-action-target-wrapper'})
                    for media in media_list:
                        medias.append(media.get('href'))

                elif len(outer_container_list) == 2:

                    # description
                    try:
                        temp = outer_container_list[0].find(
                            'span', {'class': 'visually-hidden'}).get_text().strip()
                        if temp and not temp.startswith('Skills:'):
                            description = temp
                            temp = outer_container_list[1].find(
                                'span', {'class': 'visually-hidden'}).get_text().strip()
                            if temp and temp.startswith('Skills:'):
                                skills = temp.replace('Skills:', '')
                                medias = []
                            else:
                                media_list = outer_container_list[1].find_all(
                                    'a', {'class': 'optional-action-target-wrapper'})
                                for media in media_list:
                                    medias.append(media.get('href'))
                    except:
                        pass

                    # skills
                    try:
                        temp = outer_container_list[0].find(
                            'span', {'class': 'visually-hidden'}).get_text().strip()
                        if temp and temp.startswith('Skills:'):
                            skills = temp.replace('Skills:', '')
                            temp = outer_container_list[1].find(
                                'span', {'class': 'visually-hidden'}).get_text().strip()
                            if temp:
                                description = temp
                                medias = []
                            else:
                                media_list = outer_container_list[1].find_all(
                                    'a', {'class': 'optional-action-target-wrapper'})
                                for media in media_list:
                                    medias.append(media.get('href'))
                    except:
                        pass

                    # medias
                    try:
                        media_list = outer_container_list[0].find_all(
                            'a', {'class': 'optional-action-target-wrapper'})
                        if media_list:
                            for media in media_list:
                                medias.append(media.get('href'))
                            temp = outer_container_list[1].find(
                                'span', {'class': 'visually-hidden'}).get_text().strip()
                            if temp and temp.startswith('Skills:'):
                                skills = temp.replace('Skills:', '')
                                description = None
                            elif temp:
                                description = temp
                                skills = None
                    except:
                        pass

                elif len(outer_container_list) == 1:
                    # description
                    try:
                        temp = outer_container_list[0].find(
                            'span', {'class': 'visually-hidden'}).get_text().strip()
                        if temp and not temp.startswith('Skills:'):
                            description = temp
                    except:
                        pass
                    # skills
                    try:
                        temp = outer_container_list[0].find(
                            'span', {'class': 'visually-hidden'}).get_text().strip()
                        if temp and temp.startswith('Skills:'):
                            skills = temp.replace('Skills:', '')
                    except:
                        pass
                    # medias
                    try:
                        media_list = outer_container_list[0].find_all(
                            'a', {'class': 'optional-action-target-wrapper'})
                        if media_list:
                            for media in media_list:
                                medias.append(media.get('href'))
                    except:
                        pass
                else:
                    description = None
                    skills = None
                    medias = []

            except:
                description = None
                skills = None
                medias = []
                pass

            experiences.update({
                counter: {
                    'Title': title,
                    'Company': company_name,
                    'Employment_type': employment_type,
                    'From': fromm,
                    'To': to,
                    'Duration': duration,
                    'Location': location,
                    'Description': description,
                    'Skills': skills,
                    'Medias': medias,
                }
            })
            counter += 1
        return experiences

    # HAS BAD CODE -- REWRITE
    def get_education(self, profile_url):
        url = profile_url + 'details/education/'
        edu_list = []
        educations = {}

        # self.driver.get(url)
        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                'div', {'class': 'pvs-list__container'}).find(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'}).find(
                'h2').get_text().strip()
            if nthn == 'Nothing to see for now':
                educations = None
                return educations
        except:
            pass

        edu_list = soup.find_all('li', {
            'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        for i, j in enumerate(edu_list):
            university = None
            degree_field_of_study = None
            degree = None
            field_of_study = None
            fromm = None
            to = None
            grade = None
            activities_societies = None
            description = None

            display_flex = j.find('div', {'class': 'display-flex flex-row justify-space-between'})
            university = display_flex.find('div', {'class': 'display-flex align-items-center'}).find('span', {
                'class': 'visually-hidden'}).get_text().strip()

            try:
                temp = display_flex.find('span', {'class': 't-14 t-normal'}).find('span', {
                    'class': 'visually-hidden'}).get_text().strip().split(', ')
                degree_field_of_study = None
                degree = None
                field_of_study = None
                if len(temp) == 2:
                    degree = temp[0]
                    field_of_study = temp[1]
                else:  # NEEDS LOTS OF WORK FOR EDGE CASE HANDLING
                    degree_field_of_study = temp[0]
                    degree = None
                    field_of_study = None
            except AttributeError:
                field_of_study = None
                degree = None
                field_of_study = None
            try:
                from_to = display_flex.find('span', {'class': 't-14 t-normal t-black--light'}).find('span', {
                    'class': 'visually-hidden'}).get_text().strip().split(' - ')
                if len(from_to) == 2:
                    fromm = from_to[0]
                    to = from_to[1]
                else:
                    fromm = from_to[0]
                    to = None
            except AttributeError:
                fromm = None
                to = None

            li = ['Grade: ', 'Activities and societies: ']
            try:
                outer_container = j.find('div', {'class': 'pvs-list__outer-container'})
                temp_list = outer_container.find_all('li', {'class': ''})

                grade, activities_societies, description = None, None, None
                for jj in temp_list:
                    try:
                        temp = jj.find('span', {'class': 'visually-hidden'}).get_text().strip()
                        if li[0] in temp:
                            temp = temp.replace(li[0], '')
                            grade = temp
                        elif li[1] in temp:
                            temp = temp.replace(li[1], '')
                            activities_societies = temp
                        else:
                            description = temp
                    except AttributeError:
                        pass

            except AttributeError:
                grade = None
                activities_societies = None
                description = None

            educations.update({
                i: {
                    'University': university,
                    'Degree/field_of_study': degree_field_of_study,
                    'Degree': degree,
                    'Field_of_study': field_of_study,
                    'From': fromm,
                    'To': to,
                    'Grade': grade,
                    'Activities_and_societies': activities_societies,
                    'Description': description,
                }
            })
        return educations

    # HAS VERY BAD CODE -- WORKS, BUT NEEDS LOTS OF IMPROVEMENTS -- REWRITE
    def get_certifications(self, profile_url):
        url = profile_url + 'details/certifications/'
        certifications = {}

        # self.driver.get(url)
        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                'div', {'class': 'pvs-list__container'}).find(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'}).find(
                'h2').get_text().strip()
            if nthn == 'Nothing to see for now':
                certifications = None
                return certifications
        except AttributeError:
            pass

        cer_list = soup.find_all('li', {
            'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        for i, j in enumerate(cer_list):
            issue_date, expiry_date, credential_id = None, None, None,

            display_flex = j.find('div', {'class': 'display-flex flex-row justify-space-between'})
            try:
                link = j.find('a', {'class': 'optional-action-target-wrapper display-flex flex-column full-width'}).get(
                    'href')
            except AttributeError:
                link = None
                pass

            name = display_flex.find('div', {'class': 'display-flex align-items-center'}).find('span', {
                'class': 'visually-hidden'}).get_text().strip()
            issuing_organization = display_flex.find('span', {'class': 't-14 t-normal'}).find('span', {
                'class': 'visually-hidden'}).get_text().strip()
            li = ['Issued ', 'Credential ID ']
            li2 = ['Expired', 'Expires ', 'No Expiration Date']
            try:
                temp = display_flex.find_all('span', {'class': 't-14 t-normal t-black--light'})
                for k in range(len(temp)):
                    temp[k] = temp[k].find('span', {'class': 'visually-hidden'}).get_text().strip()

                if len(temp) == 2:
                    if li[0] in temp[0] and li[1] in temp[1]:
                        temp[0] = temp[0].split(' · ')
                        issue_date = temp[0][0].replace(li[0], '')
                        if li2[0] in temp[0][1]:
                            expiry_date = temp[0][1].replace(li2[0], '')
                        elif li2[1] in temp[0][1]:
                            expiry_date = temp[0][1].replace(li2[1], '')
                        elif li2[2] in temp[0][1]:
                            expiry_date = None
                        credential_id = temp[1].replace(li[1], '')
                elif len(temp) == 1:
                    if li[0] in temp[0]:
                        credential_id = None
                        temp[0] = temp[0].split(' · ')
                        issue_date = temp[0][0].replace(li[0], '')
                        if li2[0] in temp[0][1]:
                            expiry_date = temp[0][1].replace(li2[0], '')
                        elif li2[1] in temp[0][1]:
                            expiry_date = temp[0][1].replace(li2[1], '')
                        elif li2[2] in temp[0][1]:
                            expiry_date = None
                    elif li[1] in temp[0]:
                        issue_date, expiry_date = None, None
                        credential_id = temp[1].replace(li[1], '')
                    else:
                        issue_date, expiry_date, credential_id = None, None, None
            except:
                issue_date, expiry_date, credential_id = None, None, None
                pass

            certifications.update({
                i: {
                    'Name': name,
                    'Link': link,
                    'issuing_organization': issuing_organization,
                    'Issue_date': issue_date,
                    'Expiry_date': expiry_date,
                    'Credential_ID': credential_id,
                }})

        return certifications

    # ADD IF PASSED LINKEDIN ASSESSMENT TEST FIELD
    # MAKE ENDORSERS LIST OPTIONAL
    def get_skills(self, profile_url):  # CHANGE endorsement_profile_list TO BE DICTIONARY OF ENDORSERS
        url = profile_url + 'details/skills/'
        skill_list = []
        skills = {}
        li = 'endorsement'
        driver1 = self.driver

        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('section', {'class': 'artdeco-card ember-view pb3'}).find(
                'h2', {
                    'class': 'artdeco-empty-state__headline artdeco-empty-state__headline-- '
                             'artdeco-empty-state__headline--3'}).get_text().strip()
            if nthn == 'Nothing to see for now':
                skills = None
                return skills
        except AttributeError:
            pass
        try:
            skill_list = soup.find('div', {'class': 'pvs-list__container'}).find_all(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})
            for i, j in enumerate(skill_list):
                skill_name, no_endorsements, endorsement_profile_list = None, None, None
                display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})
                skill_name = display_flex.find('span', {'class': 'visually-hidden'}).get_text().strip()

                outer_container = display_flex.find('div', {'class': 'pvs-list__outer-container'})
                if outer_container.get_text().strip() == '':
                    no_endorsements = '0'
                    endorsement_profile_list = []
                    skills.update({
                        i: {
                            'Skill_name': skill_name,
                            'No_endorsements': no_endorsements,
                            'Endorsement_profile_list': endorsement_profile_list,
                        }})
                    continue

                outer_endorse_list = outer_container.find_all('li', {'class': ''})

                for ii in outer_endorse_list:
                    temp = ii.find('span', {'class': "visually-hidden"})
                    if li in temp.get_text().strip():
                        no_endorsements = temp.get_text().strip().replace(' endorsements', '').replace(' endorsement',
                                                                                                       '')
                        url = ii.find('a').get('href')
                        driver1.get(url)
                        time.sleep(0.5)
                        temp_src = driver1.page_source
                        temp_soup = BeautifulSoup(temp_src, 'lxml')
                        try:
                            if temp_soup.find('section', {'class': 'artdeco-empty-state ember-view'}).find(
                                    'h2').get_text().strip() == 'Endorsements from colleagues will appear here':
                                endorsement_profile_list = []
                                skills.update({
                                    i: {
                                        'Skill_name': skill_name,
                                        'No_endorsements': no_endorsements,
                                        'Endorsement_profile_list': endorsement_profile_list,
                                    }})
                                break
                        except AttributeError:
                            pass
                        var = True
                        while var:
                            try:
                                element = driver1.find_element(
                                    By.XPATH, '/html/body/div[3]/div/div/div[2]/div/div[2]/div/div/div[2]/div/button')
                                element.click()
                                time.sleep(0.25)
                            except NoSuchElementException:
                                break
                            except StaleElementReferenceException:
                                var = False

                        src2 = driver1.page_source
                        soup2 = BeautifulSoup(src2, 'lxml')
                        endorsement_profile_list = []
                        try:
                            list__container = soup2.find('div', {'class': 'pvs-list__container'})
                            endorsement_list = list__container.find_all('li', {
                                'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})
                            for jj in endorsement_list:
                                endorsement_profile_link = jj.find('a').get('href')
                                endorsement_profile_list.append(endorsement_profile_link)
                        except AttributeError as e:
                            print(e)
                            pass

                    else:
                        no_endorsements = None
                        endorsement_profile_list = []

                skills.update({
                    i: {
                        'Skill_name': skill_name,
                        'No_endorsements': no_endorsements,
                        'Endorsement_profile_list': endorsement_profile_list,
                    }})

        except Exception as e:
            raise e
        return skills

    def get_languages(self, profile_url):
        url = profile_url + 'details/languages/'
        langs = {}

        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                'div', {'class': 'pvs-list__container'}).find(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'}).find(
                'h2').get_text().strip()
            if nthn == 'Nothing to see for now':
                langs = None
                return langs
        except AttributeError:
            pass

        lang_list = soup.find('div', {'class': 'pvs-list__container'}).find_all(
            'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        for i, j in enumerate(lang_list):
            display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})
            lang_name = display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip()
            try:

                proficiency = display_flex.find('span', {'class': 't-14 t-normal t-black--light'}).find(
                    'span', {'class': 'visually-hidden'}).get_text().strip()
            except AttributeError:
                proficiency = None

            langs.update({
                i: {
                    'Language': lang_name,
                    'Proficiency': proficiency,
                }
            })
        return langs

    def get_publications(self, profile_url):
        url = profile_url + 'details/publications/'
        publications = {}
        months = ['Jan ', 'Feb ', 'Mar ', 'Apr ',
                  'May ', 'Jun ', 'Jul ', 'Aug ',
                  'Sep ', 'Oct ', 'Nov ', 'Dec ']

        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                'div', {'class': 'pvs-list__container'}).find(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'}).find(
                'h2').get_text().strip()
            if nthn == 'Nothing to see for now':
                publications = None
                return publications
        except AttributeError:
            pass

        publisher = None
        date = None

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
            except:
                publisher = None
                date = None

            other_authors_str = 'Other authors'
            description = None
            publication_url = None
            other_authors = []

            try:
                outer_container = j.find('div', {'class': 'pvs-list__outer-container'})
                outer_container_list = outer_container.find_all('li', {'class': ''})
                other_authors = []
                driver1 = self.driver

                for k in outer_container_list:

                    # PUBLICATION URL
                    try:
                        temp = k.find('div', {'class': 'pv2'}).find('a').get('href')
                        if temp:
                            publication_url = temp
                            continue
                    except:
                        pass

                    # DESCRIPTION
                    try:
                        temp = k.find('span', {'class': 'visually-hidden'}).get_text().strip()
                        if temp and temp != other_authors_str:
                            description = temp
                            continue
                    except:
                        pass

                    # OTHER_AUTHORS
                    try:
                        temp = k.find(
                            'span', {'class': 'visually-hidden'}).get_text().strip()
                        if temp and temp == other_authors_str:
                            url = k.find(
                                'div', {'class': 'overflow-hidden full-width'}).find(
                                'a', {'class': 'optional-action-target-wrapper'}).get('href')
                            driver1.get(url)
                            time.sleep(0.5)
                            temp_src = driver1.page_source
                            temp_soup = BeautifulSoup(temp_src, 'lxml')
                            artdeco_model = temp_soup.find(
                                'div', {'class': 'artdeco-modal__content artdeco-modal__content--no-padding '
                                                 'ember-view pvs-modal__content'})
                            other_authors_list = artdeco_model.find_all(
                                'li', {'class': 'pvs-list__paged-list-item '
                                                'artdeco-list__item pvs-list__item--line-separated'})
                            for kk in other_authors_list:
                                temp_author = kk.find('span', {'class': 'mr1 t-bold'}).get_text().strip()
                                other_authors.append(temp_author)
                    except:
                        continue
            except:
                pass

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

    def get_honors_awards(self, profile_url):
        url = profile_url + 'details/honors/'
        honors_awards = {}
        issued_by_str = 'Issued by '
        associated_with_str = 'Associated with '

        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                'div', {'class': 'pvs-list__container'}).find(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'}).find(
                'h2').get_text().strip()
            if nthn == 'Nothing to see for now':
                honors_awards = None
                return honors_awards
        except AttributeError:
            pass

        title = None
        issuer = None
        issue_date = None
        associated_with = None
        description = None

        honors_awards_list = soup.find('div', {'class': 'pvs-list__container'}).find_all(
            'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        for i, j in enumerate(honors_awards_list):
            display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})
            inner_display_flex = display_flex.find('div', {'class': 'display-flex flex-row justify-space-between'})

            title = inner_display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip()

            try:
                temp = inner_display_flex.find('span', {'class': 't-14 t-normal'}).find(
                    'span', {'class': 'visually-hidden'}).get_text().strip().split(' · ')

                if len(temp) == 2:
                    issuer = temp[0].replace(issued_by_str, '')
                    issue_date = temp[1]
                elif len(temp) == 1:
                    if issued_by_str in temp[0]:
                        issuer = temp[0].replace(issued_by_str, '')
                        issue_date = None
                    else:
                        issuer = None
                        issue_date = temp[0]
            except:
                pass

            try:
                outer_container = j.find('div', {'class': 'pvs-list__outer-container'})
                outer_container_list = outer_container.find_all('li', {'class': ''})

                if len(outer_container_list) == 2:
                    associated_with = outer_container_list[0].find(
                        'span', {'class': 'visually-hidden'}).get_text().strip().replace(associated_with_str, '')
                    description = outer_container_list[1].find(
                        'span', {'class': 'visually-hidden'}).get_text().strip()
                elif len(outer_container_list) == 1:
                    temp = outer_container_list[0].find(
                        'span', {'class': 'visually-hidden'}).get_text().strip()
                    if temp.startswith(associated_with_str):
                        associated_with = temp
                        description = None
                    else:
                        description = temp
                        associated_with = None
                else:
                    associated_with = None
                    description = None

            except:
                associated_with = None
                description = None

            honors_awards.update({
                i: {
                    'Title': title,
                    'Issuer': issuer,
                    'Issue date': issue_date,
                    'Associated with': associated_with,
                    'Description': description,
                }
            })
        return honors_awards

    def get_courses(self, profile_url):
        url = profile_url + 'details/courses/'
        courses = {}
        associated_with_str = 'Associated with '

        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('section', {'class': 'artdeco-card ember-view pb3'}).find(
                'div', {
                    'class': 'pvs-list__container'}).find_all(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})
            if not nthn:
                courses = None
                return courses
        except AttributeError:
            pass

        courses_list = soup.find('div', {'class': 'pvs-list__container'}).find_all(
            'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        for i, j in enumerate(courses_list):
            display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})
            inner_display_flex = display_flex.find('div', {'class': 'display-flex flex-row justify-space-between'})

            course_name = inner_display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip()
            try:
                course_number = inner_display_flex.find('span', {'class': 't-14 t-normal'}).find(
                    'span', {'class': 'visually-hidden'}).get_text().strip()
            except:
                course_number = None
                pass
            try:
                associated_with = j.find('div', {'class': 'pvs-list__outer-container'}).find(
                    'li', {'class': ''}).find(
                    'span', {'class': 'visually-hidden'}).get_text().strip().replace(associated_with_str, '')
            except:
                associated_with = None
                pass

            courses.update({
                i: {
                    'Course name': course_name,
                    'Course number': course_number,
                    'Associated with': associated_with
                }
            })
        return courses

    def get_recommendations(self, profile_url):
        url_received = profile_url + 'details/recommendations/?detailScreenTabIndex=0'
        url_given = profile_url + 'details/recommendations/?detailScreenTabIndex=1'
        recommendations_received = {}
        recommendations_given = {}

        # RECEIVED
        try:
            self.load_page(url_received, 15)
            src = self.driver.page_source
            soup = BeautifulSoup(src, 'lxml')

            # NTHN
            try:
                nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                    'div', {'class': 'artdeco-tabpanel active ember-view'}).find(
                    'div', {'class': 'pvs-list__container'}).find(
                    'li', {'class': 'pvs-list__paged-list-item artdeco-list__item '
                                    'pvs-list__item--line-separated'}).find('h2').get_text().strip()
                if nthn == "You haven't received a recommendation yet":
                    recommendations_received = None
            except AttributeError:
                pass

            if recommendations_received == {}:
                recommendations_received_list = soup.find('div', {'class': 'artdeco-tabpanel active ember-view'}).find(
                    'div', {'class': 'pvs-list__container'}).find_all(
                    'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

                for i, j in enumerate(recommendations_received_list):

                    big_display_flex = j.find(
                        'div', {'class': 'display-flex flex-column full-width align-self-center'})
                    display_flex = big_display_flex.find(
                        'div', {'class': 'display-flex flex-row justify-space-between'})
                    link = display_flex.find(
                        'a', {'class': 'optional-action-target-wrapper display-flex flex-column full-width'}).get(
                        'href')
                    name = display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
                        'span', {'class': 'visually-hidden'}).get_text().strip()
                    try:
                        headline = display_flex.find('span', {'class': 't-14 t-normal'}).find(
                            'span', {'class': 'visually-hidden'}).get_text().strip()
                    except:
                        headline = None

                    date_relationship = display_flex.find('span', {'class': 't-14 t-normal t-black--light'}).find(
                        'span', {'class': 'visually-hidden'}).get_text().strip().split(',')
                    relationship = date_relationship.pop()
                    date = ','.join(map(str, date_relationship))

                    outer_container = big_display_flex.find('div', {'class': 'pvs-list__outer-container'})
                    recommendation = outer_container.find('li', {'class': ''}).find(
                        'div', {'class': 'display-flex align-items-center t-14 t-normal t-black'}).find(
                        'span', {'class': 'visually-hidden'}).get_text().strip()

                    recommendations_received.update({
                        i: {
                            'Name': name,
                            'Profile_url': link,
                            'Headline': headline,
                            'Date': date,
                            'Relationship': relationship,
                            'Recommendation': recommendation
                        }
                    })
            else:
                pass
        except:
            pass

        # GIVEN
        try:
            self.load_page(url_given, 15)
            src = self.driver.page_source
            soup = BeautifulSoup(src, 'lxml')

            # NTHN
            try:
                nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                    'div', {'class': 'artdeco-tabpanel active ember-view'}).find(
                    'div', {'class': 'pvs-list__container'}).find(
                    'li', {'class': 'pvs-list__paged-list-item artdeco-list__item '
                                    'pvs-list__item--line-separated'}).find('h2').get_text().strip()
                if nthn == "You haven't written any recommendations yet":
                    recommendations_given = None
            except AttributeError:
                pass

            if recommendations_given == {}:
                recommendations_given_list = soup.find('div', {'class': 'artdeco-tabpanel active ember-view'}).find(
                    'div', {'class': 'pvs-list__container'}).find_all(
                    'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

                for i, j in enumerate(recommendations_given_list):

                    big_display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})
                    display_flex = big_display_flex.find(
                        'div', {'class': 'display-flex flex-row justify-space-between'})

                    link = display_flex.find(
                        'a', {'class': 'optional-action-target-wrapper display-flex flex-column full-width'}).get(
                        'href')
                    name = display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
                        'span', {'class': 'visually-hidden'}).get_text().strip()
                    try:
                        headline = display_flex.find('span', {'class': 't-14 t-normal'}).find(
                            'span', {'class': 'visually-hidden'}).get_text().strip()
                    except:
                        headline = None

                    date_relationship = display_flex.find('span', {'class': 't-14 t-normal t-black--light'}).find(
                        'span', {'class': 'visually-hidden'}).get_text().strip().split(',')
                    relationship = date_relationship.pop()
                    date = ','.join(map(str, date_relationship))

                    outer_container = big_display_flex.find('div', {'class': 'pvs-list__outer-container'})
                    recommendation = outer_container.find('li', {'class': ''}).find(
                        'div', {'class': 'display-flex align-items-center t-14 t-normal t-black'}).find(
                        'span', {'class': 'visually-hidden'}).get_text().strip()

                    recommendations_given.update({
                        i: {
                            'Name': name,
                            'Profile_url': link,
                            'Headline': headline,
                            'Date': date,
                            'Relationship': relationship,
                            'Recommendation': recommendation
                        }
                    })
            else:
                pass
        except Exception as e:
            raise e
            pass

        recommendations = {
            'Received': recommendations_received,
            'Given': recommendations_given
        }
        return recommendations

    # BAD CODE
    def get_volunteering_experience(self, profile_url):
        url = profile_url + 'details/volunteering-experiences/'
        volunteering_experiences = {}
        causes = [
            'Animal Welfare', 'Arts and Culture', 'Children', 'Civil Rights and Social Action', 'Economic Empowerment',
            'Education', 'Environment', 'Health', 'Human Rights', 'Disaster and Humanitarian Relief',
            'Politics', 'Poverty Alleviation', 'Science and Technology', 'Social Services', 'Veteran Support',
        ]

        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('section', {'class': 'artdeco-card ember-view pb3'}).find(
                'div', {'class': 'pvs-list__container'}).find(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'}).find(
                'h2').get_text().strip()
            if nthn == 'Nothing to see for now':
                volunteering_experiences = None
                return volunteering_experiences
        except AttributeError:
            pass

        volunteering_experiences_list = soup.find('div', {'class': 'pvs-list__container'}).find_all(
            'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        for i, j in enumerate(volunteering_experiences_list):

            fromm = None
            to = None
            duration = None
            cause = None

            big_display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})
            display_flex = big_display_flex.find('div', {'class': 'display-flex flex-row justify-space-between'})

            role = display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip()
            organization = display_flex.find('span', {'class': 't-14 t-normal'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip()

            try:
                dates_causes = display_flex.find_all('span', {'class': 't-14 t-normal t-black--light'})

                if len(dates_causes) == 2:
                    dates = dates_causes[0].find('span', {'class': 'visually-hidden'}).get_text().strip().split(' · ')
                    from_to = dates[0].split(' - ')
                    fromm = from_to[0]
                    to = from_to[1]
                    duration = dates[1]
                    cause = dates_causes[1].find('span', {'class': 'visually-hidden'}).get_text().strip()

                elif len(dates_causes) == 1:
                    temp = dates_causes[0].find('span', {'class': 'visually-hidden'}).get_text().strip()
                    try:
                        for cau in causes:
                            if cau == temp:
                                cause = temp
                                fromm = None
                                to = None
                                duration = None
                                break
                    except:
                        pass
                    try:
                        dates = temp.split(' · ')
                        from_to = dates[0].split(' - ')
                        fromm = from_to[0]
                        to = from_to[1]
                        duration = dates[1]
                        cause = None
                    except:
                        pass

                else:
                    cause = None
                    fromm = None
                    to = None
                    duration = None

            except:
                cause = None
                fromm = None
                to = None
                duration = None
                pass

            try:
                outer_container = big_display_flex.find('div', {'class': 'pvs-list__outer-container'})

                try:
                    description = outer_container.find(
                        'div', {'class': 'display-flex align-items-center t-14 t-normal t-black'}).find(
                        'span', {'class': 'visually-hidden'}).get_text().strip()
                except:
                    description = None
                    pass
            except:
                description = None
                pass

            volunteering_experiences.update({
                i: {
                    'Role': role,
                    'Organization': organization,
                    'From': fromm,
                    'To': to,
                    'Duration': duration,
                    'Cause': cause,
                    'Description': description
                }
            })
        return volunteering_experiences

    def get_causes(self, soup):
        try:
            panels = soup.find_all('section', {'class': 'artdeco-card ember-view relative break-words pb3 mt2'})
            for panel in panels:
                temp = panel.find('div', {'id': 'volunteer_causes'})
                if temp:
                    causes = panel.find('div', {'class': 'display-flex ph5 pv3'}).find(
                        'span', {'class': 'visually-hidden'}).get_text().strip().split(' • ')
                    return causes

        except Exception as e:
            raise e

    # PROBABLY WANT TO ADD MORE TO THIS BUT FOR NOW IS GOOD ENOUGH
    def get_featured(self, profile_url):
        url = profile_url + 'details/featured/'
        featured = {}

        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                'div', {'class': 'pvs-list__container'}).find(
                'li', {'class': 'pvs-list__paged-list-item pvs-list__item--with-gap'}).find('h2').get_text().strip()
            if nthn == 'Nothing to see for now':
                featured = None
                return featured
        except AttributeError:
            pass

        featured_list = soup.find('div', {'class': 'pvs-list__container'}).find_all(
            'li', {'class': 'pvs-list__paged-list-item pvs-list__item--with-gap'})

        for i, j in enumerate(featured_list):
            link = j.find('a').get('href')
            featured.update({
                i: {
                    'Link': link
                }
            })
        return featured

    def get_test_scores(self, profile_url):
        url = profile_url + 'details/testscores/'
        test_scores = {}

        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                'div', {'class': 'pvs-list__container'}).find(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'}).find(
                'h2').get_text().strip()
            if nthn == 'Nothing to see for now':
                test_scores = None
                return test_scores
        except AttributeError:
            pass

        test_scores_list = soup.find('div', {'class': 'pvs-list__container'}).find_all(
            'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        for i, j in enumerate(test_scores_list):
            big_display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})
            display_flex = big_display_flex.find('div', {'class': 'display-flex flex-row justify-space-between'})

            title = display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip()

            score_date = display_flex.find('span', {'class': 't-14 t-normal'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip().split(' · ')
            score = score_date[0].replace('Score: ', '')
            if len(score_date) == 2:
                test_date = score_date[1]
            elif len(score_date) == 1:
                test_date = None
            else:
                test_date = None

            try:
                outer_container = big_display_flex.find('div', {'class': 'pvs-list__outer-container'})
                description = outer_container.find('span', {'class': 'visually-hidden'}).get_text().strip()
            except:
                description = None
                pass

            test_scores.update({
                i: {
                    'Title': title,
                    'Score': score,
                    'Test_date': test_date,
                    'Description': description
                }
            })
        return test_scores

    def get_organizations(self, profile_url):
        url = profile_url + 'details/organizations/'
        organizations = {}
        months = ['Jan ', 'Feb ', 'Mar ', 'Apr ',
                  'May ', 'Jun ', 'Jul ', 'Aug ',
                  'Sep ', 'Oct ', 'Nov ', 'Dec ']

        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                'div', {'class': 'pvs-list__container'}).find(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'}).find(
                'h2').get_text().strip()
            if nthn == 'Nothing to see for now':
                organizations = None
                return organizations
        except AttributeError:
            pass

        organizations_list = soup.find('div', {'class': 'pvs-list__container'}).find_all(
            'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        for i, j in enumerate(organizations_list):
            big_display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})
            display_flex = big_display_flex.find('div', {'class': 'display-flex flex-row justify-space-between'})

            organization_name = display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip()

            try:
                position_dates = display_flex.find('span', {'class': 't-14 t-normal'}).find(
                    'span', {'class': 'visually-hidden'}).get_text().strip().split(' · ')
                position = None
                fromm = None
                to = None

                if len(position_dates) == 2:
                    position = position_dates[0]
                    from_to = position_dates[1].split(' - ')
                    fromm = from_to[0]
                    to = from_to[1]
                elif len(position_dates) == 1:
                    temp = position_dates[0]
                    for month in months:
                        if month in temp:
                            position = None
                            from_to = temp.split(' - ')
                            fromm = from_to[0]
                            to = from_to[1]
                            temp = None
                            break
                    if temp:
                        position = temp
                        fromm = None
                        to = None
            except:
                position = None
                fromm = None
                to = None
                pass

            try:
                outer_container = big_display_flex.find('div', {'class': 'pvs-list__outer-container'})
                description = outer_container.find('span', {'class': 'visually-hidden'}).get_text().strip()
            except:
                description = None
                pass

            organizations.update({
                i: {
                    'Organization_name': organization_name,
                    'Position': position,
                    'From': fromm,
                    'To': to,
                    'Description': description
                }
            })
        return organizations

    def get_projects(self, profile_url):
        url = profile_url + 'details/projects/'
        projects = {}
        associated_with_str = 'Associated with '

        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                'div', {'class': 'pvs-list__container'}).find(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'}).find(
                'h2').get_text().strip()
            if nthn == 'Nothing to see for now':
                projects = None
                return projects
        except AttributeError:
            pass

        projects_list = soup.find('div', {'class': 'pvs-list__container'}).find_all(
            'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        other_creators_str = 'Other creators'

        for i, j in enumerate(projects_list):
            big_display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})
            display_flex = big_display_flex.find('div', {'class': 'display-flex flex-row justify-space-between'})

            project_name = display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip()

            fromm = None
            to = None
            try:
                dates = display_flex.find('span', {'class': 't-14 t-normal'}).find(
                    'span', {'class': 'visually-hidden'}).get_text().strip().split(' - ')
                fromm = dates[0]
                to = dates[1]
            except:
                pass

            associated_with = None
            project_url = None
            description = None
            other_creators = []
            driver1 = self.driver
            try:
                outer_container = big_display_flex.find('div', {'class': 'pvs-list__outer-container'})
                outer_container_list = outer_container.find_all('li', {'class': ''})

                if len(outer_container_list) == 4:
                    associated_with = outer_container_list[0].find(
                        'span', {'class': 'visually-hidden'}).get_text().strip().replace(associated_with_str, '')
                    project_url = outer_container_list[1].find('div', {'class': 'pv2'}).find('a').get('href')
                    description = outer_container_list[2].find(
                        'span', {'class': 'visually-hidden'}).get_text().strip()
                    # OTHER CREATORS
                    url = outer_container_list[3].find('div', {'class': 'overflow-hidden full-width'}).find(
                        'a', {'class': 'optional-action-target-wrapper'}).get('href')
                    driver1.get(url)
                    time.sleep(0.5)
                    temp_src = driver1.page_source
                    temp_soup = BeautifulSoup(temp_src, 'lxml')
                    artdeco_model = temp_soup.find(
                        'div', {'class': 'artdeco-modal__content artdeco-modal__content--no-padding '
                                         'ember-view pvs-modal__content'})
                    other_creators_list = artdeco_model.find_all(
                        'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})
                    for k in other_creators_list:
                        temp_creator = k.find('span', {'class': 'mr1 t-bold'}).get_text().strip()
                        other_creators.append(temp_creator)

                else:
                    for k in outer_container_list:
                        # ASSOCIATED WITH
                        try:
                            temp = k.find('span', {'class': 'visually-hidden'}).get_text().strip()
                            if temp and temp.startswith(associated_with_str) and temp != other_creators_str:
                                associated_with = temp.replace(associated_with_str, '')
                                continue
                        except:
                            pass

                        # PROJECT  URL
                        try:
                            temp = k.find('div', {'class': 'pv2'}).find('a').get('href')
                            if temp:
                                project_url = temp
                                continue
                        except:
                            pass

                        # DESCRIPTION
                        try:
                            temp = k.find('span', {'class': 'visually-hidden'}).get_text().strip()
                            if temp and not temp.startswith(associated_with_str) and temp != other_creators_str:
                                description = temp
                                continue
                        except:
                            pass

                        # OTHER CREATORS
                        try:
                            url = k.find('div', {'class': 'overflow-hidden full-width'}).find(
                                'a', {'class': 'optional-action-target-wrapper'}).get('href')
                            if url:
                                driver1.get(url)
                                time.sleep(0.5)
                                temp_src = driver1.page_source
                                temp_soup = BeautifulSoup(temp_src, 'lxml')
                                artdeco_model = temp_soup.find(
                                    'div', {'class': 'artdeco-modal__content artdeco-modal__content--no-padding '
                                                     'ember-view pvs-modal__content'})
                                other_creators_list = artdeco_model.find_all(
                                    'li', {'class': 'pvs-list__paged-list-item artdeco-list__item '
                                                    'pvs-list__item--line-separated'})
                                for oc in other_creators_list:
                                    temp_creator = oc.find('span', {'class': 'mr1 t-bold'}).get_text().strip()
                                    other_creators.append(temp_creator)
                            continue
                        except:
                            pass
            except:
                pass

            projects.update({
                i: {
                    'Project_name': project_name,
                    'From': fromm,
                    'To': to,
                    'Associated_with': associated_with,
                    'Project_url': project_url,
                    'Description': description,
                    'Other_creators': other_creators,
                }
            })
        return projects

    # ADD "ASSOCIATED WITH", IF FOUND IN ANY PROFILE WITH PATENTS
    def get_patents(self, profile_url):
        url = profile_url + 'details/patents/'
        patents = {}
        associated_with_str = 'Associated with '

        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            nthn = soup.find('main', {'class': 'scaffold-layout__main'}).find(
                'div', {'class': 'pvs-list__container'}).find(
                'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'}).find(
                'h2').get_text().strip()
            if nthn == 'Nothing to see for now':
                patents = None
                return patents
        except AttributeError:
            pass

        patents_list = soup.find('div', {'class': 'pvs-list__container'}).find_all(
            'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        other_inventors_str = 'Other inventors'
        issued_filed = ['Issued ', 'Filed ']
        issued = issued_filed[0]
        filed = issued_filed[1]

        for i, j in enumerate(patents_list):
            big_display_flex = j.find('div', {'class': 'display-flex flex-column full-width align-self-center'})
            display_flex = big_display_flex.find('div', {'class': 'display-flex flex-row justify-space-between'})

            title = display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip()
            number_date = display_flex.find('span', {'class': 't-14 t-normal'}).find(
                'span', {'class': 'visually-hidden'}).get_text().strip().split(' · ')
            number = number_date[0]
            patent_status = None
            date = None
            if len(number_date) == 2:
                temp = number_date[1]
                if temp.startswith(issued):
                    patent_status = issued.strip()
                    date = temp.replace(issued, '')
                elif temp.startswith(filed):
                    patent_status = filed.strip()
                    date = temp.replace(filed, '')

            # associated_with = None
            patent_url = None
            description = None
            other_inventors = []
            driver1 = self.driver
            try:
                outer_container = big_display_flex.find('div', {'class': 'pvs-list__outer-container'})
                outer_container_list = outer_container.find_all('li', {'class': ''})

                for k in outer_container_list:
                    # PATENT URL
                    try:
                        temp = k.find('div', {'class': 'pv2'}).find('a').get('href')
                        if temp:
                            patent_url = temp
                            continue
                    except:
                        pass

                    # DESCRIPTION
                    try:
                        temp = k.find('span', {'class': 'visually-hidden'}).get_text().strip()
                        if temp and temp != other_inventors_str:
                            description = temp
                            continue
                    except:
                        pass

                    # OTHER INVENTORS
                    try:
                        temp = k.find('span', {'class': 'visually-hidden'}).get_text().strip()
                        if temp and temp == other_inventors_str:
                            url = k.find('a', {'class': 'optional-action-target-wrapper'}).get('href')
                            if url:
                                driver1.get(url)
                                time.sleep(0.5)
                                temp_src = driver1.page_source
                                temp_soup = BeautifulSoup(temp_src, 'lxml')
                                artdeco_model = temp_soup.find(
                                    'div', {'class': 'artdeco-modal__content artdeco-modal__content--no-padding '
                                                     'ember-view pvs-modal__content'})
                                other_inventors_list = artdeco_model.find_all(
                                    'li', {'class': 'pvs-list__paged-list-item artdeco-list__item '
                                                    'pvs-list__item--line-separated'})
                                for oi in other_inventors_list:
                                    temp_inventor = oi.find('span', {'class': 'mr1 t-bold'}).get_text().strip()
                                    other_inventors.append(temp_inventor)
                                continue
                    except:
                        pass
            except:
                pass

            patents.update({
                i: {
                    'Title': title,
                    'Number': number,
                    'Status': patent_status,
                    'Date': date,
                    'Patent_url': patent_url,
                    'Description': description,
                    'Other_inventors': other_inventors
                }
            })

        return patents

    def scrape(self, profile_url):

        data = {
            'Name': None,
            'Profile_picture_url': None,
            'Location': None,
            'Headline': None,
            'Contact_info_url': None,
            'No_Connections': None,
            'No_Followers': None,
            'About': None,
            'Experience': None,
            'Education': None,
            'Licenses & certifications': None,
            'Skills': None,
            'Languages': None,
            'Publications': None,
            'Honors & Awards': None,
            'Courses': None,
            'Recommendations': None,
            'Volunteering_experience': None,
            'Causes': None,
            'Featured': None,
            'Test_scores': None,
            'Organizations': None,
            'Projects': None,
            'Patents': None,
        }

        # driver = self.load_page(profile_url)
        self.load_page(profile_url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        try:
            profile_picture_url = self.get_profile_picture_url(profile_url)
            data['Profile_picture_url'] = profile_picture_url
        except Exception as e:
            raise e
        try:
            name = self.get_name(soup)
            data['Name'] = name
        except Exception as e:
            raise e
        try:
            location = self.get_location(soup)
            data['Location'] = location
        except Exception as e:
            raise e
        try:
            headline = self.get_headline(soup)
            data['Headline'] = headline
        except Exception as e:
            raise e
        try:
            contact_info_url = self.get_contact_info_url(soup)
            data['Contact_info_url'] = contact_info_url
        except Exception as e:
            raise e
        try:
            about = self.get_about(soup)
            data['About'] = about
        except Exception as e:
            raise e
        try:
            no_connections, no_followers = self.no_connections_followers(soup)
            data['No_Connections'] = no_connections
            data['No_Followers'] = no_followers
        except Exception as e:
            raise e
        try:
            experience = self.get_experience(profile_url)
            data['Experience'] = experience
        except Exception as e:
            raise e
        try:
            education = self.get_education(profile_url)
            data['Education'] = education
        except Exception as e:
            raise e
        try:
            certifications = self.get_certifications(profile_url)
            data['Licenses & certifications'] = certifications
        except Exception as e:
            raise e
        try:
            skills = self.get_skills(profile_url)
            data['Skills'] = skills
        except Exception as e:
            raise e
        try:
            languages = self.get_languages(profile_url)
            data['Languages'] = languages
        except Exception as e:
            raise e
        try:
            publications = self.get_publications(profile_url)
            data['Publications'] = publications
        except Exception as e:
            raise e
        try:
            honors_awards = self.get_honors_awards(profile_url)
            data['Honors & Awards'] = honors_awards
        except Exception as e:
            raise e
        try:
            courses = self.get_courses(profile_url)
            data['Courses'] = courses
        except Exception as e:
            raise e
        try:
            recommendations = self.get_recommendations(profile_url)
            data['Recommendations'] = recommendations
        except Exception as e:
            raise e
        try:
            volunteering_experience = self.get_volunteering_experience(profile_url)
            data['Volunteering_experience'] = volunteering_experience
        except Exception as e:
            raise e
        try:
            causes = self.get_causes(soup)
            data['Causes'] = causes
        except Exception as e:
            raise e
        try:
            featured = self.get_featured(profile_url)
            data['Featured'] = featured
        except Exception as e:
            raise e
        try:
            test_scores = self.get_test_scores(profile_url)
            data['Test_scores'] = test_scores
        except Exception as e:
            raise e
        try:
            organizations = self.get_organizations(profile_url)
            data['Organizations'] = organizations
        except Exception as e:
            raise e
        try:
            projects = self.get_projects(profile_url)
            data['Projects'] = projects
        except Exception as e:
            raise e
        try:
            patents = self.get_patents(profile_url)
            data['Patents'] = patents
        except Exception as e:
            raise e

        self.data = data

