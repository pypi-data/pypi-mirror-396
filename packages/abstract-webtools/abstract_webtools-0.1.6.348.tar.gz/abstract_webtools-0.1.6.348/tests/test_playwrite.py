from imports import *
from pagination import *
url =   (            "http://www.cohtora.houstontx.gov/ibi_apps/WFServlet.ibfs?"
            "IBIAPP_app=soldpermits&IBIF_ex=online_per_se&IBIC_server=EDASERVE&"
            "VALMN=10000&VALMX=1500000&SELTD=PT&PTYPE=11")
def main():
        plywrt_mgr = playwriteManager(url)
        print(f"plywrt_mgr == {plywrt_mgr}")
        page = plywrt_mgr.page


        # Get total pages ONCE
        total_pages = get_last_page_number(page=page)
        if not total_pages:
            print("Could not detect last page!")
            browser.close()
            return
        print(f"Detected {total_pages:,} total pages. Starting download...\n")

        current_page = 1

        while True:
            print(f"Scraping page {current_page:,} / {'.' * 30}")
            # Wait for table to load
            page.wait_for_selector("#ITableData0", timeout=10000)
            rows = page.query_selector_all("#ITableData0 tr")
            data_rows = []

            for row in rows:
                cells = row.query_selector_all("td")
                if len(cells) < 7:
                    continue
                texts = [cell.inner_text().strip() for cell in cells]
                if texts[0].isdigit():  # Real data rows start with permit number
                    data_rows.append(texts)

            # Save CSV
            filename = f"houston_sold_permits_page_{current_page:04d}.csv"
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Permit_Num", "Permit_Desc", "Owner_Occupant", "Address", "Project_Desc", "Valuation", "Permit_Type"])
                writer.writerows(data_rows)

            print(f"Saved {len(data_rows):,} records → {filename}")

            # Check if we're on last page
            if current_page >= total_pages:
                print(f"\nFINISHED! All {total_pages:,} pages downloaded perfectly.")
                break

            # Click "Next Page"
            next_click = get_click_value_string(page=page, attributes={"span": {"title": "Next Page"}})
            if not next_click:
                print("Next button not found!")
                break

            try:
                button = page.query_selector(f"span[onclick=\"{next_click}\"]")
                if not button or not button.is_visible():
                    print("Next button not visible!")
                    break
                button.click()
                page.wait_for_load_state("networkidle")
                time.sleep(1.5)  # Smooth & stable
                current_page += 1
            except Exception as e:
                print("Click failed:", e)
                break

        browser.close()

if __name__ == "__main__":
    main()

