import peeweedbevolve
from flask import Flask, render_template, request, redirect, flash, url_for
from models import db, Store, Warehouse

app = Flask(__name__)
app.secret_key = b'!~\xae\xc4\xd1_\xc2\x08\xdeW\x02\xb2B\x10\xc42'

@app.before_request
def before_request():
   db.connect()

@app.after_request
def after_request(response):
   db.close()
   return response

@app.cli.command() # new
def migrate(): # new 
   db.evolve(ignore_tables={'base_model'}) # new

@app.route("/")
def index():
   return render_template('index.html')

@app.route("/store/new")
def new_store():
   return render_template('add-store.html')

@app.route("/store/submit", methods=['POST'])
def create_store():
   if request.method == "POST":
      s = Store(name=request.form.get('store_name'))
      if s.save():
         flash(f"Store name {request.form['store_name']} successfully saved.")
         return redirect(url_for('new_store'))
   else:
      return render_template('add-store.html', name=request.form['store_name'])

@app.route("/stores/")
def index_stores():
   store_list = Store.select().order_by(Store.id.asc())
   return render_template('stores.html', store_list=store_list)

@app.route("/stores/<store_id>/destroy", methods=['POST'])
def destroy_store(store_id):
   store_list = Store.select()

   if request.method == "POST":
      store = Store.get_by_id(store_id)
      flash(f"Closed {store.name}.")
      store.delete_instance()
      return redirect(url_for('index_stores'))
   else:
      return render_template('stores.html', store_list=store_list)

@app.route("/store/<store_id>", methods=['GET'])
def edit_store(store_id):
   store = Store.get_by_id(store_id)
   return render_template('store.html', store=store)

@app.route("/store/<store_id>/edit", methods=['POST'])
def update_store(store_id):
   store = Store.get_by_id(store_id)

   if request.method == "POST":
      store.name = request.form.get('store_name')
      if store.save():
         flash(f"Updated store name to {store.name}.")
         return redirect(url_for('edit_store', store_id=store.id))
   else:
      return render_template('store.html', store=store)

@app.route("/warehouse/new")
def new_warehouse():
   store_list = Store.select()
   return render_template('warehouse.html', store_list=store_list)

@app.route("/warehouse/", methods=['POST'])
def create_warehouse():
   if request.method == "POST":
      store = Store.get_by_id(request.form['store_id'])
      w = Warehouse(location=request.form['warehouse_location'], store=store)
      if w.save():
         flash(f"{store.name} added a new warehouse at {request.form['warehouse_location']}.")
         return redirect(url_for('new_warehouse'))
   else:
      return render_template('warehouse.html', location=request.form['warehouse_location'])


if __name__ == '__main__':
   app.run()
