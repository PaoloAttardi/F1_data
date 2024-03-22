import fastf1 as ff1

year, grand_prix, session = 2023, 'Bahrain', 'Race'
event = ff1.get_session(year,grand_prix,session)
event.load()
d = event.drivers
drivers = []
print(event.results.head())
print(event.results.columns)
result = event.results.values.tolist()