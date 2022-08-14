import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
import time
# import sys


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

    def load_page(self, url):
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
            if round(end - start) > 5:
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
            Contact_info_url = panel.find('a', {
                'class': 'ember-view link-without-visited-state cursor-pointer text-heading-small inline-block break-words'}).get(
                'href')
            return Contact_info_url
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

    def get_experience(self, profile_url):
        url = profile_url + 'details/experience/'
        exp_list = []
        experiences = {}

        self.driver.get(url)
        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        exp_list = soup.find_all('li', {
            'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        try:
            nthn = exp_list[0].find(
                'h2',
                {'class':
                     'artdeco-empty-state__headline artdeco-empty-state__headline--mercado-empty-room-large artdeco-empty-state__headline--mercado-spots-large'}).get_text().strip()
            if nthn == 'Nothing to see for now':
                experiences = None
                return experiences
        except:
            pass

        # HANDLE EDGE CASE FOR https://www.linkedin.com/in/sandraaclark/details/experience/
        counter = 0
        for i, j in enumerate(exp_list):
            # try:
            #     inner_list = j.find_all('li', {'class': 'pvs-list__paged-list-item'})
            #     for k in inner_list:
            #         inner_display_flex = k.find('div', {'class': 'display-flex flex-row justify-space-between'})
            #         inner_outer_container = k.find('div', {'class': 'pvs-list__outer-container'})
            #
            #         # inner
            #         title = inner_display_flex.find('div', {'class': 'display-flex align-items-center'}).find(
            #             'span', {'class': 'visually-hidden'}).get_text().strip()
            #         date_place = inner_display_flex.find_all('span', {'class': 't-14 t-normal t-black--light'})
            #
            #         dates = date_place[0].find('span', {'class': 'visually-hidden'}).get_text().strip().split(' · ')
            #         from_to = dates[0].split(' - ')
            #         if len(date_place) == 2:
            #             duration = dates[1]
            #             location = date_place[1].find('span', {'class': 'visually-hidden'}).get_text().strip()
            #         else:
            #             duration = dates[1]
            #             location = None
            #         if len(from_to) == 2:
            #             fromm = from_to[0]
            #             to = from_to[1]
            #         else:
            #             fromm = from_to[0]
            #             to = None
            #
            #         about_skills_media = inner_outer_container.find_all('li', {'class': ''})
            #
            #         if len(about_skills_media) == 3:
            #             description = about_skills_media[0].find(
            #                 'span', {'class': 'visually-hidden'}).get_text().strip()
            #             skills = about_skills_media[1].find(
            #                 'span', {'class': ''}).get_text().strip()
            #
            #             medias = about_skills_media[2].find_all(
            #                 'li', {'class': 'pvs-list__item--with-top-padding'})
            #             media_links = []
            #             for media in medias:
            #                 temp = media.find('a', {'class': 'optional-action-target-wrapper'}).get('href')
            #                 media_links.append(temp)
                    # SOLVE THIS FUCKING SHIT
                    # elif len(about_skills_media) == 2:
                        # temp0 = about_skills_media[0]
                        # temp1 = about_skills_media[1]
                        #
                        # skills0 = temp0[1].find(
                        #     'span', {'class': ''}).get_text().strip()
                        # skills1 = temp1[1].find(
                        #     'span', {'class': ''}).get_text().strip()
                        # if skills0.find('Skills:'):
                        #     skills = skills0
                        # elif skills1.find('Skills:'):
                        #     skills = skills1
                        # else:
                        #     skills = None
                        #
                        # medias0 = temp0.find_all(
                        #     'li', {'class': 'pvs-list__item--with-top-padding'})
                        # medias1 = temp1.find_all(
                        #     'li', {'class': 'pvs-list__item--with-top-padding'})
                        # media_links = []
                        # if medias0:
                        #     for media in medias0:
                        #         temp = media.find('a', {'class': 'optional-action-target-wrapper'}).get('href')
                        #         media_links.append(temp)
                        # elif medias1:
                        #     for media in medias1:
                        #         temp = media.find('a', {'class': 'optional-action-target-wrapper'}).get('href')
                        #         media_links.append(temp)


                    # 'Skills:'
                    # media by href
            #
            # except:
            #     pass

            display_flex = j.find('div', {'class': 'display-flex flex-row justify-space-between'})
            title = display_flex.find('div', {'class': 'display-flex align-items-center'}).find('span', {
                'class': 'visually-hidden'}).get_text().strip()

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
                dates = temp[0].find('span', {'class': 'visually-hidden'}).get_text().strip().split(' · ')
                from_to = dates[0].split(' - ')
                if len(from_to) == 2:
                    fromm = from_to[0]
                    to = from_to[1]
                else:
                    fromm = from_to[0]
                    to = None
                duration = dates[1]
                location = temp[1].find('span', {'class': 'visually-hidden'}).get_text().strip()
            else:
                dates = temp[0].find('span', {'class': 'visually-hidden'}).get_text().strip().split(' · ')
                from_to = dates[0].split(' - ')
                if len(from_to) == 2:
                    fromm = from_to[0]
                    to = from_to[1]
                else:
                    fromm = from_to[0]
                    to = None
                duration = dates[1]
                location = None

            try:
                outer_container = j.find('div', {'class': 'pvs-list__outer-container'})
                description = outer_container.find('span', {'class': 'visually-hidden'}).get_text().strip()
            except AttributeError:
                description = None

            experiences.update({
                i: {
                    'Title': title,
                    'Company': company_name,
                    'Employment_type': employment_type,
                    'From': fromm,
                    'To': to,
                    'Duration': duration,
                    'Location': location,
                    'Description': description,
                }
            })
        return experiences

    def get_education(self, profile_url):
        url = profile_url + 'details/education/'
        edu_list = []
        educations = {}

        # self.driver.get(url)
        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        edu_list = soup.find_all('li', {
            'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})
        for i, j in enumerate(edu_list):
            try:
                nthn = j.find(
                    'h2',
                    {'class':
                         'artdeco-empty-state__headline artdeco-empty-state__headline--mercado-empty-room-large artdeco-empty-state__headline--mercado-spots-large'}).get_text().strip()
                if nthn == 'Nothing to see for now':
                    educations = None
                    return educations
            except:
                pass
            try:
                nthn = j.find('h2').get_text().strip()
                if nthn == 'Nothing to see for now':
                    educations = None
                    return educations
            except AttributeError:
                pass

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
                    except AttributeError:
                        pass
                    if li[0] in temp:
                        temp = temp.replace(li[0], '')
                        grade = temp
                    elif li[1] in temp:
                        temp = temp.replace(li[1], '')
                        activities_societies = temp
                    else:
                        description = temp
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

    def get_certifications(self, profile_url):
        url = profile_url + 'details/certifications/'
        cer_list = []
        certifications = {}

        # self.driver.get(url)
        self.load_page(url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        cer_list = soup.find_all('li', {
            'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

        for i, j in enumerate(cer_list):
            try:
                nthn = j.find('h2').get_text().strip()
                if nthn == 'Nothing to see for now':
                    certifications = None
                    return certifications
            except AttributeError:
                pass

            display_flex = j.find('div', {'class': 'display-flex flex-row justify-space-between'})
            try:
                link = j.find('a', {'class': 'optional-action-target-wrapper display-flex flex-column full-width'}).get(
                    'href')
            except AttributeError:
                link = None
                pass

            name = display_flex.find('div', {'class': 'display-flex align-items-center'}).find('span', {
                'class': 'visually-hidden'}).get_text().strip()
            Issuing_organization = display_flex.find('span', {'class': 't-14 t-normal'}).find('span', {
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
            except Exception as e:
                raise e

            certifications.update({
                i: {
                    'Name': name,
                    'Link': link,
                    'Issuing_organization': Issuing_organization,
                    'Issue_date': issue_date,
                    'Expiry_date': expiry_date,
                    'Credential_ID': credential_id,
                }})

        return certifications

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

                        while True:
                            try:
                                element = driver1.find_element(By.XPATH,
                                                               '/html/body/div[3]/div/div/div[2]/div/div[2]/div/div/div[2]/div/button')
                                element.click()
                                time.sleep(0.25)
                            except selenium.common.exceptions.NoSuchElementException:
                                break
                            except selenium.common.exceptions.StaleElementReferenceException:
                                False

                        src2 = driver1.page_source
                        soup2 = BeautifulSoup(src2)
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
            nthn = soup.find('section', {'class': 'artdeco-card ember-view pb3'}).find(
                'h2', {
                    'class': 'artdeco-empty-state__headline artdeco-empty-state__headline--mercado-empty-room-large '
                             'artdeco-empty-state__headline--mercado-spots-large'}).get_text().strip()
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

    # Other authors work needs heavy work to be done. later
    def get_publications(self,  profile_url):
        url = profile_url + 'details/publications/'
        publications = {}
        months = ['Jan ', 'Feb ', 'Mar ', 'Apr ',
                  'May ', 'Jun ', 'Jul ', 'Aug ',
                  'Sep ', 'Oct ', 'Nov ', 'Dec ']

        self.load_page(url)
        src = self.driver.page_source
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
                    if months in publisher_date[0]:
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
            outer_container = j.find('div', {'class': 'pvs-list__outer-container'})
            outer_container_list = outer_container.find_all('li', {'class': ''})
            other_authors = []
            driver1 = self.driver

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
                    'li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated '})
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
                except:
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
                except:
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
                except:
                    pass

            elif len(outer_container_list) == 1:
                try:
                    temp = outer_container_list[0].find('span', {'class': 'visually-hidden'}).get_text().strip()
                    if temp:
                        description = outer_container_list[0].find('span', {'class': 'visually-hidden'}).get_text().strip()
                except:
                    pass
                try:
                    temp = outer_container_list[0].find('div', {'class': 'pv2'}).find('a').get('href')
                    if temp:
                        publication_url = outer_container_list[0].find('div', {'class': 'pv2'}).find('a').get('href')
                except:
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
                        {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated '})
                    for k in other_authors_list:
                        temp_author = k.find('span', {'class': 'mr1 t-bold'}).get_text().strip()
                        other_authors.append(temp_author)
                except:
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

    def scrape(self, profile_url):

        data = {
            'Name': None,
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

        }

        # driver = self.load_page(profile_url)
        self.load_page(profile_url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        # try:
        #     name = self.get_name(soup)
        #     data['Name'] = name
        # except Exception as e:
        #     raise e
        # try:
        #     location = self.get_location(soup)
        #     data['Location'] = location
        # except Exception as e:
        #     raise e
        # try:
        #     headline = self.get_headline(soup)
        #     data['Headline'] = headline
        # except Exception as e:
        #     raise e
        # try:
        #     contact_info_url = self.get_contact_info_url(soup)
        #     data['Contact_info_url'] = contact_info_url
        # except Exception as e:
        #     raise e
        # try:
        #     about = self.get_about(soup)
        #     data['About'] = about
        # except Exception as e:
        #     raise e
        # try:
        #     no_connections, no_followers = self.no_connections_followers(soup)
        #     data['No_Connections'] = no_connections
        #     data['No_Followers'] = no_followers
        # except Exception as e:
        #     raise e
        # try:
        #     experience = self.get_experience(profile_url)
        #     data['Experience'] = experience
        # except Exception as e:
        #     raise e
        # try:
        #     education = self.get_education(profile_url)
        #     data['Education'] = education
        # except Exception as e:
        #     raise e
        # try:
        #     certifications = self.get_certifications(profile_url)
        #     data['Licenses & certifications'] = certifications
        # except Exception as e:
        #     raise e
        # try:
        #     skills = self.get_skills(profile_url)
        #     data['Skills'] = skills
        # except Exception as e:
        #     raise e
        # try:
        #     languages = self.get_languages(profile_url)
        #     data['Languages'] = languages
        # except Exception as e:
        #     raise e
        try:
            publications = self.get_publications(profile_url)
            data['Publications'] = publications
        except Exception as e:
            raise e

        self.data = data
