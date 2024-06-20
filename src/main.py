from crawler import fetch_leakbase_data, fetch_lockbit_data, fetch_blacksuit_data

if __name__ == '__main__':
    fetch_leakbase_data()
    fetch_lockbit_data()
    fetch_blacksuit_data()
    print('Crawling finished.')
