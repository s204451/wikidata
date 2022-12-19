import pywikibot
from pywikibot.data import api

site = pywikibot.Site("test", "wikidata")
site.useragent = "BjoeBot/1.0 (bjorn60@gmail.com)"

repo = site.data_repository()

page_names = ["Sandbox"] # list of page names to search for, gathered from https://en.wikipedia.org/wiki/Template:Location_map/List
prop_id = "P31" # instance of
prop_id = "P81" # soblop of
prop_val = "Q18711811" # map data module
prop_val = "Q1001" # test

src_id = "P143" # imported from Wikimedia project
src_id = "P143" # imported from Wikimedia project
src_val = "Q328" # English Wikipedia
src_val = "Q213573" # English Wikipedia

def wikiitemsearch(label):
    params = {'action': 'wbsearchentities', 'format': 'json',
              'language': 'en', 'type': 'item', 'limit':1,
              'search': label}
    request = api.Request(site=site, parameters=params)
    result = request.submit()['search']
    if result:
        if len(result) > 1:
            print(f"{len(result)} results for '{label}':")
            print(result)
        else:
            return result[0]['id']
    return None


for page_name in page_names:
    item_id = wikiitemsearch(page_name)
    if item_id:
        item = pywikibot.ItemPage(repo, item_id)
        item_dict = item.get()
        clm_list = item_dict["claims"][prop_id]
        val_found = False
        for clm in clm_list:
            trgt = clm.getTarget()
            print(trgt.id, prop_val)
            if trgt.id == prop_val:
                val_found = True
                break
        if not val_found:
            new_clm = pywikibot.Claim(repo, prop_id)
            trgt = pywikibot.ItemPage(repo, prop_val)
            new_clm.setTarget(trgt)
            item.addClaim(new_clm)

            src_clm = pywikibot.Claim(repo, src_id)
            src_trgt = pywikibot.ItemPage(repo, src_val)
            src_clm.setTarget(src_trgt) #Inserting value
            new_clm.addSource(src_clm)

    else:
        print(f"{page_name} not found on Wikidata")
