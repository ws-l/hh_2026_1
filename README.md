## email: won.sang.l@gmail.com



engine = create_engine(
    "postgresql+psycopg2://user:pw@host:5432/dbname",
    connect_args={"options": "-c client_encoding=utf8"}
)
