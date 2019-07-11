import helper
import json
import requests,bs4
from datetime import datetime
from helper import SpreadsheetHandler
import argparse
import time

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-i','--filename',type=str,help='FILE NAME goes here')
	args = parser.parse_args()
	filename = args.filename
	obj = helper.SpreadsheetHandler()
	data = obj.excel_read(filename)
	print("Running bot...")
	url = 'https://www.instagram.com/'
	userids = [ data[i][0] for i in range(1,len(data)) ]
	likes = []
	comments = []
	for i in range(len(userids)):
		page = requests.get(url + userids[i] + '/')
		soup = bs4.BeautifulSoup(page.text,"html5lib")
		webData = json.loads(soup.find('body').find('script').text.strip().replace('window._sharedData =','').replace(';',''))
		nodes = webData['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
		for j in range(3,len(nodes)):
			likes.append(nodes[j]['node']['edge_liked_by']['count'])
			comments.append(nodes[j]['node']['edge_media_to_comment']['count'])

		avgLikes = round(sum(likes)/len(likes),2)
		avgComments = round(sum(comments)/len(comments),2)
		noOfPosts = webData['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count']
		accType = 'Business' if webData['entry_data']['ProfilePage'][0]['graphql']['user']['is_business_account'] else 'Personal'
		noOfFollowers = webData['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']

		try:
			f=open('.past_data','r')
			pastData=f.read().split()
			pastData[0]=pastData[0].split(',')
			pastData[1]=pastData[1].split(',')
			if userids[i] in pastData[0]:
				index = pastData[0].index(userids[i])
				now=time.time()
				if pastData[1][index]=='0':
					pastData[1][index]=str(now)
					data[i+1][7] = noOfPosts
				else:
					today=datetime.fromtimestamp(now)
					then = datetime.fromtimestamp(float(pastData[1][index]))
					diff = today-then
					if diff.days>0:
						data[i+1][7] = round(noOfPosts/diff.days,2)
				f.close()
			else:
				pastData[0].append(userids[i])
				pastData[1].append(str(now))
			f=open('.past_data','w')
			pastData[0]=','.join(pastData[0])
			pastData[1]=','.join(pastData[1])
			pastData = '\n'.join(pastData)
			f.write(pastData)
			f=open('.copy','w')
			f.write(pastData)
			f.close()
		except:
			print("Error Occured! Try again!")
			copy = open('.copy','r')
			f = open('.past_data','w')
			pastData = copy.read()
			f.write(pastData)
			
		data[i+1][2] = noOfFollowers
		data[i+1][3] = avgLikes
		data[i+1][4] = avgComments
		data[i+1][8] = accType

	obj.excel_write(data,'input.xlsx')
	print("Data scraped and stored in file")
	
if __name__=='__main__':
	main()




