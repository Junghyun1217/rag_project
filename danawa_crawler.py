from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains 
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import random

# --- 다나와 스크래핑 설정 변수 (게이밍 노트북) ---
BASE_SEARCH_URL = "https://search.danawa.com/dsearch.php?query=게이밍 노트북"
MAX_PAGES = 5
MAX_REVIEWS = 200
MAX_REVIEWS_PER_PRODUCT = 20 

# 제품 목록 선택자
PRODUCT_LINK_SELECTOR = 'a.click_log_product_standard_title_' 

# 리뷰 텍스트 선택자
REVIEW_TEXT_SELECTOR = 'div.atc' 

# '더보기' 버튼 선택자
MORE_BUTTON_SELECTOR = 'button.btn_review_more'


# --- 1. 드라이버 초기화 함수 ---
def init_driver():
    options = webdriver.ChromeOptions()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# --- 2. 제품 목록 URL 수집 함수 (URL 고유성 확보) ---
def get_product_urls(driver, base_url, max_pages):
    urls = []
    print(">> 다나와 제품 상세 URL 수집 시작...")
    
    for page in range(1, max_pages + 1):
        # base_url 인자를 사용하여 URL 생성
        list_url = f"{base_url}&page={page}" 
        driver.get(list_url)
        time.sleep(random.uniform(1, 2))
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, PRODUCT_LINK_SELECTOR))
            )
            links = driver.find_elements(By.CSS_SELECTOR, PRODUCT_LINK_SELECTOR)
            for link in links:
                href = link.get_attribute('href')
                
                if href and '/info/?pcode=' in href:
                    pcode_index = href.find('pcode=')
                    if pcode_index != -1:
                        pcode_value = href[pcode_index + 6:].split('&')[0]
                        unique_url = f"https://prod.danawa.com/info/?pcode={pcode_value}"
                        urls.append(unique_url)
            
            print(f"페이지 {page}에서 {len(urls)}개 URL 수집 중...", end='\r')
            
        except Exception:
            break
            
    unique_urls = list(set(urls))
    print(f"\n>> 총 {len(unique_urls)}개의 고유 제품 URL 수집 완료.")
    # 🚨 수정 완료: 중복 제거된 unique_urls를 반환합니다.
    return unique_urls 

# --- 3. 동적 리뷰 추출 함수 (스크롤 동작 및 리뷰 탭 특정 클릭) ---
def extract_dynamic_reviews(driver, product_url):
    reviews = []
    
    try:
        driver.get(product_url)
        # 제품 제목 로딩 확인 (페이지 진입 확인)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h3.prod_tit'))
        )
        title = driver.find_element(By.CSS_SELECTOR, 'h3.prod_tit').text
        
        # 💡 추가: 제목 클리닝 로직
        if '\nVS검색하기\nVS검색 도움말' in title:
            title = title.replace('\nVS검색하기\nVS검색 도움말', '').strip()
        
        print(f"\n[제품] {title} 상세 페이지 진입 성공.")

        # 1. 스크롤 동작 추가: 리뷰 탭(드롭다운 바)이 나타나도록 화면을 내림
        driver.execute_script("window.scrollBy(0, 800);") 
        print(f" 	✅ 1. 800px 스크롤 성공. 드롭다운 리뷰 탭 활성화 시도.")
        time.sleep(2) 
        
        # 2-1. '의견/리뷰' 탭 클릭 (1단계: 탭 활성화)
        review_tab_xpath = "//h3[@class='tab_txt' and text()='의견/리뷰']/parent::a"
        review_link = None
        try:
            review_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, review_tab_xpath))
            )
            ActionChains(driver).move_to_element(review_link).click().perform()
            print(f" 	✅ 2-1. '의견/리뷰' 탭 1차 Action 클릭 성공 (탭 활성화).")
            time.sleep(3) 
            
        except Exception:
            print(f" 	❌ 2-1. '의견/리뷰' 탭 클릭 실패! XPath '{review_tab_xpath}'를 찾거나 클릭할 수 없습니다.")
            return []

        # 2-2. '쇼핑몰 상품리뷰' 탭 클릭 (2단계: 리뷰 데이터 로드)
        SUB_REVIEW_TAB_XPATH = "//h4[@class='txt' and text()='쇼핑몰 상품리뷰']/parent::a"
        
        try:
            sub_review_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, SUB_REVIEW_TAB_XPATH))
            )
            ActionChains(driver).move_to_element(sub_review_link).click().perform()
            
            print(f" 	✅ 2-2. '쇼핑몰 상품리뷰' 탭 (XPath) Action 클릭 성공 (데이터 로드 시도).")
            time.sleep(3)
            
        except Exception:
            print(f" 	❌ 2-2. '쇼핑몰 상품리뷰' 탭 클릭 실패! XPath '{SUB_REVIEW_TAB_XPATH}'를 찾거나 클릭할 수 없습니다.")
            # 대체 로직 (Fallback)
            if review_link is not None:
                print(f" 	 	💡 대안: '의견/리뷰' 탭을 한 번 더 눌러 데이터 로드를 강제 시도합니다.")
                try:
                    ActionChains(driver).move_to_element(review_link).click().perform()
                    print(f" 	 	✅ 대안 성공: '의견/리뷰' 탭 재클릭 성공.")
                    time.sleep(3)
                except Exception:
                    print(f" 	 	❌ 대안 실패: '의견/리뷰' 탭 재클릭도 실패.")
                    return []
            else:
                return []


        # 3. 리뷰 텍스트가 실제로 나타날 때까지 대기
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, REVIEW_TEXT_SELECTOR))
            )
            print(f" 	✅ 3. 리뷰 콘텐츠 로딩 성공. 선택자: '{REVIEW_TEXT_SELECTOR}'")
            time.sleep(2)
        except:
            print(f" 	❌ 3. 리뷰 콘텐츠 로딩 실패! 선택자 '{REVIEW_TEXT_SELECTOR}'에 해당하는 요소가 나타나지 않습니다. (선택자 오류)")
            return []

        # 4. '더보기' 버튼 반복 클릭 로직
        count = 0
        while len(reviews) < MAX_REVIEWS_PER_PRODUCT:
            current_elements = driver.find_elements(By.CSS_SELECTOR, REVIEW_TEXT_SELECTOR)
            if len(current_elements) >= MAX_REVIEWS_PER_PRODUCT:
                 break 
            
            try:
                more_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, MORE_BUTTON_SELECTOR))
                )
                ActionChains(driver).move_to_element(more_button).click().perform()
                count += 1
                time.sleep(1.5) 
            except:
                break 

        print(f" 	✅ 4. '더보기' 버튼 {count}회 Action 클릭 완료.")

        # 5. 모든 로딩된 리뷰 텍스트 추출 및 제한 적용
        review_elements = driver.find_elements(By.CSS_SELECTOR, REVIEW_TEXT_SELECTOR)
        
        for el in review_elements:
            text = el.text.strip()
            if len(text) > 10 and len(reviews) < MAX_REVIEWS_PER_PRODUCT:
                reviews.append({"title": title, "text": text})

        print(f" 	✅ 5. 최종 {len(reviews)}건의 리뷰 추출 성공 (제한: {MAX_REVIEWS_PER_PRODUCT}건).")

    except Exception:
        pass
        
    return reviews

# --- 4. 전체 크롤링 실행 및 파일 저장 ---
if __name__ == "__main__":
    driver = init_driver()
    target_urls = get_product_urls(driver, BASE_SEARCH_URL, MAX_PAGES)
    
    all_reviews = []
    
    print(f"\n총 {len(target_urls)}개 제품 URL 기반으로 리뷰 {MAX_REVIEWS}건 수집 목표 (제품당 최대 {MAX_REVIEWS_PER_PRODUCT}건).")
    
    if len(target_urls) > 0:
        for url in target_urls:
            reviews = extract_dynamic_reviews(driver, url)
            all_reviews.extend(reviews)
            
            print(f"최종 수집된 리뷰: {len(all_reviews)}건", end='\r')
            
            if len(all_reviews) >= MAX_REVIEWS:
                print(f"\n>> 목표 {MAX_REVIEWS}건 달성! 크롤링 중단.")
                break
            time.sleep(random.uniform(1, 2)) 
    
    driver.quit()
    
    if all_reviews:
        with open('documents.json', 'w', encoding='utf-8') as f:
            json.dump(all_reviews, f, ensure_ascii=False, indent=4) 
        print(f"\n✅ 'documents.json' 파일 저장 완료. 총 {len(all_reviews)}건 수집.")
    else:
        print("\n❌ 리뷰 수집에 최종 실패했습니다. 리뷰 텍스트/더보기 버튼 선택자 확인이 필요합니다.")