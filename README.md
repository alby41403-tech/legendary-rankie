# legendary-rankie
nursing ranklist scrapped and rearranged according to index Mark for easy finding
# 🩺 Nursing Rank List

## 💡 About the Project (The Student Story)
As a nursing student going through admissions, waiting for the official rank list announcement is incredibly stressful. The official portals can be slow, messy, and difficult to search through quickly. Sorting through thousands of candidates manually or trying to compute index marks out of 300 based on Physics, Chemistry, and Biology scores takes days of exhausting effort. I built this tool because I wanted an instant, lightning-fast way to parse, clean, and rank student admissions data immediately, saving countless hours of anxiety for students checking their standing.
How I Developed It:
 * Data Acquisition: I used Bright Data Scraper Studio to efficiently scrape and extract the raw, unstructured nursing rank list data from the web pages. Bright Data handled the heavy lifting of navigating the complex layouts and structuring the raw text into a clean dataset.
 * Data Processing Pipeline: I imported the extracted data into a Python environment using Pandas. The script normalizes messy grade records, calculates accurate index marks out of 300, and sorts candidates instantly.
 * User Experience & Deployment: I built a clean, mobile-responsive web app using Streamlit. It features instant application-number searching, side-by-side category views, and automated visual highlights for pending statuses so users can check their exact standing in seconds.



---

## ✨ Features
* **Instant Application Search:** Quickly look up your exact standing by entering your application number.
* **Smart Categorization:** Easily switch between Accepted/Pending lists and Rejected lists.
* **Status Highlighting:** Entire rows are highlighted in a soft red background for applicants whose status is currently Pending.
* **Fully Responsive:** Designed for seamless use on both laptops and mobile phones.

---

## 🤖 AI Assistance Disclosure
As I made this project, I utilized AI coding assistant Google Gemini to help draft and refine the Python/Streamlit layout code, style the custom CSS for mobile responsiveness, and organize the documentation. All architectural decisions, data verification, testing, and implementation choices were made by me 



