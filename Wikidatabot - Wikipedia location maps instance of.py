import pywikibot

site = pywikibot.Site("wikidata", "wikidata")
site.set_maxlag(5)
site.useragent = "BjoeBot/1.0 (bjorn60@gmail.com)"

repo = site.data_repository()

page_names = [] # list of page names to search for, gathered from https://en.wikipedia.org/wiki/Template:Location_map/List
property_id = "P31" # instance of
item_id = "Q18711811" # map data module

for page_name in page_names:
    page = pywikibot.Page(site, page_name)
    if page.exists():
        item = pywikibot.ItemPage.fromPage(page).get()
        claims = item.get('claims')
        if property_id not in claims:
            new_claim = pywikibot.Claim(repo, property_id)
            new_claim.setTarget(pywikibot.ItemPage(repo, item_id))
            item.addClaim(new_claim)
            print(f"Added Property:P31 of Q18711811 to {page_name}")
        else:
            print(f"{page_name} already has Property:P31")
    else:
        print(f"{page_name} not found on Wikidata")
