from catalog.icat.facade import Catalog
client = Catalog()
output = client.get_run_number_and_title('NOM', 'IPTS-17210')
print(output)
