import pywikibot
from pywikibot.data import api
from pywikibot import pagegenerators as pg

wikipedia_site = pywikibot.Site("en", "wikipedia")
site = pywikibot.Site("wikidata", "wikidata")
site.useragent = "BjoeBot/1.0 (bjorn60@gmail.com)"

repo = site.data_repository()

# list of page names to search for, gathered from https://en.wikipedia.org/wiki/Template:Location_map/List
with open('wikidata\\Location map list.txt', mode='r', encoding='UTF-8') as f: # Here: Update txt from https://en.wikipedia.org/wiki/Template:Location_map/List
    page_names = f.read().splitlines()
page_names = ['Module:Location map/data/' + n for n in page_names if not '← ' in n]

prop_id = "P31" # instance of
prop_val = "Q18711811" # map data module
prop_val_parent = "Q15184295" # Wikimedia module

src_id = "P143" # imported from Wikimedia project
src_val = "Q328" # English Wikipedia

desc_dict = {"en": "Wikimedia module"}

def wikiitemsearch(label):
    params = {'action': 'wbsearchentities', 'format': 'json',
              'language': 'en', 'type': 'item',
              'search': label}
    request = api.Request(site=site, parameters=params)
    result = request.submit()['search']
    if result:
        if len(result) > 1:
            for r in result:
                if r['label'] == label:
                    return r['id']
        else:
            return result[0]['id']
    return None

def create_item(site, label_dict):
    new_item = pywikibot.ItemPage(site)
    new_item.editLabels(labels=label_dict)
    new_item.editDescriptions(desc_dict)
    return new_item.getID()

# Handles all the pages in the list from wikipedia and adds them if they don't exists, adds "map data module" if it is not added
def process_page_names():
    for idx, page_name in enumerate(page_names[2870:]):
        if idx % 10 == 0:
            print(idx)
        item_id = wikiitemsearch(page_name)

        new_claim = pywikibot.Claim(repo, prop_id)
        claim_target = pywikibot.ItemPage(repo, prop_val)
        new_claim.setTarget(claim_target)

        src_claim = pywikibot.Claim(repo, src_id)
        src_target = pywikibot.ItemPage(repo, src_val)
        src_claim.setTarget(src_target)
        new_claim.addSource(src_claim)

        if item_id:
            item = pywikibot.ItemPage(repo, item_id)
            item_dict = item.get()
            claim_dict = item_dict["claims"]


            if not prop_id in claim_dict:
                #print(f"Adding prop to: {page_name}")
                item.addClaim(new_claim)
            else:
                claim_list = claim_dict[prop_id]
                val_found = False
                parent_claim = None # If parent claim is found this is changed to sub claim instead of adding a new claim
                for claim in claim_list:
                    target = claim.getTarget()
                    if target.id == prop_val:
                        val_found = True
                        break
                    elif target.id == prop_val_parent:
                        parent_claim = claim
                if val_found:
                    #print(f"{page_name} is already ok")
                    continue
                if parent_claim:
                    #print(f"Changing: {page_name}")
                    parent_claim.changeTarget(claim_target, summary="Wikimedia module > map data module")
                    if not parent_claim.sources:
                        parent_claim.addSource(src_claim)
                else:
                    #print(f"Adding prop to: {page_name}")
                    item.addClaim(new_claim)

        else:
            test_page = pywikibot.Page(wikipedia_site, page_name)
            try:
                test_item = pywikibot.ItemPage.fromPage(test_page)
            except:
                print(f"Adding: {page_name}")
                labels = {"en": page_name}
                new_item_id = create_item(site, labels)
                new_item = pywikibot.ItemPage(repo, new_item_id)
                new_item.addClaim(new_claim)
                sitedict = {'site':'enwiki', 'title':page_name}
                new_item.setSitelink(sitedict)
            else:
                new_labels = {"en": page_name}
                test_item.editLabels(labels=new_labels)
                print(f"*** {test_item.id} > {page_name}")


# Checks all "Wikimedia module" beginning with "Module:Location map/data/" and changes to the sub class "map data module"
def process_parent_prop():
    wdq = 'SELECT DISTINCT ?item WHERE {?item wdt:P31 wd:Q15184295 . ?item rdfs:label ?itemLabel . FILTER NOT EXISTS { ?item wdt:P31 wd:Q18711811 . } FILTER (lang(?itemLabel) = "en") FILTER REGEX(STR(?itemLabel), "^Module:Location map/data/")}'
    generator = pg.WikidataSPARQLPageGenerator(wdq, site=site)
    for idx, page in enumerate(generator):
        if idx % 10 == 0:
            print(idx)
        item_dict = page.get()
        claim_list = item_dict["claims"][prop_id]

        for claim in claim_list:
            trgt = claim.getTarget()
            if trgt.id == prop_val_parent:
                print(f"Changing: {page} {page.id}")
                claim_target = pywikibot.ItemPage(repo, prop_val)
                claim.changeTarget(claim_target, summary="Wikimedia module > map data module")
                break



if __name__ == "__main__":
    # process_page_names()
    process_parent_prop()