from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq #uReq opens up any url we want.

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page (index.html)
@cross_origin()
def homePage():
    return render_template("index.html") #always keep the html files inside templates folder. Don't mess spelling of folder.
#render template package for showcasing the html at the home page ('/')

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI. Execute the below when path is review

# Check index.html which runs at the home page. If we click submit, we are taken to the /review page.
# This is why next app.route is at review. At review path, we execute the below function.
# This is executed at the submit button named search in index.html , which takes in the form value named 'content'.(check index.html)


#Data is being sent through html page

@cross_origin()  #reqd when we deploy this over a cloud platform because we don't know from which location we will deploy it.
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","") #Content is what we enter in the search tab. Check index.html
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url) #we are able to ping this url using uReq
            flipkartPage = uClient.read()  #returns a huge text which is all the meta information for this page. right click and view page source to see
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser") #extract the html through beautifulsoup. bs is a library that can find html tags
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})

            #findAll is a method inside bs.
            #Here we give the class name inside the division tag. The above division tag selects the entire product.
            #Gives a 'list' of the above mentioned class.
            
           # Next step is to find the href to get url of each product. This is at box.div.div.div.a['href']


            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])


        #Check results.html, there is a loop for reviews where we are saving the reviews in a table format.
        
        #We have table headers Product, name, rating etc.,

        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001, debug=True)
	#app.run(debug=True)
