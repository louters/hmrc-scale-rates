# HMRC Scale Rates
A website that allows one to look up HMRC scale rates by location (country, city), and compute the maximum allowable scale rate payment for a specific trip (given a location, trip's arrival & departure date and time).

The [official HMRC webpage](https://www.gov.uk/guidance/expenses-rates-for-employees-travelling-outside-the-uk) where you can find the rates, examples, and more information.

**N.B.:** There is no live website for the current application.

## Try it!
In order to try it locally, first download the repository to your machine. Then, depending on your OS perform the following.

### On Linux/macOS
In your terminal:

    $ export FLASK_APP=app.py
    $ flask run
    * Running on http://127.0.0.1:5000/
### On Windows
On Command Prompt:

    C:\path\to\app>set FLASK_APP=app.py
    $ python -m flask run
      * Running on http://127.0.0.1:5000/
  
  
## Technical information
A MVC framework is used. 

The back-end uses Python 3.6 and the Flask framework.
The front-end uses JavaScript, HTML5, CSS, and [Bootstrap](https://getbootstrap.com/). 

The [official HMRC webpage](https://www.gov.uk/guidance/expenses-rates-for-employees-travelling-outside-the-uk) is parsed with bs4 (BeautifulSoup) and re (Regular Expression). 

The data is then structured in a multi-nested dictionary that contains all the relevant information. It is made persistent by dumping in a JSON file. The latter is only updated (on request of the use of the service) at most once every 24 hours. 

## Ideas for improvements
- Fix parsing when rate is stated in a currency different from the country's main currency 
- Add register/login features
- Add history functionality (ie consult past trips and rates)
- Add exchange rate with GBP in order to convert scale rates to GBP

## Images
Images used come from [unsplash.com](https://unsplash.com/).
Icon used comes from [favicon.io](https://favicon.io/emoji-favicons/).
