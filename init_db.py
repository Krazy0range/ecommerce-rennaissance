from database import Database


def main():

    products_db_path = "database/products.csv"
    urls_db_path = "database/urls.csv"

    products_db = Database(products_db_path)
    urls_db = Database(urls_db_path)

    products_db.headers = ["name", "price", "url", "timestamp"]
    urls_db.headers = ["url", "references", "timestamp"]

    products_db.write_data()
    urls_db.write_data()


if __name__ == "__main__":
    main()
