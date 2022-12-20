import pywikibot
from pywikibot.data import api

wikipedia_site = pywikibot.Site("en", "wikipedia")
site = pywikibot.Site("wikidata", "wikidata")
site.useragent = "BjoeBot/1.0 (bjorn60@gmail.com)"

repo = site.data_repository()

# list of page names to search for, gathered from https://en.wikipedia.org/wiki/Template:Location_map/List
with open('wikidata\\Location map list.txt', mode='r', encoding='UTF-8') as f: # Here: Update txt from https://en.wikipedia.org/wiki/Template:Location_map/List
    page_names = f.read().splitlines()
page_names = ['Module:Location map/data/' + n for n in page_names if not '← ' in n]
page_names = page_names[:50] # For testing

prop_id = "P31" # instance of
prop_val = "Q18711811" # map data module
prop_val_parent = "Q15184295" # Wikimedia module

src_id = "P143" # imported from Wikimedia project
src_val = "Q328" # English Wikipedia

new_claim = pywikibot.Claim(repo, prop_id)
claim_target = pywikibot.ItemPage(repo, prop_val)
new_claim.setTarget(claim_target)

src_claim = pywikibot.Claim(repo, src_id)
src_target = pywikibot.ItemPage(repo, src_val)
src_claim.setTarget(src_target)


def wikiitemsearch(label):
    params = {'action': 'wbsearchentities', 'format': 'json',
              'language': 'en', 'type': 'item',
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

def create_item(site, label_dict):
    new_item = pywikibot.ItemPage(site)
    new_item.editLabels(labels=label_dict)
    return new_item.getID()


for page_name in page_names:
    item_id = wikiitemsearch(page_name)
    if item_id:
        item = pywikibot.ItemPage(repo, item_id)
        item_dict = item.get()
        claim_dict = item_dict["claims"]
        if not prop_id in claim_dict:
            print(f"Adding prop to {page_name}")
            item.addClaim(new_claim)
        else:
            claim_list = claim_dict[prop_id]
            val_found = False
            val_parent_found = False
            for claim in claim_list:
                target = claim.getTarget()
                if target.id == prop_val:
                    val_found = True
                    break
                elif target.id == prop_val_parent:
                    val_parent_found = True
            if val_found:
                print(f"{page_name} is already ok")
                continue
            if val_parent_found:
                print(f"Changing {page_name} to sub prop")
                claim.changeTarget(claim_target, summary="Wikimedia module > map data module")
                #claim.addSource(src_claim)
            else:
                print(f"Adding prop to {page_name}")
                item.addClaim(new_claim)
                #new_claim.addSource(src_claim)

    else:
        test_page = pywikibot.Page(wikipedia_site, page_name)
        if test_page.exists():
            test_item = pywikibot.ItemPage.fromPage(test_page)
            print(f"'{page_name}' exists with the id '{test_item.id}'")
        else:
            print(f"{page_name} not found on Wikidata")
            # labels = {"en": page_name}
            # new_item_id = create_item(site, labels)
            # new_item = pywikibot.ItemPage(repo, new_item_id)
            # item.addClaim(new_claim)
            # # new_claim.addSource(src_claim)
            # sitedict = {'site':'enwiki', 'title':page_name}
            # new_item.setSitelink(sitedict)