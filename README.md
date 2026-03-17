# Proyek Analisis Data E-Commerce (Dicoding)

Dashboard ini dibuat untuk proyek Analisis Data Dicoding menggunakan E-Commerce Public Dataset (Olist).  
Fokus analisis:
1. Kategori produk dengan revenue tertinggi pada 2018 dan tren bulanannya.
2. Kota/wilayah dengan loyalitas customer (repeat order) dan pola aktivitasnya.

Insight ringkas:
1. health_beauty menjadi kategori dengan kontribusi revenue tertinggi dan tren paling kuat.
2. Revenue terkonsentrasi pada beberapa kategori utama (market concentration).
3. Sao Paulo menjadi kontributor revenue terbesar, namun ada risiko ketergantungan pada sedikit wilayah.
4. Mayoritas pelanggan masih one-time buyer, sehingga retensi adalah peluang utama.

## Struktur Proyek
submission/
├── dashboard/
│   ├── dashboard.py
│   └── main_data.csv
├── data/E-Commerce Public Dataset/
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb
├── requirements.txt
└── README.md

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard/dashboard.py
```