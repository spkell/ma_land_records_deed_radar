############################################################################################
# Massacusetts Land Records Deed Radar
# 
# Produced by Sean Kelly
# v1.0
# Date: 5/8/20
#
# Currently supports Nantucket, Dukes, Suffolk, and Southern Bershire County
#
# Pre Conditions: have relatively recent deed stored in each deed_archive file
############################################################################################

#All counties in MA: https://www.norfolkdeeds.org/resources/other-ma-registries-of-deeds
def main():
  counties = ['Nantucket', 'Dukes', 'MiddlesexNorth', 'MiddlesexSouth', 'BerkSouth', 'Suffolk']
  for county in range(len(counties)):
    
    registry = 'http://www.masslandrecords.com/' + counties[county] +'/'
    archive_list = retrieve_deed_archive(counties[county])
    recent_date = archive_list[0][5]
    recent_page = archive_list[0][8]
    new_deeds = masslandrecords_deed_scraper_update(registry, recent_page, recent_date)
    day_arranged_list = county_deed_arrange(new_deeds)
    updated_list = reverse_deed_list_times(archive_list, day_arranged_list)
    store_deed_archive(counties[county], updated_list)
    write_to_csv(counties[county], updated_list)



#TODO: Switch time.sleep to selenium wait
#TODO: Switch xpath to css selector where possible for more robust code
#TODO: add condition to look for dates entered if input is given
#TODO: Use last (oldest) deed in archive to judge if deed can be added

#Returns raw list of deeds that are more recent than the previous most recent

def masslandrecords_deed_scraper_update(county_registry_url, recent_page, recent_date):

    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    import selenium
    import time
    wait_time = 1.75
    
    
    #Initialize list to store Deed Data
    street_address = ["Street_address"]
    town = ["Town"]
    parties = ["Parties"]
    document_num = ["document Number"]
    record_date = ["Recording Date"]
    record_time = ["Recording Time"]
    book_pages = ["Book Pages"]
    consideration = ["Consideration ($)"]
    document_status = ["Document Status"]
    
    
    # Return in case of exceptions
    empty_set = []
    
    
    #Open and Initialize Website
    """driver = webdriver.Chrome()
    driver.get(county_registry_url)
    driver.implicitly_wait(10)
    time.sleep(wait_time)"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)

    
    # Page Initiation Past Time Out Territory
    page_timeout = True
    while(page_timeout):
        page_timeout = False #Assume page will not crash during statements
        
        
        #Open Search Criteria Menu
        try:
            criteria = driver.find_element_by_id("Navigator1_SearchCriteria1_menuActiveSpace")
            criteria.click()
        except:
            print("Error: Failed To Open Search Menu")
            page_timeout = True


        #Select Recorded Land -> Recorded Date Search
        try:
            date_search = driver.find_element_by_id("Navigator1_SearchCriteria1_LinkButton04")
            date_search.click()
        except:
            print("Error: Failed To Select Recorded Date Search")
            page_timeout = True


        time. sleep(wait_time)


        #Enter Start Date
        try:
            start_date = driver.find_element_by_xpath("//input[@name='SearchFormEx1$ACSTextBox_DateFrom']")
            start_date.click()
            for i in range(2):
                start_date.send_keys(Keys.ARROW_RIGHT)
            for i in range(10):
                start_date.send_keys(Keys.BACKSPACE)
            start_date.send_keys("4/28/2020")
        except:
            page_timeout = True

        #Enter End Date
        try:
            end_date = driver.find_element_by_xpath("//input[@name='SearchFormEx1$ACSTextBox_DateTo']")
            end_date.click()
            for i in range(2):
                end_date.send_keys(Keys.ARROW_RIGHT)
            for i in range(10):
                end_date.send_keys(Keys.BACKSPACE)
            end_date.send_keys("5/4/2020")
        except:
            page_timeout = True
            
        if(page_timeout):
            driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'r')


    #Select DEED as document type
    from selenium.webdriver.support.ui import Select
    select_deed = Select(driver.find_element_by_id('SearchFormEx1_ACSDropDownList_DocumentType'))
    select_deed.select_by_visible_text("DEED")


    #Initiate Deed Search
    search = driver.find_element_by_xpath("//input[@name='SearchFormEx1$btnSearch']")
    search.click()


    """#Show 100 Deeds/Page
    try:
        show_100 = driver.find_element_by_id('DocList1_PageView100Btn')
        show_100.click()
    except:
        pass"""


    #Sorts Deed Entries by Most Recent, time inverted
    time.sleep(wait_time)
    sort_date = driver.find_element_by_xpath('//*[@id="DocList1_ContentContainer1"]/table/tbody/tr[1]/td/div/div[1]/table/thead/tr/th[2]/a[1]')
    sort_date.click()


    ################################### END PAGE INITIALIZATION ###################################
    
    # Loops through each page containing deed entries
    page_ct = 0
    total_page_list = driver.find_elements_by_xpath("/html/body/form/div[4]/div[27]/div[1]/div[2]/table/tbody/tr[1]/td/div/div[3]/table/tbody/tr/td[3]/a")
    for page in total_page_list:
        
        
        # Initializes raw deed list for the given page
        page_ct = page_ct + 1
        time.sleep(wait_time)
        raw_deed_list = driver.find_elements_by_css_selector('#DocList1_ContentContainer1 > table > tbody > tr:nth-child(1) > td > div > div:nth-child(2) > table > tbody > tr')
        
        
        # Loops through each deed entry on page
        for entry in range(len(raw_deed_list)):
            
            
            # Determines page of current deed
            deed_pages_str = "//*[@id='DocList1_ContentContainer1']/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr[" + str(entry+1) + "]/td[3]"
            deed_pages = driver.find_element_by_xpath(deed_pages_str)
            current_deed_pages = deed_pages.text
            current_deed_pages_arr = current_deed_pages.split("/")
            
            
            # Determines date of current deed
            deed_date_str = "//*[@id='DocList1_ContentContainer1']/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr[" + str(entry+1) + "]/td[2]"
            deed_date = driver.find_element_by_xpath(deed_date_str)
            current_deed_date = deed_date.text
            current_deed_date_arr = current_deed_date.split("/")
            
            
            # Most recent day and pages from previous archives
            most_recent_deed_pages = recent_page.split("/") #declare as constant
            most_recent_deed_date = recent_date.split("/") #declare as constant
            
            
            # Returns list if deed is older than the most recent from the archive
            if (int(current_deed_date_arr[2]) < int(most_recent_deed_date[2]) #Different year
                or int(current_deed_date_arr[0]) < int(most_recent_deed_date[0]) #Different month
                or ( int(current_deed_date_arr[0]) == int(most_recent_deed_date[0]) #Same month, different day
                and int(current_deed_date_arr[1]) < int(most_recent_deed_date[1])) ):
                deed_list = [street_address,town,parties,consideration,document_status,record_date,record_time,document_num,book_pages]
                driver.close()
                return deed_list #Only returns new entries           
            
            
            # Skip all deeds from current day that are older than current deed
            if (int(current_deed_pages_arr[0]) < int(most_recent_deed_pages[0]) #Different page index
                or int(current_deed_pages_arr[0]) == int(most_recent_deed_pages[0]) #Same page index, different entry
                and int(current_deed_pages_arr[1]) <= int(most_recent_deed_pages[1])):
                pass
            
            
            # Record Deed Entry
            else:
                
                #Record town
                stale = True
                while(stale):
                    try:
                        deed_town_str = "//*[@id='DocList1_ContentContainer1']/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr[" + str(entry+1) + "]/td[5]"
                        deed_town_info = driver.find_element_by_xpath(deed_town_str)
                        town.append(deed_town_info.text)
                        stale = False
                    except:
                        print("Error: Stale Town Reference")
                        pass

                
                time.sleep(wait_time)

                
                #Opens deed entry
                stale = True
                while(stale):
                    try:
                        open_deed_str = "//*[@id='DocList1_ContentContainer1']/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr[" + str(entry+1) + "]/td[6]/a"
                        open_deed = driver.find_element_by_xpath(open_deed_str)
                        open_deed.click()
                        stale = False
                    except:
                        print("Error: Open Deed Click Exception")
                        pass

                    
                #TODO: Allows the page to register open the new deed window, may be better to use Selenium waits instead
                time.sleep(wait_time)

                
                #Record deed info from table
                deed_info = driver.find_elements_by_xpath("//*[@id='DocDetails1_GridView_Details']/tbody/tr[2]/td")      
                deed_info_comps = []
                stale = True
                while(stale):
                    deed_info_comps = []
                    for elm in deed_info:
                        try:
                            deed_info_comps.append(elm.text)
                            stale = False
                        except:
                            print("Error: Deed Info Failure")
                            pass
                document_num.append(deed_info_comps[0])
                record_date.append(deed_info_comps[1])
                record_time.append(deed_info_comps[2])
                book_pages.append(deed_info_comps[5])            
                consideration.append(deed_info_comps[6])
                document_status.append(deed_info_comps[7])

                
                #Records deed address from table
                deed_multi_address = driver.find_elements_by_xpath("//*[@id='DocDetails1_GridView_Property']/tbody/tr")
                deed_address_temp = []
                address_present = True
                for i in range(len(deed_multi_address)):
                    deed_address_path = "//*[@id='DocDetails1_GridView_Property']/tbody/tr[" + str(i+1) + "]"
                    deed_address = driver.find_elements_by_xpath(deed_address_path)
                    for entry in deed_address:
                        address_temp = entry.text
                    try:
                        deed_address_temp.append(address_temp)
                    except: #Sometimes address isn't listed
                        print("Error: Deed address not detected")
                        address_present = False
                if(address_present):
                    try:
                        del deed_address_temp[0]
                    except:
                        print("Error: First Address Not Present")
                        pass
                    street_address_comps = []
                if (len(deed_address_temp) > 0):
                    for i in range(len(deed_address_temp)):
                        street_address_comps.append(deed_address_temp[i])
                    street_address.append(street_address_comps)
                else:
                    street_address.append('N/A')

                    
                #Prints Grantors (sellers) and Grantees (Buyers)
                deed_parties = driver.find_elements_by_xpath("//*[@id='DocDetails1_GridView_GrantorGrantee']/tbody/tr")
                parties_temp = []
                emptySet = 1
                for elm in deed_parties:
                    if (emptySet == 1):
                        emptySet = 0
                    else:
                        stale = True
                        while(stale):
                            try:
                                parties_temp.append(elm.text)
                                stale = False
                            except:
                                print("Error: Append Parties Failure")
                                pass
                parties.append(parties_temp)
            
        #Go to next page
        if (page_ct < len(total_page_list)):
            stale = True
            while(stale):
                select_next_page = driver.find_element_by_id('DocList1_LinkButtonNext')
                try:
                    select_next_page.click()
                    stale = False
                except:
                    print("Error: Next Page Failure")
                    pass
        
    deed_list = [street_address,town,parties,consideration,document_status,record_date,record_time,document_num,book_pages]
    driver.close()
    return deed_list
#END masslandrecords_deed_scraper_update()


# Takes in raw list of deed info from the scraper() function
# Returns deeds as separate objects

def county_deed_arrange(raw_deed_list):
    day_arranged_list = []
    for j in range(len(raw_deed_list[0])):
        deed_entries = []
        for k in range(len(raw_deed_list)):
            deed_entries.append(raw_deed_list[k][j])
        day_arranged_list.append(deed_entries)
    return day_arranged_list
#END county_deed_arrange()


# Takes in archive of county deed history, and blocks of new deeds to add to it.
# Reverses the order of deeds on each day since the times are inverted

def reverse_deed_list_times(archive_list, day_arranged_list):

    new_day = []
    sorting_dates = []

    for deed in range(len(day_arranged_list)-1):
        date_list_unplaced = day_arranged_list[deed+1][5].split("/")
        appended = False

        for date in range(len(sorting_dates)):
            date_list_placed = sorting_dates[date][0][5].split("/")

            if date_list_unplaced[2] == date_list_placed[2]:
                if date_list_unplaced[0] == date_list_placed[0]:
                    if date_list_unplaced[1] == date_list_placed[1]:
                        sorting_dates[date].append(day_arranged_list[deed+1])
                        appended = True

        if (appended == False):
            new_day = []
            new_day.append(day_arranged_list[deed+1])
            sorting_dates.append(new_day)

    for i in range(len(sorting_dates)):
        for j in range(len(sorting_dates[len(sorting_dates)-i-1])):
            archive_list.insert(0, sorting_dates[len(sorting_dates)-i-1][j])
    
    return archive_list
#END reverse_deed_list_times()



# Takes name of county and its new deed entries, and stores them in a list

def store_deed_archive(county_name, archive_list):
    import pickle
    archive_path = 'deed_archives/' + county_name + '_archive_list' ###DEBUG so I dont delete whole list
    with open(archive_path, 'wb') as f:
        pickle.dump(archive_list, f)
#END store_deed_archive()



# Takes name of county and returns the archived list for it

def retrieve_deed_archive(county_name):
    import pickle
    archive_path = 'deed_archives/' + county_name + '_archive_list'
    with open(archive_path, 'rb') as f:
         mylist = pickle.load(f)
    return mylist   
#END retrieve_deed_archive()


# Takes name of county and its archive list, and writes them to a tabled csv file
def write_to_csv(county_name, archive_list):
    import csv
    csv_county_path = 'public/recent_deeds/' + county_name + '_recent_deeds.csv'
    with open(csv_county_path, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['Street_address', 'Town', 'Parties', 'Consideration ($)', 'Document Status', 'Recording Date', 'Recording Time', 'document Number', 'Book Pages']
        writer.writerow(header)
        for deed in range(len(archive_list)):
            writer.writerow(archive_list[deed])
#END write_to_csv()