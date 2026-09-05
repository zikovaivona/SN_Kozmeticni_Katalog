import sqlite3
import os
import getpass
from werkzeug.security import check_password_hash


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sephora.db")


# Vzpostavi povezavo s SQLite podatkovno bazo.
def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


# Omogoča iskanje in prikaz izdelkov glede na ime, znamko ali kategorijo.
def search_products(db):
    term = input("Search product, brand or category (empty = all): ").strip()
    rows = db.execute("""
        SELECT id, product_name, brand_name, rating, price_usd, sale_price_usd
        FROM products
        WHERE product_name LIKE ? OR brand_name LIKE ?
           OR primary_category LIKE ? OR secondary_category LIKE ?
        ORDER BY product_name
        LIMIT 20
    """, tuple([f"%{term}%"] * 4)).fetchall()

    if not rows:
        print("No products found.")
        return

    for row in rows:
        price = row["sale_price_usd"] if row["sale_price_usd"] is not None else row["price_usd"]
        print(f'{row["id"]}: {row["product_name"]} | {row["brand_name"] or "Unknown"} | '
              f'Rating: {row["rating"] or "N/A"} | ${price or 0:.2f}')


# Prikaže podrobne informacije o izbranem izdelku.
def show_product(db):
    try:
        pid = int(input("Product database ID: "))
    except ValueError:
        print("Invalid ID.")
        return

    row = db.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    if not row:
        print("Product not found.")
        return

    print("\n--- PRODUCT ---")
    print("Name:", row["product_name"])
    print("Brand:", row["brand_name"] or "Unknown")
    print("Product ID:", row["product_id"] or "—")
    print("Price:", f'${row["price_usd"]:.2f}' if row["price_usd"] is not None else "N/A")

    if row["sale_price_usd"] is not None:
        print("Sale price:", f'${row["sale_price_usd"]:.2f}')

    if row["value_price_usd"] is not None:
        print("Value/reference price:", f'${row["value_price_usd"]:.2f}')

    print("Source rating:", row["rating"] if row["rating"] is not None else "N/A")
    print("Source reviews:", row["reviews"] if row["reviews"] is not None else 0)

    print("Category:", " / ".join(filter(None, [
        row["primary_category"],
        row["secondary_category"],
        row["tertiary_category"]
    ])))


# Izračuna in prikaže osnovne statistične podatke o izdelkih.
def analytics(db):
    stats = db.execute("""
        SELECT COUNT(*) AS products,
               COUNT(DISTINCT brand_name) AS brands,
               ROUND(AVG(price_usd), 2) AS avg_price,
               ROUND(AVG(rating), 2) AS avg_rating
        FROM products
    """).fetchone()

    print("\n--- ANALYTICS ---")
    print("Products:", stats["products"])
    print("Brands:", stats["brands"])
    print("Average price:", f'${stats["avg_price"] or 0:.2f}')
    print("Average rating:", stats["avg_rating"] or 0)


# Omogoča prijavo uporabnika in preverjanje njegovega gesla.
def login(db):
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")

    user = db.execute(
        "SELECT id, username, role, password_hash FROM users WHERE username=?",
        (username,)
    ).fetchone()

    if user and check_password_hash(user["password_hash"], password):
        print(f'Logged in as {user["username"]} ({user["role"]}).')
        return user

    print("Incorrect username or password.")
    return None


# Prikaže seznam izdelkov, ki jih je uporabnik dodal med priljubljene.
def favorites(db, user):
    if not user:
        print("Please log in first.")
        return

    rows = db.execute("""
        SELECT p.id, p.product_name, p.brand_name
        FROM favorites f JOIN products p ON p.id=f.product_id
        WHERE f.user_id=?
        ORDER BY p.product_name
    """, (user["id"],)).fetchall()

    print("\n--- FAVORITES ---")

    if not rows:
        print("No favorites.")

    for row in rows:
        print(f'{row["id"]}: {row["product_name"]} | {row["brand_name"] or "Unknown"}')


# Doda izdelek med priljubljene ali ga iz priljubljenih odstrani.
def toggle_favorite(db, user):
    if not user:
        print("Please log in first.")
        return

    try:
        pid = int(input("Product database ID: "))
    except ValueError:
        print("Invalid ID.")
        return

    if not db.execute("SELECT id FROM products WHERE id=?", (pid,)).fetchone():
        print("Product not found.")
        return

    exists = db.execute(
        "SELECT 1 FROM favorites WHERE user_id=? AND product_id=?",
        (user["id"], pid)
    ).fetchone()

    if exists:
        db.execute(
            "DELETE FROM favorites WHERE user_id=? AND product_id=?",
            (user["id"], pid)
        )
        print("Removed from favorites.")
    else:
        db.execute(
            "INSERT INTO favorites(user_id, product_id) VALUES (?, ?)",
            (user["id"], pid)
        )
        print("Added to favorites.")

    db.commit()


# Glavna funkcija programa, ki prikazuje meni in obdeluje izbiro uporabnika.
def main():
    if not os.path.exists(DB_PATH):
        raise SystemExit("Database not found. Run seed_database.py first.")

    db = connect()
    user = None

    while True:
        print("""
=== BEAUTÉ TEXT INTERFACE ===
1. Search/list products
2. Product details
3. Analytics
4. Login
5. Show favorites
6. Add/remove favorite
0. Exit
""")

        choice = input("Choose: ").strip()

        if choice == "1":
            search_products(db)
        elif choice == "2":
            show_product(db)
        elif choice == "3":
            analytics(db)
        elif choice == "4":
            user = login(db)
        elif choice == "5":
            favorites(db, user)
        elif choice == "6":
            toggle_favorite(db, user)
        elif choice == "0":
            break
        else:
            print("Unknown option.")

    db.close()


# Zažene glavno funkcijo samo, če datoteko zaženemo neposredno.
if __name__ == "__main__":
    main()