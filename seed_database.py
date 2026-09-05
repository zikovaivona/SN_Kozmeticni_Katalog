# Uvozimo knjižnice za branje podatkov in delo s podatkovno bazo.
import csv, sqlite3, os, ast
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.join(BASE_DIR, 'sephora.db')
CSV_PATH=os.path.join(BASE_DIR, 'product_info.csv')

def init_db():
# Povežemo se s podatkovno bazo.
    db=sqlite3.connect(DB_PATH)
    db.executescript('''
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user','admin')), created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT UNIQUE, product_name TEXT NOT NULL, brand_name TEXT, loves_count INTEGER DEFAULT 0, rating REAL, reviews INTEGER, size TEXT, variation_type TEXT, variation_value TEXT, variation_desc TEXT, ingredients TEXT, price_usd REAL, value_price_usd REAL, sale_price_usd REAL, limited_edition INTEGER DEFAULT 0, new_product INTEGER DEFAULT 0, online_only INTEGER DEFAULT 0, out_of_stock INTEGER DEFAULT 0, sephora_exclusive INTEGER DEFAULT 0, highlights TEXT, primary_category TEXT, secondary_category TEXT, tertiary_category TEXT, child_count INTEGER DEFAULT 0, child_max_price REAL, child_min_price REAL);
    CREATE TABLE IF NOT EXISTS favorites (user_id INTEGER NOT NULL, product_id INTEGER NOT NULL, PRIMARY KEY(user_id, product_id), FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, product_id INTEGER NOT NULL, rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5), comment TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id, product_id), FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE);
    CREATE INDEX IF NOT EXISTS idx_products_name ON products(product_name);
    CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand_name);
    CREATE INDEX IF NOT EXISTS idx_products_category ON products(primary_category);
    CREATE INDEX IF NOT EXISTS idx_products_price ON products(price_usd);
    ''')
    columns = [row[1] for row in db.execute('PRAGMA table_info(users)').fetchall()]
    if 'role' not in columns:
        db.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
    db.commit(); db.close()

def val(row,key):
    v=row.get(key,'')
    return None if v is None or str(v).strip()=='' else v

def num(v, cast=float):
    try: return cast(v) if v not in (None,'') else None
    except: return None

def text(v):
    return '' if v is None else str(v)

# Pripravimo bazo in povezavo za vnos izdelkov.
init_db(); db=sqlite3.connect(DB_PATH)
db.execute('DELETE FROM products')
with open(CSV_PATH, newline='', encoding='utf-8-sig') as f:
    reader=csv.DictReader(f)
    rows=[]
    for r in reader:
        rows.append((
            val(r,'product_id'), text(val(r,'product_name')), text(val(r,'brand_name')),
            num(val(r,'loves_count'),int) or 0, num(val(r,'rating')), num(val(r,'reviews'),int),
            text(val(r,'size')), text(val(r,'variation_type')), text(val(r,'variation_value')), text(val(r,'variation_desc')),
            text(val(r,'ingredients')), num(val(r,'price_usd')), num(val(r,'value_price_usd')), num(val(r,'sale_price_usd')),
            num(val(r,'limited_edition'),int) or 0, num(val(r,'new'),int) or 0, num(val(r,'online_only'),int) or 0,
            num(val(r,'out_of_stock'),int) or 0, num(val(r,'sephora_exclusive'),int) or 0,
            text(val(r,'highlights')), text(val(r,'primary_category')), text(val(r,'secondary_category')), text(val(r,'tertiary_category')),
            num(val(r,'child_count'),int) or 0, num(val(r,'child_max_price')), num(val(r,'child_min_price'))
        ))
db.executemany('''INSERT OR IGNORE INTO products(product_id,product_name,brand_name,loves_count,rating,reviews,size,variation_type,variation_value,variation_desc,ingredients,price_usd,value_price_usd,sale_price_usd,limited_edition,new_product,online_only,out_of_stock,sephora_exclusive,highlights,primary_category,secondary_category,tertiary_category,child_count,child_max_price,child_min_price) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',rows)
db.commit()
count=db.execute('SELECT COUNT(*) FROM products').fetchone()[0]
print(f'Imported {count} products into {DB_PATH}')
db.close()
