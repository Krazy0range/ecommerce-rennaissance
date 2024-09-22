from database import Database


def main():

    products_db_path = "database/products.csv"
    urls_db_path = "database/urls.csv"
    backup_products_db_path = "database_backups/backup_products.csv"
    backup_urls_db_path = "database_backups/backup_urls.csv"

    products_db = Database(products_db_path)
    urls_db = Database(urls_db_path)
    backup_products_db = Database(backup_products_db_path)
    backup_urls_db = Database(backup_urls_db_path)

    products_db.read_data()
    urls_db.read_data()

    backup_products_db.copy_db(products_db)
    backup_urls_db.copy_db(urls_db)

    backup_products_db.write_data()
    backup_urls_db.write_data()


if __name__ == "__main__":
    main()
