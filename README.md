## email: won.sang.l@gmail.com



engine = create_engine(
    "postgresql+psycopg2://user:pw@host:5432/dbname",
    connect_args={"options": "-c client_encoding=utf8"}
)


def to_utf8(x):
    if isinstance(x, str):
        return x.encode("utf-8", "ignore").decode("utf-8")
    return x

df = df.applymap(to_utf8)
