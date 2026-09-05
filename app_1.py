# Uvozimo funkcije, ki jih potrebujemo za delovanje spletne aplikacije.
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
# Funkciji za varno shranjevanje in preverjanje uporabniških gesel.
from werkzeug.security import generate_password_hash, check_password_hash
# Funkcija za varen prikaz besedila v HTML-ju.
from html import escape
# Knjižnice za podatkovno bazo, delo s potmi in statistične izračune.
import sqlite3, os, math, statistics, uuid, ast

# Določimo osnovno mapo projekta.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Določimo lokacijo podatkovne baze.
DB_PATH = os.path.join(BASE_DIR, 'sephora.db')
# Ustvarimo Flask aplikacijo.
app = Flask(__name__)
# Skrivni ključ omogoča varno uporabo uporabniških sej.
app.secret_key = os.environ.get('SECRET_KEY', 'dev-only-change-this-secret-key')
app.config['DATABASE'] = DB_PATH


# Vzpostavimo povezavo s podatkovno bazo za trenutni zahtevek.
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
# Po koncu zahtevka zapremo odprto povezavo z bazo.
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# Ustvarimo potrebne tabele, če še ne obstajajo.
def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript('''
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user', 'admin')),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT UNIQUE,
        product_name TEXT NOT NULL,
        brand_name TEXT,
        loves_count INTEGER DEFAULT 0,
        rating REAL,
        reviews INTEGER,
        size TEXT,
        variation_type TEXT,
        variation_value TEXT,
        variation_desc TEXT,
        ingredients TEXT,
        price_usd REAL,
        value_price_usd REAL,
        sale_price_usd REAL,
        limited_edition INTEGER DEFAULT 0,
        new_product INTEGER DEFAULT 0,
        online_only INTEGER DEFAULT 0,
        out_of_stock INTEGER DEFAULT 0,
        sephora_exclusive INTEGER DEFAULT 0,
        highlights TEXT,
        primary_category TEXT,
        secondary_category TEXT,
        tertiary_category TEXT,
        child_count INTEGER DEFAULT 0,
        child_max_price REAL,
        child_min_price REAL
    );
    CREATE TABLE IF NOT EXISTS favorites (
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        PRIMARY KEY(user_id, product_id),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
        comment TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, product_id),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_products_name ON products(product_name);
    CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand_name);
    CREATE INDEX IF NOT EXISTS idx_products_category ON products(primary_category);
    CREATE INDEX IF NOT EXISTS idx_products_price ON products(price_usd);
    ''')
    # Združljivost z obstoječimi bazami: dodamo vlogo, če je še ni.
    columns = [row[1] for row in db.execute('PRAGMA table_info(users)').fetchall()]
    if 'role' not in columns:
        db.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
        db.commit()
    db.commit()
    db.close()


# Preverimo, ali je podatkovna baza pripravljena in vsebuje izdelke.
def ensure_db():
    init_db()
    db = sqlite3.connect(DB_PATH)
    count = db.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    db.close()
    if count == 0:
        raise RuntimeError('Database is empty. Run seed_database.py first.')


# Poiščemo trenutno prijavljenega uporabnika.
def current_user():
    uid = session.get('user_id')
    if not uid: return None
    return get_db().execute('SELECT id, username, role FROM users WHERE id=?', (uid,)).fetchone()

@app.context_processor
def inject_globals():
    return {'current_user': current_user()}


# Vrednosti iz obrazca pretvorimo v 0 ali 1.
def parse_bool(v):
    return 1 if str(v).lower() in ('1','true','yes','on') else 0

def format_list(value):
    """Turn dataset strings such as "['A', 'B']" into readable text."""
    if not value:
        return ''
    value = str(value).strip()
    try:
        parsed = ast.literal_eval(value)
        if isinstance(parsed, (list, tuple)):
            return ', '.join(str(item).strip() for item in parsed if str(item).strip())
    except (ValueError, SyntaxError):
        pass
    return value


app.jinja_env.filters['readable_list'] = format_list

@app.route('/')
# Začetna stran prikaže osnovno statistiko in izbrane izdelke.
def home():
    db = get_db()
    stats = {
        'products': db.execute('SELECT COUNT(*) FROM products').fetchone()[0],
        'brands': db.execute('SELECT COUNT(DISTINCT brand_name) FROM products WHERE brand_name IS NOT NULL AND brand_name <> ""').fetchone()[0],
        'categories': db.execute('SELECT COUNT(DISTINCT primary_category) FROM products WHERE primary_category IS NOT NULL AND primary_category <> ""').fetchone()[0],
        'rating': db.execute('SELECT ROUND(AVG(rating),2) FROM products WHERE rating IS NOT NULL').fetchone()[0] or 0
    }
    featured = db.execute('SELECT * FROM products WHERE rating IS NOT NULL ORDER BY rating DESC, loves_count DESC LIMIT 8').fetchall()
    return render_template('home.html', stats=stats, featured=featured)

@app.route('/products')
# Omogočimo iskanje, filtriranje, razvrščanje in strani izdelkov.
def products():
    db = get_db()
    q = request.args.get('q','').strip()
    brand = request.args.get('brand','').strip()
    category = request.args.get('category','').strip()
    min_price = request.args.get('min_price','').strip()
    max_price = request.args.get('max_price','').strip()
    min_rating = request.args.get('min_rating','').strip()
    sort = request.args.get('sort','name')
    page = max(int(request.args.get('page',1)),1)
    per_page = 24
    where=[]; params=[]
    if q:
        where.append('(product_name LIKE ? OR brand_name LIKE ? OR primary_category LIKE ? OR secondary_category LIKE ?)')
        x=f'%{q}%'; params += [x,x,x,x]
    if brand: where.append('brand_name=?'); params.append(brand)
    if category: where.append('primary_category=?'); params.append(category)
    if min_price:
        try: where.append('COALESCE(sale_price_usd, price_usd)>=?'); params.append(float(min_price))
        except ValueError: pass
    if max_price:
        try: where.append('COALESCE(sale_price_usd, price_usd)<=?'); params.append(float(max_price))
        except ValueError: pass
    if min_rating:
        try: where.append('rating>=?'); params.append(float(min_rating))
        except ValueError: pass
    where_sql = (' WHERE ' + ' AND '.join(where)) if where else ''
    order_map = {'name':'product_name ASC','price_low':'COALESCE(sale_price_usd,price_usd) ASC','price_high':'COALESCE(sale_price_usd,price_usd) DESC','rating':'rating DESC','popular':'loves_count DESC','new':'new_product DESC, product_name ASC'}
    order_sql = order_map.get(sort, order_map['name'])
    total = db.execute('SELECT COUNT(*) FROM products'+where_sql, params).fetchone()[0]
    pages = max(math.ceil(total/per_page),1)
    page=min(page,pages)
    offset=(page-1)*per_page
    rows=db.execute(f'SELECT * FROM products{where_sql} ORDER BY {order_sql} LIMIT ? OFFSET ?', params+[per_page,offset]).fetchall()
    brands=db.execute('SELECT DISTINCT brand_name FROM products WHERE brand_name IS NOT NULL AND brand_name<>"" ORDER BY brand_name').fetchall()
    cats=db.execute('SELECT DISTINCT primary_category FROM products WHERE primary_category IS NOT NULL AND primary_category<>"" ORDER BY primary_category').fetchall()
    return render_template('products.html', products=rows, brands=brands, categories=cats, total=total, page=page, pages=pages, q=q, brand=brand, category=category, min_price=min_price, max_price=max_price, min_rating=min_rating, sort=sort)

@app.route('/product/<int:pid>')
# Prikažemo podrobnosti izdelka, priljubljenost in ocene.
def product(pid):
    db=get_db(); p=db.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone()
    if not p: return 'Product not found',404
    fav=False
    if session.get('user_id'):
        fav=bool(db.execute('SELECT 1 FROM favorites WHERE user_id=? AND product_id=?',(session['user_id'],pid)).fetchone())
    reviews=db.execute('''SELECT r.*,u.username FROM reviews r JOIN users u ON u.id=r.user_id WHERE r.product_id=? ORDER BY r.created_at DESC''',(pid,)).fetchall()
    return render_template('product.html', p=p, favorite=fav, reviews=reviews)

@app.route('/register', methods=['GET','POST'])
# Registriramo novega uporabnika in njegovo geslo shranimo kot hash.
def register():
    if request.method=='POST':
        username=request.form.get('username','').strip(); password=request.form.get('password','')
        if len(username)<3 or len(password)<6: flash('Username needs 3+ characters and password 6+ characters.','error')
        else:
            try:
                db=get_db(); db.execute('INSERT INTO users(username,password_hash,role) VALUES (?,?,?)',(username,generate_password_hash(password),'user')); db.commit()
                flash('Account created. You can log in now.','success'); return redirect(url_for('login'))
            except sqlite3.IntegrityError: flash('Username already exists.','error')
    return render_template('auth.html', mode='register')

@app.route('/login', methods=['GET','POST'])
# Preverimo uporabniško ime in geslo ter ustvarimo sejo.
def login():
    if request.method=='POST':
        username=request.form.get('username','').strip(); password=request.form.get('password','')
        user=get_db().execute('SELECT * FROM users WHERE username=?',(username,)).fetchone()
        if user and check_password_hash(user['password_hash'],password): session['user_id']=user['id']; flash('Welcome back!','success'); return redirect(url_for('home'))
        flash('Incorrect username or password.','error')
    return render_template('auth.html', mode='login')

@app.route('/logout')
def logout(): session.clear(); flash('You have been logged out.','success'); return redirect(url_for('home'))

# Preverimo, ali je uporabnik prijavljen.
def login_required():
    if not session.get('user_id'):
        flash('Please log in first.','error'); return False
    return True


def admin_required():
    user = current_user()
    if not user:
        flash('Please log in first.','error')
        return False
    if user['role'] != 'admin':
        flash('Only administrators can manage products.','error')
        return False
    return True


@app.route('/favorite/<int:pid>', methods=['POST'])
# Izdelek dodamo med priljubljene ali ga od tam odstranimo.
def favorite(pid):
    if not login_required(): return redirect(url_for('login'))
    db=get_db(); exists=db.execute('SELECT 1 FROM favorites WHERE user_id=? AND product_id=?',(session['user_id'],pid)).fetchone()
    if exists: db.execute('DELETE FROM favorites WHERE user_id=? AND product_id=?',(session['user_id'],pid)); flash('Removed from favorites.','success')
    else: db.execute('INSERT INTO favorites(user_id,product_id) VALUES (?,?)',(session['user_id'],pid)); flash('Added to favorites.','success')
    db.commit(); return redirect(request.referrer or url_for('products'))

@app.route('/favorites')
# Prikažemo vse izdelke, ki jih je uporabnik shranil.
def favorites():
    if not login_required(): return redirect(url_for('login'))
    rows=get_db().execute('''SELECT p.* FROM products p JOIN favorites f ON f.product_id=p.id WHERE f.user_id=? ORDER BY p.product_name''',(session['user_id'],)).fetchall()
    return render_template('favorites.html', products=rows)

@app.route('/review/<int:pid>', methods=['POST'])
# Shranimo novo oceno ali posodobimo obstoječo oceno.
def add_review(pid):
    if not login_required(): return redirect(url_for('login'))
    try: rating=int(request.form.get('rating','5')); rating=max(1,min(5,rating))
    except ValueError: rating=5
    comment=request.form.get('comment','').strip()[:1000]
    db=get_db(); db.execute('''INSERT INTO reviews(user_id,product_id,rating,comment) VALUES(?,?,?,?) ON CONFLICT(user_id,product_id) DO UPDATE SET rating=excluded.rating, comment=excluded.comment, created_at=CURRENT_TIMESTAMP''',(session['user_id'],pid,rating,comment)); db.commit(); flash('Your review was saved.','success'); return redirect(url_for('product',pid=pid))

@app.route('/analytics')
# Izračunamo statistične podatke in pripravimo podatke za grafe.
def analytics():
    db=get_db()
    stats=db.execute('SELECT COUNT(*) products, COUNT(DISTINCT brand_name) brands, ROUND(AVG(price_usd),2) avg_price, ROUND(AVG(rating),2) avg_rating, SUM(loves_count) loves FROM products').fetchone()
    cats=db.execute('SELECT COALESCE(primary_category,"Other") category, COUNT(*) count FROM products GROUP BY primary_category ORDER BY count DESC LIMIT 12').fetchall()
    brands=db.execute('SELECT COALESCE(brand_name,"Unknown") brand, COUNT(*) count FROM products GROUP BY brand_name ORDER BY count DESC LIMIT 10').fetchall()
    price=db.execute('SELECT MIN(price_usd) min_price, MAX(price_usd) max_price FROM products WHERE price_usd IS NOT NULL').fetchone()

    ratings=db.execute("SELECT CAST(ROUND(rating,0) AS INTEGER) rating, COUNT(*) count FROM products WHERE rating IS NOT NULL AND rating BETWEEN 1 AND 5 GROUP BY CAST(ROUND(rating,0) AS INTEGER) ORDER BY rating").fetchall()
    price_ranges=db.execute("""SELECT CASE WHEN price_usd < 25 THEN '< $25' WHEN price_usd < 50 THEN '$25–49' WHEN price_usd < 100 THEN '$50–99' WHEN price_usd < 200 THEN '$100–199' ELSE '$200+' END price_range, COUNT(*) count FROM products WHERE price_usd IS NOT NULL AND price_usd >= 0 GROUP BY CASE WHEN price_usd < 25 THEN '< $25' WHEN price_usd < 50 THEN '$25–49' WHEN price_usd < 100 THEN '$50–99' WHEN price_usd < 200 THEN '$100–199' ELSE '$200+' END ORDER BY MIN(price_usd)""").fetchall()
    sale=db.execute("SELECT COUNT(*) total_sale, ROUND(AVG((price_usd-sale_price_usd)/price_usd*100),1) avg_discount FROM products WHERE price_usd>0 AND sale_price_usd IS NOT NULL AND sale_price_usd<price_usd").fetchone()
    price_values=[r[0] for r in db.execute('SELECT price_usd FROM products WHERE price_usd IS NOT NULL AND price_usd>=0').fetchall()]
    rating_values=[r[0] for r in db.execute('SELECT rating FROM products WHERE rating IS NOT NULL').fetchall()]
    corr_rows=db.execute('SELECT price_usd,rating FROM products WHERE price_usd IS NOT NULL AND rating IS NOT NULL').fetchall()
    if len(corr_rows)>=3:
        xs=[float(r['price_usd']) for r in corr_rows]; ys=[float(r['rating']) for r in corr_rows]
        mx,my=statistics.mean(xs),statistics.mean(ys)
        den=math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
        correlation=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/den if den else 0
    else:
        correlation=0
    median_price=statistics.median(price_values) if price_values else 0
    std_price=statistics.stdev(price_values) if len(price_values)>1 else 0
    median_rating=statistics.median(rating_values) if rating_values else 0

    def bar_chart(rows, label_key, title, value_suffix=''):
        rows=list(rows)
        if not rows: return ''
        width,height=900,360
        left,right,top,bottom=190,45,45,30
        max_value=max(float(r['count'] or 0) for r in rows) or 1
        gap=(height-top-bottom)/len(rows)
        bar_h=min(28,gap*0.62)
        out=[f'<div class="card" style="padding:18px"><h3 style="margin-top:0">{escape(title)}</h3><svg viewBox="0 0 {width} {height}" style="width:100%;height:auto">']
        for i,r in enumerate(rows):
            label=str(r[label_key] or 'Other')
            value=float(r['count'] or 0)
            y=top+i*gap
            w=(value/max_value)*(width-left-right)
            out.append(f'<text x="{left-10}" y="{y+bar_h*0.72:.1f}" text-anchor="end" fill="#666" font-size="13">{escape(label[:27])}</text>')
            out.append(f'<rect x="{left}" y="{y:.1f}" width="{w:.1f}" height="{bar_h:.1f}" rx="6" fill="#e88bb6"></rect>')
            out.append(f'<text x="{left+w+8:.1f}" y="{y+bar_h*0.72:.1f}" fill="#e88bb6" font-size="13" font-weight="700">{value:,.0f}{escape(value_suffix)}</text>')
        out.append('</svg></div>')
        return ''.join(out)

    def donut_chart(rows,title):
        rows=list(rows)[:9]
        total=sum(float(r['count'] or 0) for r in rows) or 1
        colors=['#e88bb6','#ef9fc4','#f3b0ce','#f6c1d8','#f8d0e2','#f9dce9','#fbe6f0','#e6a0c1','#d97aa7']
        start=0; stops=[]; legend=[]
        for i,r in enumerate(rows):
            value=float(r['count'] or 0)
            end=start+value/total*360
            stops.append(f'{colors[i]} {start:.1f}deg {end:.1f}deg')
            legend.append(f'<div style="display:grid;grid-template-columns:12px 1fr auto;gap:8px;align-items:center;font-size:13px"><span style="width:10px;height:10px;border-radius:50%;background:{colors[i]}"></span><span>{escape(str(r["category"]))}</span><b>{int(value):,}</b></div>')
            start=end
        return f'<div class="card" style="padding:18px"><h3 style="margin-top:0">{escape(title)}</h3><div style="display:flex;gap:28px;align-items:center;flex-wrap:wrap"><div style="width:210px;height:210px;border-radius:50%;background:conic-gradient({",".join(stops)});display:grid;place-items:center"><div style="width:112px;height:112px;border-radius:50%;background:white;display:flex;flex-direction:column;align-items:center;justify-content:center"><b style="font-size:23px">{int(total):,}</b><span style="font-size:12px;color:#777">products</span></div></div><div style="display:grid;gap:9px;min-width:210px">{"".join(legend)}</div></div></div>'

    charts=(f'<div style="margin-top:28px"><h2>Graphs & visual statistics</h2>'
            f'<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px">'
            f'{donut_chart(cats,"Products by category")}'
            f'{bar_chart(brands,"brand","Top 10 brands by number of products")}'
            f'</div>'
            f'<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:18px">'
            f'{bar_chart(ratings,"rating","Rating distribution"," ★")}'
            f'{bar_chart(price_ranges,"price_range","Products by price range")}'
            f'</div>'
            f'<div class="card" style="margin-top:18px;padding:18px"><h3 style="margin-top:0">Statistical summary</h3>'
            f'<div style="display:flex;gap:45px;flex-wrap:wrap">'
            f'<div><div style="font-size:26px;font-weight:800">${median_price:,.2f}</div><div style="color:#777">median price</div></div>'
            f'<div><div style="font-size:26px;font-weight:800">${std_price:,.2f}</div><div style="color:#777">price standard deviation</div></div>'
            f'<div><div style="font-size:26px;font-weight:800">{median_rating:.2f}</div><div style="color:#777">median rating</div></div>'
            f'<div><div style="font-size:26px;font-weight:800">{correlation:.3f}</div><div style="color:#777">Pearson price–rating correlation</div></div>'
            f'<div><div style="font-size:26px;font-weight:800">{int(sale["total_sale"] or 0):,}</div><div style="color:#777">products on sale</div></div>'
            f'<div><div style="font-size:26px;font-weight:800">{float(sale["avg_discount"] or 0):.1f}%</div><div style="color:#777">average discount</div></div>'
            f'</div><p style="color:#777;margin-bottom:0">Pearson correlation measures the strength of the linear relationship between price and rating; it does not imply causation.</p></div></div>')

    return render_template('analytics.html', stats=stats, cats=cats, brands=brands, price=price, charts=charts)

@app.route('/add', methods=['GET','POST'])
# Administrator adds a new product; source rating/review counts are not manually entered.
def add_product():
    if not admin_required():
        return redirect(url_for('login'))
    if request.method == 'POST':
        f = request.form
        try:
            price = float(f.get('price_usd') or 0)
            if price < 0:
                raise ValueError
        except ValueError:
            flash('Price must be a non-negative number.', 'error')
            return render_template('product_form.html', mode='Add')

        product_id = 'LOCAL-' + uuid.uuid4().hex[:10].upper()
        db = get_db()
        try:
            db.execute('''INSERT INTO products(
                product_id, product_name, brand_name, price_usd, size,
                primary_category, secondary_category, tertiary_category,
                ingredients, highlights, new_product, online_only,
                out_of_stock, sephora_exclusive, limited_edition
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                product_id,
                f.get('product_name','').strip(),
                f.get('brand_name','').strip(),
                price,
                f.get('size','').strip(),
                f.get('primary_category','').strip(),
                f.get('secondary_category','').strip(),
                f.get('tertiary_category','').strip(),
                f.get('ingredients','').strip(),
                f.get('highlights','').strip(),
                parse_bool(f.get('new_product')),
                parse_bool(f.get('online_only')),
                parse_bool(f.get('out_of_stock')),
                parse_bool(f.get('sephora_exclusive')),
                parse_bool(f.get('limited_edition'))
            ))
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            flash('Could not add the product.', 'error')
            return render_template('product_form.html', mode='Add')

        flash(f'Product added with ID {product_id}.', 'success')
        return redirect(url_for('products'))
    return render_template('product_form.html', mode='Add')


@app.route('/edit/<int:pid>', methods=['GET','POST'])
# Administrator edits product catalogue data; imported rating/review counts remain read-only.
def edit_product(pid):
    if not admin_required():
        return redirect(url_for('login'))
    db = get_db()
    p = db.execute('SELECT * FROM products WHERE id=?', (pid,)).fetchone()
    if not p:
        return 'Product not found', 404

    if request.method == 'POST':
        f = request.form
        try:
            price = float(f.get('price_usd') or 0)
            if price < 0:
                raise ValueError
        except ValueError:
            flash('Price must be a non-negative number.', 'error')
            return render_template('product_form.html', mode='Edit', p=p)

        db.execute('''UPDATE products SET
            product_name=?, brand_name=?, price_usd=?, size=?,
            primary_category=?, secondary_category=?, tertiary_category=?,
            ingredients=?, highlights=?, new_product=?, online_only=?,
            out_of_stock=?, sephora_exclusive=?, limited_edition=?
            WHERE id=?''', (
            f.get('product_name','').strip(),
            f.get('brand_name','').strip(),
            price,
            f.get('size','').strip(),
            f.get('primary_category','').strip(),
            f.get('secondary_category','').strip(),
            f.get('tertiary_category','').strip(),
            f.get('ingredients','').strip(),
            f.get('highlights','').strip(),
            parse_bool(f.get('new_product')),
            parse_bool(f.get('online_only')),
            parse_bool(f.get('out_of_stock')),
            parse_bool(f.get('sephora_exclusive')),
            parse_bool(f.get('limited_edition')),
            pid
        ))
        db.commit()
        flash('Product updated.', 'success')
        return redirect(url_for('product', pid=pid))

    return render_template('product_form.html', mode='Edit', p=p)


@app.route('/delete/<int:pid>', methods=['POST'])
# Izbrani izdelek odstranimo iz podatkovne baze.
def delete_product(pid):
    if not admin_required(): return redirect(url_for('login'))
    db=get_db(); db.execute('DELETE FROM products WHERE id=?',(pid,)); db.commit(); flash('Product deleted.','success'); return redirect(url_for('products'))


@app.route('/cookie-preferences', methods=['POST'])
# Shranimo uporabnikovo izbiro glede piškotkov.
def cookie_preferences():
    choice=request.form.get('choice','accept'); session['cookies_choice']=choice; return redirect(request.referrer or url_for('home'))

# Aplikacijo zaženemo, ko datoteko zaženemo neposredno.
if __name__=='__main__':
    ensure_db()
    app.run(debug=True)
