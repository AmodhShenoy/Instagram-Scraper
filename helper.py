import subprocess
import string,secrets,random,os,time,importlib
import sys
from pathlib import Path

###############################################################
#
#	PACKAGE INSTALLER FUNCTIONS
#
###############################################################

def install_pip(log=None):
   # log("Installing pip, the standard Python Package Manager, first")
    from os     import remove
    from urllib import urlretrieve
    urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
    subprocess.call(["python", "get-pip.py"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    remove("get-pip.py")

def get_pip(log=None):
    from os.path import isfile, join
    from sys     import prefix
    pipPath = join(prefix, 'Scripts', 'pip.exe')
    if not isfile(pipPath):
        install_pip(log)
        if not isfile(pipPath):
            raise("Failed to find or install pip!")
    return pipPath

def install_package(name, pip_name=None, notes="", log=None):
    from pkgutil import iter_modules
    from sys import prefix
    try:
    	pip=get_pip(log)
    except:
    	if getos()=='mac':
    		pip=str(Path(prefix).parent.parent.joinpath('shims','pip3'))
    	else:
    		pip=str(os.system('which pip3'))
    if name not in [tuple_[1] for tuple_ in iter_modules()]:
        #log("Installing " + name + notes + " Library for Python")
        subprocess.call([pip, "install", pip_name if pip_name else name], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def getos():
	platform=sys.platform
	if 'linux' in platform:
		return 'linux'
	elif 'win' in platform:
		return 'windows'
	else:
		return 'mac'

###############################################################
#
#	WEBDRIVER FUNCTIONS 
#
#	Useful definitions:
#	1) Headless - Browser instance without a GUI
#	2) Lite - Browser instance without does not load images and CSS
#
#
###############################################################

class BrowserHandler():
	def __init__(self):
		install_package('selenium')
		self.Select=importlib.import_module('selenium.webdriver.support.ui').Select
		self.webdriver=importlib.import_module('selenium.webdriver')
		self.Options=importlib.import_module('selenium.webdriver.firefox.options').Options
		self.Keys=importlib.import_module('selenium.webdriver.common.keys').Keys
		self.ActionsChains=importlib.import_module('selenium.webdriver.common.action_chains').ActionChains

	def get_screenshot(self,browser,element,filename):
		install_package('Pillow')
		from PIL import Image
		from io import BytesIO
		location = element.location
		size = element.size
		png = browser.get_screenshot_as_png() # saves screenshot of entire page

		im = Image.open(BytesIO(png)) # uses PIL library to open image in memory

		left = location['x']
		top = location['y']
		right = location['x'] + size['width']
		bottom = location['y'] + size['height']

		im = im.crop((left, top, right, bottom)) # defines crop points
		im.save(filename) # saves new cropped image

	def chrome(self,lite=False,headless=False,proxy=False,incognito=False,host="",port="",login="",password=""):
		PROXY=host+':'+port
		chrome_options = self.webdriver.ChromeOptions()

		if proxy:
			chrome_options.add_argument('--proxy-server=http://%s' % PROXY)

		if incognito:
			chrome_options.add_argument("--incognito")

		if lite:
			chrome_options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.image': 2})
			chrome_options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.stylesheet': 2})

		if headless:
			chrome_options.add_argument('--disable-gpu') 
			chrome_options.headless = True

		browser=self.webdriver.Chrome(executable_path=str(Path.joinpath(Path.cwd(),'common',getos(),'chromedriver')),chrome_options=chrome_options)
		#Proxy works only with windows!
		if login or password:
			subprocess.Popen([str(Path.joinpath(Path.cwd(),'common','chrome_proxy.exe')),login,password])
			browser.get("https://www.google.com")
			browser.get("http://amibehindaproxy.com/")
			

		return browser
	
	def firefox(self,lite=False,location_access=True,headless=False,proxy=False,incognito=False,host="",port="",login="",password=""):
		profile = self.webdriver.FirefoxProfile()
		options = self.Options()
		if proxy:
			profile.set_preference("network.proxy.type", 1)
			profile.set_preference("network.proxy.http", host )
			profile.set_preference("network.proxy.http_port", int(port))

		if not location_access:
			profile.set_preference("geo.enabled", False)
			profile.set_preference("geo.provider.use_corelocation", False)
			profile.set_preference("geo.prompt.testing", False)
			profile.set_preference("geo.prompt.testing.allow", False)

		if incognito:
			profile.set_preference("browser.privatebrowsing.autostart", True)

		if lite:
			profile.set_preference('permissions.default.image', 2)
			profile.set_preference('permissions.default.stylesheet', 2)

		if headless:
			options.set_headless(True) 

		profile.update_preferences()
		browser=self.webdriver.Firefox(executable_path=str(Path.joinpath(Path.cwd(),'common',getos(),'geckodriver')),firefox_profile=profile,options=options)
		#Proxy only works with windows!
		if login or password:
			browser.get("https://www.google.com")
			browser.get("http://amibehindaproxy.com/")
			os.system(str(Path.joinpath(Path.cwd(),'common','firefox_proxy.exe'))+login+" "+password)

		return browser


	###############################################################
	#
	#	FUNCTIONS FOR HANDLING DYNAMICALLY LOADED ELEMENTS
	#
	###############################################################

	def find_element_by_id(self,element,parent):
		try:
			el=parent.find_element_by_id(element)
			return el
		except:
			time.sleep(3)
			print("Searching for element "+element)
			self.find_element_by_id(element,parent)

	def find_elements_by_class_name(self,element,parent):
		try:
			el=parent.find_elements_by_class_name(element)
			if(len(el)>0):
				return el
			else:	
				time.sleep(3)
				print("Searching for element "+element)
				self.find_elements_by_class_name(element,parent)
		except:
			time.sleep(3)
			print("Searching for element "+element)
			self.find_elements_by_class_name(element,parent)

	def find_element_by_name(self,element,parent):
		try:
			el=parent.find_element_by_name(element)
			return el
		except:
			time.sleep(3)
			print("Searching for element "+element)
			self.find_element_by_name(element,parent)

	def find_elements_by_tag_name(self,element,parent):
		try:
			el=parent.find_elements_by_tag_name(element)
			if(len(el)>0):
				return el
			else:
				time.sleep(3)
				print("Searching for element "+element)
				self.find_elements_by_tag_name(element,parent)
		except:
			time.sleep(3)
			print("Searching for element "+element)
			self.find_elements_by_tag_name(element,parent)


	###############################################################
	#
	#	SOME HELPFUL FUNCTIONS
	#
	###############################################################

	def select(self,driver, element, labels):
		select = self.Select(element)
		for label in labels:
			select.select_by_visible_text(label)

	def move_to(self,element,driver):
		driver.execute_script("arguments[0].scrollIntoView();", element)
		return element

	def find_parent(self,element):
		parent=element.find_element_by_xpath('..')
		return parent

###############################################################
#
#	ACCOUNT GENERATOR FUNCTIONS
#
###############################################################

class AccountHandler():
	def __init__(self):
		install_package('faker')
		self.faker=importlib.import_module('faker')

	def generate_password(self):
		alphabet = string.ascii_letters + string.digits
		password=""
		while True:
			password = ''.join(random.choice(alphabet) for i in range(10))
			if (any(c.islower() for c in password)	and any(c.isupper() for c in password)	and sum(c.isdigit() for c in password) >= 3):
				break
		return password

	def create_profile(self):
		profile={}
		fake=self.faker.Faker()
		profile['first_name']=fake.first_name()
		profile['gender']=fake.first_name()
		profile['last_name']=fake.last_name()
		profile['email']=fake.free_email()
		profile['email']=profile['email'].split('@')
		profile['email']=profile['email'][0]+''.join(["%s" % random.randint(0, 9) for num in range(0, 6)])+'@'+profile['email'][1]
		profile['password']=self.generate_password()
		dob=fake.date_of_birth(minimum_age=18,maximum_age=60)
		if len(str(dob.day))==1:
			profile['dob_day']='0'+str(dob.day)
		else:
			profile['dob_day']=str(dob.day)
		if len(str(dob.month))==1:
			profile['dob_month']='0'+str(dob.month)
		else:
			profile['dob_month']=str(dob.month)
		profile['dob_year']=str(dob.year)

		return profile

###############################################################
#
#	DATABASE MANIPULATION FUNCTIONS
#
###############################################################

class DatabaseHandler():
	def __init__(self):
		install_package('mysql-connector-python')
		self.mysql_connector=importlib.import_module('mysql.connector')

	def mysql_login(self,host,username,password,database):
		mydb = self.mysql_connector.connect(
		host=host,
		user=username,
		passwd=password,
		database=database
		)
		return mydb

	def insert_into_table(self,database,table,dictionary):
		mycursor = database.cursor()
		allvals=['%s' for x in list(dictionary.keys())]
		columns="("
		columns+=",".join(list(dictionary.keys()))
		columns+=")"
		v="("
		v+=",".join(allvals)
		v+=")"
		sql=""
		sql = "INSERT INTO "+table+" "+columns+"values "+v
		mycursor.execute(sql,tuple(list(dictionary.values())))
		
		database.commit()


###############################################################
#
#	SPREADSHEET MANIPULATION FUNCTIONS
#
###############################################################

class SpreadsheetHandler():
	def __init__(self):
		#install_package('xlrd')
		self.xlrd=importlib.import_module('xlrd')
		#install_package('xlsxwriter')
		self.xlsxwriter=importlib.import_module('xlsxwriter')
		#install_package('openpyxl')
		self.openpyxl=importlib.import_module('openpyxl')

	def excel_read(self,file,sheet_name='Sheet1'):	
		book = self.xlrd.open_workbook(file)
		sheet = book.sheet_by_name(sheet_name)
		data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
		return data

	def excel_write(self,dataset,file):
		workbook = self.xlsxwriter.Workbook(file)
		worksheet = workbook.add_worksheet()
		n=1
		for data in dataset:
			c='A'
			for x in data:
				cell=c+str(n)
				worksheet.write(cell, x)
				c=chr(ord(c)+1)
			n+=1
		workbook.close()

	def excel_append(self,dataset,file,sheet_name='Sheet1'):
		wb = self.openpyxl.load_workbook(filename=file)
		ws = wb.get_sheet_by_name(sheet_name)
		for new_row in dataset:
			row = ws.max_row+ 1
			for col, entry in enumerate(new_row, start=1):
				ws.cell(row=row, column=col, value=entry)
		wb.save(file)

###############################################################
#
#	TEXT FILE MANIPULATION FUNCTIONS
#
###############################################################
	
class FileHandler():
	def text_read(self,file):
		with open(file) as f:
			content = f.readlines()
		return content	

	def text_write(self,data,file):
		with open(file, 'w') as f:
			for item in data:
				f.write("%s\n" % item)


###############################################################
#
#	EMAIL FUNCTIONS
#
###############################################################

class EmailHandler():
	def __init__(self):
		install_package('smtplib')
		self.MIMEMultipart=importlib.import_module('email.mime.multipart').MIMEMultipart
		self.MIMEText=importlib.import_module('email.mime.text').MIMEText
		self.imaplib=importlib.import_module('imaplib')
		self.smtplib=importlib.import_module('smtplib')

	def send_email(self,to_id,subject,body,from_id='mobits.bot@gmail.com',from_pass='mobits123'):
		server = self.smtplib.SMTP(host='smtp.gmail.com', port=587)
		server.starttls()
		server.login(from_id, from_pass)

		msg = self.MIMEMultipart()
		msg['From'] = from_id
		msg['To'] = to_id
		msg['Subject'] = subject
		
		msg.attach(self.MIMEText(body, 'plain'))

		server.sendmail(from_id, to_id, msg.as_string())
		server.quit()

	def read_email(self,from_email,from_pwd,smtp_server,search_filter,smtp_port=993):
		
		mail = self.imaplib.IMAP4_SSL(smtp_server)
		mail.login(from_email,from_pwd)
		mail.select('inbox')
		result, data = mail.search(None, search_filter)
		mail_ids = data[0]
		id_list = mail_ids.split()
		first_email_id =id_list[0]
		latest_email_id = id_list[-1] #most recent email
		result,data = mail.fetch(latest_email_id, "(RFC822)")
		raw_email = data[0][1].decode('utf-8')

		#read the email 
		email_message = email.message_from_string(raw_email)

		return str(email_message)

#################################################################
#
#	CAPTCHA SOLVING FUNCTIONS
#
#################################################################

class CaptchaHandler():
	def __init__(self):
		install_package('requests')
		import requests

	def solve_recaptcha(self,API_KEY,element,browser):
		site_key=browser.execute_script("return arguments[0].src",element).split('&k=')[1]
		site_key=site_key.split('&co')[0]

		url=browser.current_url

		captcha_id = requests.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(API_KEY, site_key, url)).text
		try:
			captcha_id=captcha_id.split('|')[1]
		except:
			return False

		recaptcha_answer = requests.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
		print("solving captcha...")
		while 'CAPCHA_NOT_READY' in recaptcha_answer:
			print('Waiting for solution')
			time.sleep(10)
			recaptcha_answer = requests.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
		try:
			recaptcha_answer = recaptcha_answer.split('|')[1]
		except:
			recaptcha_answer=recaptcha_answer
		payload = {'key': 'value','gresponse': recaptcha_answer}
		response = requests.post(url, payload)
		return recaptcha_answer