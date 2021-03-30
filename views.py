from django.http import HttpResponse
from django.shortcuts import render
import json 
import requests

# The index function, which linked to the request in the index.html
def index(request):
    # guest_entry sting
	guest_entry = request.GET.get("guest_entry", "")
	if guest_entry:
		data = {"data":ncbi_pmid_srch(guest_entry), 'query':guest_entry}
		return render(request, "result.html", context=data);

	return render(request, "index.html")

def ncbi_pmid_srch(guest_entry):

      # Entrez API base URL
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    # database
    db = "pubmed"

    # query url 
    query_url = base_url + "esearch.fcgi?db=" + db + "&term=" + guest_entry + "&retmode=json"

    # response in the json format
    response = requests.get(query_url).json()

    # idList to str
    idList = response["esearchresult"]["idlist"]

    result = []

    # if no articles print the next text to the log file
    if len(idList) == 0: 
        print("Skipped, there is no such article for that query.")
    
    # if articles found
    else: 
        # iter first few articles in the list
        for article in idList[0:2]: 
            
            # count total
            total = len(idList[0:2])
            
            # searching the index
            i = idList.index(article)
            
            # massage to the log file
            if i == 0: 
                print("starting search")
               
            article_count = int(i) + 1
                
            # count number of each article    
            print(f"Retrieving articles {article_count} of {total}")
            
            
            # base url to retrieve article summary   
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
            
            # generate endpoint url from our search to retrieve information for each article 
            search_url = url + "db=" + db + "&id=" + article +"&retmode=json"

            # request article information, formatted as json 
            recieved_article_info = requests.get(search_url).json()
            
            # create empty list for storing multiple authors per article
            author_list = []

            
        
            # try and except loop to keep the loop running 
            try: 

                # data parsing from our search response 
                title = recieved_article_info["result"][article]["title"]
                authors = recieved_article_info["result"][article]["authors"]
                journal = recieved_article_info["result"][article]["source"]
                pub_date = recieved_article_info["result"][article]["pubdate"]
                volume = recieved_article_info["result"][article]["volume"]
                issue = recieved_article_info["result"][article]["issue"]
                pages = recieved_article_info["result"][article]["pages"]
                doi = recieved_article_info["result"][article]["elocationid"]

                # append values to list 
                for i in authors: 
                    all_authors = i["name"]
                    author_list.append(all_authors)

                               # replace [,], and ' symbols from each element in author list 
                names = str(author_list).replace("'", "").replace("[", "").replace("]", "")

                # replace title italization <i></i>
                correct_title = title.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>").replace("&lt;sub&gt;", "<sub>").replace("&lt;/sub&gt;","</sub>")
                year =  str(pub_date[0:4])
                
                correct_pubdate = " ("+year+"). "
                
                result.append(f"{names}.{correct_pubdate} {correct_title} {journal};{volume}({issue}):{pages}. {doi}")
                
             
            # exception log
            except: 
                print("Skipping, no iformation")

    return result