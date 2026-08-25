SEPHORA MAKEUP DATABASE APP

Python + Flask + SQLite. No Java and no product images.

1. Install Python 3.
2. Open terminal in this folder.
3. Install dependencies:
   pip install -r requirements.txt
4. Build the SQLite database from the included Sephora CSV:
   python seed_database.py
5. Start the app:
   python app.py
6. Open http://127.0.0.1:5000

The included database contains the cleaned/imported products from product_info.csv.
The app supports login/register, cookies, favorites, reviews, search, filters, analytics,
add/edit/delete products and dark mode.

The app intentionally does not display or load product images.
