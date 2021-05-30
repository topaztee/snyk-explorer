import json
import openai
from bs4 import BeautifulSoup as bs
import requests
import config

# Reading the API key from a file
service_key = config.api_key
openai.api_key = service_key

# PACKAGE NAME
pkg_name = input("Enter package name: ")

# Get the URL
URL = 'https://snyk.io/advisor/npm-package/' + pkg_name
URL_dep = URL + '#dependencies'
r =requests.get(URL)
r_dep =requests.get(URL_dep)

if r.status_code == 200:

	soup = bs(r.text, "html.parser")
	soup_dep = bs(r_dep.text, "html.parser")

	# Parse the HTML for the data
	data_set = []
	dependencies = ['List of package dependencies']
	for tag in soup.find_all('div', class_='number'):
		data_set.append(tag.text)
	for tag in soup.find_all('ul', class_='scores'):
		for ele in tag.find_all('li'):
		    data_set.append(ele.text)
	for tag in soup.find_all('dl', class_='stats'):
		for ele in tag.find_all('div'):
		    text = ele.text.replace('\n', '')
		    text = " ".join(text.split())
		    data_set.append(text)
	# Dependencies
	for tag in soup_dep.find_all('div', {'id': 'dependencies'}):
		for ele in tag.find_all('a'):
	#         print(ele.text)
		    dependencies.append(ele.text)
		    
	# Create list of JSON objects
	list_of_jsons = []
	for line in data_set:
		json_obj = {"text": line}
		list_of_jsons.append(json_obj)
	dep = ", ".join(dependencies)
	dep_obj = [{'text' : dep, "metadata": "list of package dependencies"}]

	# Create file with data
	with open('data.jsonl', 'w') as json_file:
		for ele in list_of_jsons:
		    json.dump(ele, json_file)
		    json_file.write('\n')
		for ele in dep_obj:
		    json.dump(ele, json_file)
		    json_file.write('\n')
		    
	# Send file to openAI
	file = openai.File.create(file=open("data.jsonl"), purpose='answers')
	file_id = file['id']

	print("--------------------")
	print("Type 'exit' to quit.")
	print("--------------------")
	# QUESTION:
	q = input("Question: ")
	while q != 'exit':

		# Get an answer
		answer = openai.Answer.create(
			search_model="ada", 
			model="curie", 
			question=q, 
			file=file_id, 
			examples_context="In 2017, U.S. life expectancy was 78.6 years.", 
			examples=[["What is human life expectancy in the United States?", "78 years."]], 
			max_rerank=10,
			max_tokens=5,
			stop=["\n", "<|endoftext|>"]
		)

		ans = "".join(answer['answers'])
		print(f"A: {ans}")
		q = input("Question: ")
else:
	print("Package not found.")
