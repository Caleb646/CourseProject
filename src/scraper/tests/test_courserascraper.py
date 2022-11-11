import scrapers.coursera as c  

# invalid urls contain the words quiz, exam, #tag_name, and don't contain www.coursera.org and cs-410
invalid_urls = [
    "https://www.coursera.org/learn/cs-410/exam/E81Mz/orientation-quiz", 
    "https://www.coursera.org/learn/cs-410/quiz/bAk3a/week-3-practice-quiz", 
    "https://www.coursera.org/learn/cs-410/home/week/15#main", 
    "https://www.coursera.org/learn/cs-410/exam/PaNAP/week-8-quiz", 
    "https://www.coursera.org/learn/cs-410/lecture/7hOfP/12-8-summary-for-exam-2", 
    "https://www.coursera.org/learn/cs-410/exam/S0Bpp/week-11-quiz", 
    "https://www.coursera.org/learn/cs-410/quiz/GYBV8/pre-quiz", 
    "https://www.coursera.org/learn/cs-410/home/week/10#main", 
    "https://www.coursera.org/learn/cs-410/home/week/5#main", 
    "https://www.coursera.org/learn/cs-410/quiz/CTsPR/week-6-practice-quiz",
    "https://www.coursera.org/learn/cs-410/home/week/11#main", 
    "https://www.coursera.org/my-purchases", 
    "https://www.coursera.org/learn/cs-410/supplement/dE9Wb/how-to-use-proctoru-for-exams", 
    "https://www.coursera.org/"
    ]

valid_urls = [
    "https://www.coursera.org/learn/cs-410/E81Mz/", 
    "https://www.coursera.org/learn/cs-410/bAk3a/week-3", 
    "https://www.coursera.org/learn/cs-410/home/week/15", 
    "https://www.coursera.org/learn/cs-410/PaNAP/week-8-", 
    "https://www.coursera.org/learn/cs-410/lecture/7hOfP/12-8-summary-for--2", 
    "https://www.coursera.org/learn/cs-410/S0Bpp/week-11-", 
    "https://www.coursera.org/learn/cs-410/GYBV8/pre-", 
    "https://www.coursera.org/learn/cs-410/home/week/10main", 
    "https://www.coursera.org/learn/cs-410/home/week/5main", 
    "https://www.coursera.org/learn/cs-410/CTsPR/week-6-practice-",
    "https://www.coursera.org/learn/cs-410/home/week/11main", 
    "https://www.coursera.org/learn/cs-410/supplement/dE9Wb/how-to-use-proctoru-for-s", 
    ]

def test_scraper_url_rules(scraper, urls):
    res = []
    for url in urls:
        url, valid = scraper._process_url(url)
        if valid:
            res.append(url)
    return res

def main():
    scraper = c.CouseraScraper("", "", "")
    processed_urls = test_scraper_url_rules(scraper, invalid_urls)
    assert not processed_urls, "Processed Urls should be empty not [{}]".format(processed_urls)
    processed_urls = test_scraper_url_rules(scraper, valid_urls)
    assert processed_urls, "Processed Urls should not be empty [{}]".format(processed_urls)

    print("All Tests for CourseraScraper Class Passed Successfully.")

if __name__ == "__main__":
    main()
