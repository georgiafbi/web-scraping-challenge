from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import os
import pandas as pd
import requests
from pprint import pprint
import time
import pymongo


# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

def scrape_info():
    # Setup splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    browser.driver.maximize_window()
    #definition returns html soup
    def soup(u1="", u2=""):
        browser.visit(u1+u2)
        browser.driver.maximize_window()
        time.sleep(2)
        html=browser.html
        return BeautifulSoup(html,'html.parser')
    # URL of page to be scraped
    url = "https://mars.nasa.gov/news/"


    # Create BeautifulSoup object; parse with 'html.parser'
    text_soup=soup(url)
    results = text_soup.find_all('li', class_='slide')

    # Loop through returned results
    mars_news_collection = []
    for result in results:
        # error handling
        try:
            # identify and return "rollover_description_inner" of listing
            news_p = result.find('div', class_="article_teaser_body").text
            # print(news_p)
            # identify and return news title of listing
            news_title = result.find('div', class_='content_title').text
            # Print results only if news_title, and news_p
            if (news_title and news_p):
                mars_news_dict = {'news_title': news_title, 'news_p': news_p}
                mars_news_collection.append(mars_news_dict)
                print('-------------')
                print(news_title)
                print(news_p)
        except AttributeError as e:
            print(e)


    mars_image_url = 'https://www.jpl.nasa.gov/images?search=&category=Mars'
    browser.driver.maximize_window()
    browser.visit(mars_image_url)
    time.sleep(2)
    xpath = '/html/body/div/div/div/header/div[1]/div[3]/div/nav/div[1]/div[4]/button'
    browser.find_by_xpath(xpath).click()
    time.sleep(4)
    super_html = browser.html

    featured_img_soup = BeautifulSoup(super_html, 'html.parser')

    featured_img = featured_img_soup.find_all('div', class_='col-span-3')
    super_cam_url = featured_img[0].find('a')['href']

    supercam_img_soup = soup(f'https://www.jpl.nasa.gov{super_cam_url}')
    supercam_img_id = supercam_img_soup.find('div', id='82498')

    supercam_img_url = supercam_img_id.find('img')["srcset"].split()[-2]
    supercam_text=supercam_img_soup.find('h1',class_='text-h2').text
    print(supercam_text)
    print(supercam_img_url)
    time.sleep(2)

### JPL Mars Space Images - Featured Image

# * Visit the url for JPL Featured Space Image [here](2 ).

# * Use splinter to navigate the site and find the image url for the current Featured Mars Image and assign the url string to a variable called `featured_image_url`.

# * Make sure to find the image url to the full size `.jpg` image.

# * Make sure to save a complete url string for this image.
    base_url='https://www.jpl.nasa.gov'
    mars_url = '/images?search=&category=Mars'
    #ensures window opens to its maximum size
    browser.driver.maximize_window()
    #visits first web page
    browser.visit(base_url+mars_url)
    #gives time for the browser to load
    time.sleep(2)

    #checks the Mars topic
    browser.find_by_css("input[id=filter_Mars]").first.click()
    time.sleep(2)

    #gets the html code of the page
    html2=browser.html
    time.sleep(2)
    #turns the html into beautiful soup
    mars_topic_soup=BeautifulSoup(html2,'html.parser')

    #returns a list of mars topic images on this visited webpage
    search_listing_page_results=mars_topic_soup.find_all('div',class_="SearchResultCard")[0]
    #concatenates base_url with image url
    first_mars_topic_img_url=base_url+search_listing_page_results.a['href']
    #gets title
    first_mars_topic_img_title=search_listing_page_results.h2.text
    print(first_mars_topic_img_url)
    print(first_mars_topic_img_title)

    #visits the nasa page with the high resolution URL
    browser.visit(first_mars_topic_img_url)
    time.sleep(2)
    #get the html code for that high resolution url page
    html3=browser.html
    #turns that html code into some beautiful soup
    high_res_soup=BeautifulSoup(html3,'html.parser')
    #concatenates base_url with high resolution link
    featured_img_url=high_res_soup.find_all('img',class_='BaseImage')[0]['srcset'].split()[-2]

    # Visit the Mars Facts webpage [here](https://space-facts.com/mars/)
    # and use Pandas to scrape the table containing facts about the planet including Diameter, Mass, etc.
    mars_facts_url = "https://space-facts.com/mars/"
    browser.visit(mars_facts_url)
    time.sleep(2)
    # Use Pandas to convert the data to a HTML table string.
    tables = pd.read_html(mars_facts_url)

    df = tables[0]
    mars_facts_table = df.rename(
        columns={0: "Description", 1: "Mars"}).set_index("Description")
    print(mars_facts_table)
    html_mars_facts_table = mars_facts_table.to_html()

    html_table_string = html_mars_facts_table.replace("\n", '')
    print(html_table_string)
    # mars_facts_table.to_html('templates/mars_facts_table.html')

    usgs_ext = "/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    usgs_url = "https://astrogeology.usgs.gov"
    browser.visit(usgs_url+usgs_ext)
    time.sleep(2)
    mars_usgs_html = browser.html
    usgs_soup = BeautifulSoup(mars_usgs_html, "html.parser")

    mars_image_soup = usgs_soup.find_all('div', class_='description')

    hemisphere_image_urls = []
    for link in mars_image_soup:
        full_img_link = link.find('a')['href']
        title = link.h3.text.replace(' Enhanced', '')
        
        hemi_soup=soup(usgs_url,full_img_link)

        wide_image_url = hemi_soup.find('img', class_='wide-image')['src']
        img_url = usgs_url+wide_image_url
        hemisphere_image_urls.append({"title": title, "img_url": img_url})
        print(img_url)
    
    featured_img_url=[{"ftitle": first_mars_topic_img_title, "fimg_url": featured_img_url},{"ftitle": supercam_text, "fimg_url": supercam_img_url}]
    mars_dict = {'news_title': mars_news_collection[0]['news_title'], 'news_p': mars_news_collection[0]['news_p'],
                 'featured_img_url': featured_img_url, 'mars_facts': html_table_string, 'hemisphere_image_urls': hemisphere_image_urls
                 }
    
    browser.quit()

    return mars_dict

