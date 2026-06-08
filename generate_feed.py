import urllib.request
import json
import csv
import re
import html

# Fetch products from Shopify
url = "https://stillrisingco.com/collections/all/products.json?limit=250"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
except Exception as e:
    print(f"Error fetching products: {e}")
    exit(1)

products = data.get("products", [])
if not products:
    print("No products found.")
    exit(1)

def clean_html(raw_html):
    if not raw_html: return ""
    clean_text = re.sub(r'<[^>]+>', ' ', raw_html)
    clean_text = html.unescape(clean_text)
    return ' '.join(clean_text.split())

pinterest_rows = []
for product in products:
    desc = clean_html(product.get("body_html", ""))
    vendor = product.get("vendor", "")
    p_type = product.get("product_type", "")
    p_id = product.get("id", "")
    handle = product.get("handle", "")
    images = product.get("images", [])
    first_image = images[0].get("src", "") if images else ""

    for variant in product.get("variants", []):
        variant_id = variant.get("id")
        v_title = variant.get("title", "")
        title = product.get("title", "")
        if v_title and v_title != "Default Title":
            title = f"{title} - {v_title}"
            
        featured_image = variant.get("featured_image")
        image_url = featured_image.get("src") if featured_image else first_image
        
        price_val = float(variant.get("price", 0))
        compare_val = variant.get("compare_at_price")
        base_price = f"{price_val:.2f} USD"
        sale_price = ""
        
        if compare_val:
            try:
                compare_float = float(compare_val)
                if compare_float > price_val:
                    base_price = f"{compare_float:.2f} USD"
                    sale_price = f"{price_val:.2f} USD"
            except ValueError:
                pass
                
        available = variant.get("available", False)
        availability = "in stock" if available else "out of stock"
        link = f"https://stillrisingco.com/products/{handle}?variant={variant_id}"
        
        row = {
            "id": variant_id, "title": title, "description": desc, "link": link,
            "image_link": image_url, "price": base_price, "sale_price": sale_price,
            "availability": availability, "brand": vendor, "condition": "new",
            "product_type": p_type, "item_group_id": p_id, "mpn": variant.get("sku", "")
        }
        pinterest_rows.append(row)

headers = ["id", "title", "description", "link", "image_link", "price", "sale_price", "availability", "brand", "condition", "product_type", "item_group_id", "mpn"]
with open("pinterest_catalog.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(pinterest_rows)
print(f"Successfully generated feed.")
