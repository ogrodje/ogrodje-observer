# Ogrodje Observer

We observe the world of tech / dev in Slovenia w/ this.

## Collection and tools

Make sure you get API keys from `@otobrglez` then you can run:

```bash
./bin/observer-dev.sh up pg kafka kafdrop

# Schedule collection
python -m scrapers.start_collection

# If u have multiple partitions enable u can have multiple collectors
nodemon -w scrapers -e py --exec "python -m scrapers.collector"

# Persistors will persist collected items in the database
nodemon -w scrapers -e py --exec "python -m scrapers.persistor"

# Django for actual API service
python manage.py migrate
python manage.py runserver
```

P.s.: Your live will be easier if you use [devenv](https://devenv.sh/) with this project.

## Authors

- [Oto Brglez](https://github.com/otobrglez)

