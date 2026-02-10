## email: won.sang.l@gmail.com



    if isinstance(x, str):
        return x.encode("utf-8", "ignore").decode("utf-8")
    return x

df = df.applymap(to_utf8)
