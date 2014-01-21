import mechanize;
import BeautifulSoup
import time
import datetime
import urlparse

__author__ = 'Adriaan'
#User input
nickname = raw_input('Enter your nickname: ')
password = raw_input('Enter your password: ')
i = str(raw_input('Enter timestamp (2013, 01, 01 00:00): '))
#Get the time datetime value from raw input
try:
    dt_start = datetime.datetime.strptime(i, '%Y, %m, %d %H:%M')
except ValueError:
    print "Incorrect format"
#Browser define
br = mechanize.Browser();
#Cookie Jar for cookies
cj = mechanize.CookieJar();
br.set_cookiejar(cj)
#Browser Options
br.set_handle_equiv(True)
#GZip is experimental either uncomment or use as browser option
#br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(True)
# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
# The site we will navigate into, handling it's session
br.open('http://slashdot.org/')
# Select the login form
br.select_form(nr=1)
# User credentials
br.form['unickname'] = nickname
br.form['upasswd'] = password
# Login
try:
    #Login using form and credentials
    br.submit()
except ValueError:
    print('Login Submission error')
try:
    #Read the browser response from form submission and make your soup using BS
    html = br.response().read()
    soup = BeautifulSoup.BeautifulSoup(html)
    #Get the current url to valuate if your login was succesfull
    #in this case if the url is 'http://slashdot.org/' the your login worked if its 'https://slashdot.org/my/login'
    #the your login failed and you where returned to the login page
    browserUrl = br.geturl()
except ValueError:
    print('Error geting soup or current url')

#this string contains the final list of stories to print
resultString = ''

if 'http://slashdot.org/' in browserUrl.lower():
    print('Logged In')
    #get the older button
    olderAhref = soup.find("a", { "class" : "prevnextbutact" })
    #only read the page while the second button found on html does not contain the word Newer
    while 'Newer' not in olderAhref.getText():
        try:
            #Join url to pass to browser for next page to inspect
            urlNext = urlparse.urljoin('http:', olderAhref['href'], allow_fragments=True)
            olderAhref['absolute_url']= urlNext
            #get all spans with a id that startswith 'title-'
            storyIds = soup.findAll("h2", { "class" : "story"})
            #loop through id to get the details of the story
            for storyid in storyIds:
                sid = storyid.span['id']
                sdid = 'details-' + sid[6:]
                stid = 'fhtime-' + sid[6:]
                storyDetail = soup.find('div', id=sdid)
                storyDateTime = soup.find('time', id=stid)
                storyTitle = storyid.a.getText()
                storyAuthor = storyDetail.a.getText()
                storyTime = storyDateTime.getText()
                subTimeShrt = storyTime[3:-2]
                strTime = subTimeShrt.replace("@", "")
                formatedTime = time.mktime(datetime.datetime.strptime(strTime, "%A %B %d, %Y %H:%M").timetuple())
                strFormatedTime = str(formatedTime)
                #if the story is older than our entered date then it must be added to the list of stories in the resulting string
                if dt_start > datetime.datetime.strptime(strTime, "%A %B %d, %Y %H:%M"):
                    print("Adding Story :" +storyTitle)
                    resultString = resultString + ' {\n headline: ' + storyTitle + ',\n author: ' + storyAuthor + ',\n date: ' + strFormatedTime + '\n },\n'
#We have the next url to follow and have got all the older stories now to open that page and read then soup it up
            #cut the last trailing comma from the story list
            storyList = resultString[:-2]
            #print the story list with square brackets enclosing it
            if len(storyList) > 1:
                print('[\n' + storyList + '\n]')
            resultString = ""
            br.open(urlNext)
            html = br.response().read()
            soup = BeautifulSoup.BeautifulSoup(html)
            #Here we find the older control button
            olderAhref = soup.findAll("a", { "class" : "prevnextbutact" })[1]

            if 'Newer' in olderAhref.getText():
                break
        except ValueError:
            print('Error in passing older pages')
#handle invalid login
elif 'https://slashdot.org/my/login' in browserUrl.lower():
    print('Login Failed')
#Close Browser
br.close()

